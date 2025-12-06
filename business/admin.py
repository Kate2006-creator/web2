from django.contrib import admin
from business.models import Favour, Project, Review, ProjectService

@admin.register(Favour)
class FavourAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['description', 'mark', 'pr']

@admin.register(ProjectService)
class ProjectServiceAdmin(admin.ModelAdmin):
    list_display = ['project', 'favour']



