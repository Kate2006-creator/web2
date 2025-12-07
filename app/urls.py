from django.contrib import admin
from django.urls import path, include

from business import views

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


from business.api import ProjectsViewset, FavoursViewset, ProjectServicesViewset, ReviewsViewset, UserProfilesViewset, UsersViewset, UsersLoginViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("projects", ProjectsViewset, basename="projects")
router.register("favours", FavoursViewset, basename="favours")
router.register("project_services", ProjectServicesViewset, basename="project_services")
router.register("reviews", ReviewsViewset, basename="reviews")
router.register("user_profiles", UserProfilesViewset, basename="user_profiles")
router.register("users", UsersViewset, basename="users") 
router.register("users_login", UsersLoginViewset, basename="users_login") 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
