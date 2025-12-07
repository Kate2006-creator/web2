from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets
from business.models import Project, Favour, Review, ProjectService
from general.models import UserProfile
from django.contrib.auth.models import User

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.contrib.auth import authenticate, login, logout

from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from business.serializers import ProjectSerializer, ProjectServiceSerializer, FavourSerializer, ReviewSerializer, UserProfileSerializer, UserSerializer

class ProjectsViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class FavoursViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = Favour.objects.all()
    serializer_class = FavourSerializer

class ProjectServicesViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = ProjectService.objects.all()
    serializer_class = ProjectServiceSerializer

class ReviewsViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class UserProfilesViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UsersLoginViewset(GenericViewSet):
    queryset = UserProfile.objects.all()

    @method_decorator(csrf_exempt, name='dispatch')
    @action(url_path="my", methods=["GET"], detail=False)
    def get_my(self, *args, **kwargs):
        return Response({
            'username': self.request.user.username,
            'is_authenticated': self.request.user.is_authenticated,
            'is_staff': self.request.user.is_staff,
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