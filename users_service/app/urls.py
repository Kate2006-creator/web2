from django.contrib import admin
from django.urls import path, include


from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from general.api import UserProfilesViewset, UsersViewset, UsersLoginViewset


router = DefaultRouter()

router.register("user_profiles", UserProfilesViewset, basename="user_profiles")
router.register("users", UsersViewset, basename="users") 
router.register("users_login", UsersLoginViewset, basename="users_login") 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)