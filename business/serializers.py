from rest_framework import serializers
from django.contrib.auth.models import User

from business.models import Project, Review, Favour, ProjectService
from general.models import UserProfile

class ProjectSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'status', 'client_user']

    def create(self, validated_data, *args, **kwargs):
        user = self.context['request'].user
        if not user.is_staff:
            validated_data['client_user'] = user

        print(validated_data )

        return super().create(validated_data)
    

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

# ВОТ С ЭТИМ РАЗОБРАТЬСЯ!!!!
    def create(self, validated_data):
        # Получаем пароль из данных
        password = validated_data.pop('password', None)
        
        # Создаем пользователя
        user = User.objects.create(**validated_data)
        
        # Устанавливаем и хэшируем пароль
        if password:
            user.set_password(password)
            user.save()
        
        return user
    
    def update(self, instance, validated_data):
        # Если в данных есть пароль - обновляем его
        password = validated_data.pop('password', None)
        
        if password:
            instance.set_password(password)
        
        # Обновляем остальные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance