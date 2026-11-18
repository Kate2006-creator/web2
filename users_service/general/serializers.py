from rest_framework import serializers
from django.contrib.auth.models import User

from general.models import UserProfile

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
    
