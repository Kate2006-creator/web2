from rest_framework import serializers


from business.models import Project, Review, Favour, ProjectService

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'status', 'client_user_id'] # Заменили client_user на client_user_id

    def create(self, validated_data, *args, **kwargs):
        user = self.context['request'].user
        # Так как client_user - это IntegerField, мы передаем ID пользователя
        if not user.is_staff:
            validated_data['client_user_id'] = user.id
        elif 'client_user_id' not in validated_data:
            # Если админ не указал ID, можно оставить null или поставить 1 (для теста)
            validated_data['client_user_id'] = 1 

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
    
    class Meta:
        model = ProjectService
        fields = ['id', 'project', 'favour', 'employee_user_id', 'notes', 'project_name', 'favour_name']