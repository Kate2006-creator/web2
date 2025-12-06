from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets
from business.models import Project, Favour, Review, ProjectService

from business.serializers import ProjectSerializer, ProjectServiceSerializer, FavourSerializer, ReviewSerializer

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