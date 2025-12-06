from rest_framework import serializers

from business.models import Project, Review, Favour, ProjectService

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'status', 'client_user']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id','description', 'mark', 'pr']

class FavourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favour
        fields = ['id', 'name', 'description', 'price']

class ProjectServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectService
        fields = ['id', 'project', 'favour', 'employee_user', 'notes']