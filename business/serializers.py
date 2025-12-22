from rest_framework import serializers
from django.contrib.auth.models import User

from business.models import Project, Review, Favour, ProjectService
from general.models import UserProfile

class ProjectSerializer(serializers.ModelSerializer):
    client_fio = serializers.CharField(source='client_user.profile.fio', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'status', 'client_user', 'client_fio']

    def create(self, validated_data, *args, **kwargs):
        user = self.context['request'].user
        if not user.is_staff:
            validated_data['client_user'] = user

        print(validated_data )

        return super().create(validated_data)
    

class ReviewSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='pr.name', read_only=True) 

    class Meta:
        model = Review 
        fields = ['id','description', 'mark', 'pr', 'picture','project_name']

class FavourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favour
        fields = ['id', 'name', 'description', 'price']

class ProjectServiceSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    favour_name = serializers.CharField(source='favour.name', read_only=True)
    employee_fio = serializers.CharField(source='employee_user.profile.fio', read_only=True)
    employee_position = serializers.CharField(source='employee_user.profile.position', read_only=True)
    
    class Meta:
        model = ProjectService
        fields = ['id', 'project', 'favour', 'employee_user', 'notes', 'project_name', 'favour_name', 'employee_fio', 'employee_position']

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

    def create(self, validated_data):
        # Получаем пароль из данных
        password = validated_data.pop('password', None)
        
        # Создаем пользователя
        user = User.objects.create(**validated_data)
        
        # Устанавливаем пароль
        if password:
            user.set_password(password)
            user.save()
        
        return user
    
