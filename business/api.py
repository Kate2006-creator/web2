from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets
from business.models import Project, Favour, Review, ProjectService
from general.models import UserProfile
from django.contrib.auth.models import User

from rest_framework import status

from django.db.models import Avg, Count, Max, Min, Q
from rest_framework.permissions import IsAuthenticated

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.contrib.auth import authenticate, login, logout

from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from business.serializers import ProjectSerializer, ProjectServiceSerializer, FavourSerializer, ReviewSerializer, UserProfileSerializer, UserSerializer
from business.word_exporter import WordExporter

class ProjectsViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = Project.objects.all()
        user = self.request.user
        
        # Если пользователь не админ, показываем только его проекты
        if not user.is_staff:
            queryset = queryset.filter(client_user=user)
        
        client_id = self.request.query_params.get('client_id', None)
        status = self.request.query_params.get('status', None)
        
        # Фильтруем по клиенту (только для админов)
        if user.is_staff and client_id:
            queryset = queryset.filter(client_user_id=client_id)
        
        # Фильтруем по статусу
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset



    class StatsSerializer(serializers.Serializer):
        total_count = serializers.IntegerField()
        by_status = serializers.DictField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):

        total_count = Project.objects.count()
        
        # проекты по статусам
        status_stats = Project.objects.values('status').annotate(
            count=Count('id')
        )
        
        # Преобразуем в словарь {статус: количество}
        by_status = {}
        for stat in status_stats:
            by_status[stat['status']] = stat['count']
        
        stats = {
            'total_count': total_count,
            'by_status': by_status
        }
        
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=["GET"], url_path="export_word")
    def export_to_word(self, request, *args, **kwargs):
    # Берем проекты как в get_queryset
        queryset = self.get_queryset().select_related('client_user') 
    
        doc = WordExporter.export_to_word(
            data=queryset,
            title="Список проектов",
            headers=["ID", "Название", "Описание", "Статус", "Клиент"],
            fields=["id", "name", "description", "status", "client_user"]
        )
    
        return WordExporter.create_http_response(doc, "проекты.docx")

    @action(detail=False, methods=['GET'], url_path='filter')
    def filter_projects(self, request):
        queryset = self.get_queryset()
        
        # Фильтр по клиенту
        client_id = request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(client_user_id=client_id)
        
        # Фильтр по статусу
        status = request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class FavoursViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = Favour.objects.all()
    serializer_class = FavourSerializer

    def get_queryset(self):
        queryset = Favour.objects.all()
        
        # Получаем параметры фильтрации из запроса
        price_sort = self.request.query_params.get('price_sort', None)
        alphabet_sort = self.request.query_params.get('alphabet_sort', None)
        
        # Применяем сортировку по цене
        if price_sort == 'asc':
            queryset = queryset.order_by('price')
        elif price_sort == 'desc':
            queryset = queryset.order_by('-price')
        
        # Применяем сортировку по алфавиту
        if alphabet_sort == 'asc':
            # Если уже есть сортировка по цене, добавляем вторую сортировку
            if price_sort:
                queryset = queryset.order_by('name', 'price' if price_sort == 'asc' else '-price')
            else:
                queryset = queryset.order_by('name')
        
        return queryset

    

    class StatsSerializer(serializers.Serializer):
        total_count = serializers.IntegerField()
        min_price = serializers.FloatField()
        max_price = serializers.FloatField()
        avg_price = serializers.FloatField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = Favour.objects.aggregate(
            total_count=Count("*"),
            min_price=Min("price"),
            max_price=Max("price"),
            avg_price=Avg("price"),
        )
        
        # Округляем avg_price до 2 знаков
        if stats['avg_price']:
            stats['avg_price'] = round(stats['avg_price'], 2)
        
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=["GET"], url_path="export_word")
    def export_to_word(self, request, *args, **kwargs):
        favours = Favour.objects.all()
        
        doc = WordExporter.export_to_word(
            data=favours,
            title="Список услуг",
            headers=["ID", "Название", "Описание", "Цена"],
            fields=["id", "name", "description", "price"]
        )

        return WordExporter.create_http_response(doc, "услуги.docx")

class ProjectServicesViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = ProjectService.objects.all()
    serializer_class = ProjectServiceSerializer

    def get_queryset(self):
        user = self.request.user
        
        if user.is_staff:
            queryset = ProjectService.objects.all()
            
            employee_user = self.request.query_params.get('employee_user', None)
            project = self.request.query_params.get('project', None)
            
            # Фильтруем по сотруднику
            if employee_user:
                queryset = queryset.filter(employee_user_id=employee_user)
            
            # Фильтруем по проекту
            if project:
                queryset = queryset.filter(project_id=project)
                
            return queryset
        else:
            # Клиент видит только услуги в СВОИХ проектах
            return ProjectService.objects.filter(project__client_user=user)

    @action(detail=False, methods=["GET"], url_path="export_word")
    def export_to_word(self, request, *args, **kwargs):
        queryset = self.get_queryset().select_related(
            'project', 'favour', 'employee_user'
        )

        doc = WordExporter.export_to_word(
            data=queryset,
            title="Список услуг в проектах",
            headers=["ID", "Проект", "Услуга", "Сотрудник", "Примечания"],
            fields=["id", "project", "favour", "employee_user", "notes"]
    )
        
        return WordExporter.create_http_response(doc, "услуги_в_проектах.docx")


class ReviewsViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.all()
        
        mark = self.request.query_params.get('mark', None)
        
        if mark and mark != 'all':
            queryset = queryset.filter(mark=int(mark))
        
        return queryset

    class StatsSerializer(serializers.Serializer):
        total_count = serializers.IntegerField()
        avg_mark = serializers.FloatField()
        marks_distribution = serializers.DictField()  # Добавляю распределение по оценкам
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = Review.objects.aggregate(
            total_count=Count("*"),
            avg_mark=Avg("mark"),
        )
        
        marks_stats = Review.objects.values('mark').annotate( #читает количество записей (Count('id'))
            count=Count('id')
        ).order_by('mark')
        
        marks_dict = {}
        for i in range(1, 6):
            marks_dict[str(i)] = 0 
        
        for stat in marks_stats:
            marks_dict[str(stat['mark'])] = stat['count']
        
        stats['marks_distribution'] = marks_dict
        
        serializer = self.StatsSerializer(instance=stats)
        return Response(serializer.data)
    

class UserProfilesViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    class StatsSerializer(serializers.Serializer):
        total_clients = serializers.IntegerField()
        total_employees = serializers.IntegerField()
        employees_by_position = serializers.DictField()  # только сотрудники по должностям
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        
        stats = UserProfile.objects.aggregate(
            total_clients=Count('id', filter=Q(user_type='client')),
            total_employees=Count('id', filter=Q(user_type='employee')),
        )
        
        employees_by_position = UserProfile.objects.filter( #С filter мы считаем только те записи, которые удовлетворяют условию
            user_type='employee',
            position__isnull=False
        ).exclude(position='').values('position').annotate(
            count=Count('id')
        ).order_by('position')
        
        # Преобразуем в словарь {должность: количество}
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


class UsersLoginViewset(GenericViewSet):
    queryset = UserProfile.objects.all()

    client_perms = [
        'can_create_projects',
        'can_see_ProjectServicesView',
    ]

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
            return Response({
                "status": "failed"
            }, status = 401)
        return Response()
    
    @action(url_path="logout", methods=["POST"], detail=False)
    def process_logout(self, *args, **kwargs):
        logout(self.request)
        return Response({
                "status": "success"
            })

class UsersViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

  #  разрешение только для staff
    permission_classes = [IsAuthenticated] 
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            return User.objects.filter(id=user.id)
        
        return User.objects.all()
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "Только администраторы могут создавать пользователей"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {"error": "Только администраторы могут удалять пользователей"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)