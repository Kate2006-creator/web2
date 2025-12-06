from django.contrib import admin
from django.urls import path, include

from business import views

from business.api import ProjectsViewset, FavoursViewset, ProjectServicesViewset, ReviewsViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("projects", ProjectsViewset, basename="projects")
router.register("favours", FavoursViewset, basename="favours")
router.register("projects_services", ProjectServicesViewset, basename="projects_services")
router.register("reviews", ReviewsViewset, basename="reviews")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
]
