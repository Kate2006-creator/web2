from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.http import JsonResponse

from business.models import Project, Review, Favour, ProjectService

class ShowProjectsView(View):
    def get(request, *args, **kwargs):
        projects = Project.objects.all()

        result = " "
        for p in projects:
            result += p.name + "<br>"
            return HttpResponse(result)
        
class ShowReviewsView(View):
    def get(request, *args, **kwargs):
        reviews = Review.objects.all()

        result = " "
        for r in reviews:
            result += r.name + "<br>"
        
            return HttpResponse(result)
        
class ShowFavoursView(View):
    def get(request, *args, **kwargs):
        favours = Favour.objects.all()

        result = " "
        for f in favours:
            result += f.name + "<br>"
        
            return HttpResponse(result)

class ShowProjectServicesView(View):
    def get(request, *args, **kwargs):
        project_services = ProjectService.objects.all()

        result = " "
        for ps in project_services:
            result += ps.name + "<br>"
        
            return HttpResponse(result)

