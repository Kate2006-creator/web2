from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from general.models import UserProfile
from django.contrib.auth.models import User
from rest_framework import status
from django.db.models import Count, Q
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from general.serializers import UserProfileSerializer, UserSerializer
from general.word_exporter import WordExporter

@method_decorator(csrf_exempt, name='dispatch')
class UserProfilesViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    class StatsSerializer(serializers.Serializer):
        total_clients = serializers.IntegerField()
        total_employees = serializers.IntegerField()
        employees_by_position = serializers.DictField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = UserProfile.objects.aggregate(
            total_clients=Count('id', filter=Q(user_type='client')),
            total_employees=Count('id', filter=Q(user_type='employee')),
        )
        employees_by_position = UserProfile.objects.filter(
            user_type='employee',
            position__isnull=False
        ).exclude(position='').values('position').annotate(
            count=Count('id')
        ).order_by('position')
        
        positions_dict = {}
        for stat in employees_by_position:
            positions_dict[stat['position']] = stat['count']
        
        stats['employees_by_position'] = positions_dict
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=["GET"], url_path="export_employees_word")
    def export_employees_to_word(self, request, *args, **kwargs):
        employees = UserProfile.objects.filter(user_type='employee').select_related('user')
        doc = WordExporter.export_to_word(
            data=employees,
            title="Список сотрудников",
            headers=["ID", "ФИО", "Должность", "Дата рождения", "Email"],
            fields=["id", "fio", "position", "birthday", "user__email"]
        )
        return WordExporter.create_http_response(doc, "сотрудники.docx")
    
    @action(detail=False, methods=["GET"], url_path="export_clients_word")
    def export_clients_to_word(self, request, *args, **kwargs):
        clients = UserProfile.objects.filter(user_type='client').select_related('user')
        doc = WordExporter.export_to_word(
            data=clients,
            title="Список клиентов",
            headers=["ID", "ФИО", "Компания", "Дата рождения", "Email"],
            fields=["id", "fio", "company_name", "birthday", "user__email"]
        )
        return WordExporter.create_http_response(doc, "клиенты.docx")

@method_decorator(csrf_exempt, name='dispatch')
class UsersLoginViewset(GenericViewSet):
    queryset = UserProfile.objects.all()

    @method_decorator(csrf_exempt, name='dispatch')
    @action(url_path="my", methods=["GET"], detail=False)
    def get_my(self, *args, **kwargs):
        permissions = self.request.user.get_all_permissions()
        return Response({
            'username': self.request.user.username,
            'is_authenticated': self.request.user.is_authenticated,
            'is_staff': self.request.user.is_staff,
            'can_create_projects' :  self.request.user.has_perm('general.can_create_projects'),
            'permissions': permissions ,
        })
    
    @action(url_path="entrance", methods=["POST"], detail=False)
    def process_login(self, *args, **kwargs):
        class LoginSerializer(serializers.Serializer):
            username = serializers.CharField()
            password = serializers.CharField()

        serializer = LoginSerializer(data=self.request.data)
        serializer.is_valid(raise_exception = True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if user:
            login(self.request, user)
        else:
            return Response({"status": "failed"}, status = 401)
        return Response()
    
    @action(url_path="logout", methods=["POST"], detail=False)
    def process_logout(self, *args, **kwargs):
        logout(self.request)
        return Response({"status": "success"})

@method_decorator(csrf_exempt, name='dispatch')
class UsersViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [] 
    
    def get_queryset(self):
        return User.objects.all()
    