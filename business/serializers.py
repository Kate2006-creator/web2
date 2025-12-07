from rest_framework import serializers
from django.contrib.auth.models import User

from business.models import Project, Review, Favour, ProjectService
from general.models import UserProfile

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'status', 'client_user']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review 
        fields = ['id','description', 'mark', 'pr', 'picture']

class FavourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favour
        fields = ['id', 'name', 'description', 'price']

class ProjectServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectService
        fields = ['id', 'project', 'favour', 'employee_user', 'notes']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_type', 'fio', 
            'birthday', 'picture', 'company_name', 
            'position']
        
class UserSerializer(serializers.ModelSerializer):    
    class Meta:
        model = User
        fields = ['id', 'username', 'password','email', 'first_name', 'last_name']