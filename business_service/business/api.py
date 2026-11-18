from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from business.models import Project, Favour, Review, ProjectService

from rest_framework import status

from django.db.models import Avg, Count, Max, Min, Q
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from business.serializers import ProjectSerializer, ProjectServiceSerializer, FavourSerializer, ReviewSerializer
from business.word_exporter import WordExporter

class ProjectsViewset(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = Project.objects.all()
        user = self.request.user

        if not user.is_staff:
            queryset = queryset.filter(client_user_id=user.id) # ИСПРАВЛЕНО: client_user -> client_user_id
        
        client_id = self.request.query_params.get('client_id', None)
        status_filter = self.request.query_params.get('status', None) # Переименовал переменную, чтобы не перекрывать импорт status
        
        # Фильтруем по клиенту (только для админов)
        if user.is_staff and client_id:
            queryset = queryset.filter(client_user_id=client_id)
        
        # Фильтруем по статусу
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    class StatsSerializer(serializers.Serializer):
        total_count = serializers.IntegerField()
        by_status = serializers.DictField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        total_count = Project.objects.count()
        status_stats = Project.objects.values('status').annotate(
            count=Count('id')
        )
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
        queryset = self.get_queryset()
        # Убрал select_related('client_user'), так как это больше не ForeignKey
        doc = WordExporter.export_to_word(
            data=queryset,
            title="Список проектов",
            headers=["ID", "Название", "Описание", "Статус", "ID Клиента"],
            fields=["id", "name", "description", "status", "client_user_id"] # ИСПРАВЛЕНО
        )
        return WordExporter.create_http_response(doc, "проекты.docx")

    @action(detail=False, methods=['GET'], url_path='filter')
    def filter_projects(self, request):
        queryset = self.get_queryset()
        client_id = request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(client_user_id=client_id)
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
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
            
            if employee_user:
                queryset = queryset.filter(employee_user_id=employee_user) # ИСПРАВЛЕНО
            
            if project:
                queryset = queryset.filter(project_id=project)
            return queryset
        else:
            # Клиент видит только услуги в СВОИХ проектах
            return ProjectService.objects.filter(project__client_user_id=user.id) # ИСПРАВЛЕНО

    @action(detail=False, methods=["GET"], url_path="export_word")
    def export_to_word(self, request, *args, **kwargs):
        queryset = self.get_queryset().select_related('project', 'favour')
        # Убрал employee_user из select_related
        doc = WordExporter.export_to_word(
            data=queryset,
            title="Список услуг в проектах",
            headers=["ID", "Проект", "Услуга", "ID Сотрудника", "Примечания"],
            fields=["id", "project", "favour", "employee_user_id", "notes"] # ИСПРАВЛЕНО
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
        marks_distribution = serializers.DictField()
    
    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        stats = Review.objects.aggregate(
            total_count=Count("*"),
            avg_mark=Avg("mark"),
        )
        marks_stats = Review.objects.values('mark').annotate(
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
    

