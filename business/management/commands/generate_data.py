from django.core.management.base import BaseCommand
from faker import Faker
from django.db import transaction
from django.contrib.auth.models import User
import random

from general.models import UserProfile
from business.models import Favour, Project, Review, ProjectService

class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        
        ProjectService.objects.all().delete()
        Review.objects.all().delete()
        Project.objects.all().delete()
        Favour.objects.all().delete()
        UserProfile.objects.all().delete()
        
        # Удаляем только тестовых пользователей, не всех
        User.objects.filter(username__startswith='user_').delete()
        
        with transaction.atomic(): #либо все транзакции выполняем, либо ни одну не выполняем
            # Создание пользователей и профилей
            users = []
            
            for i in range(10):
                username = f"user_{i}_{fake.user_name()}"
                email = fake.email()
                
                # Проверяем, существует ли пользователь
                if not User.objects.filter(username=username).exists():
                    user = User(
                        username=username,
                        email=email,
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        is_active=True
                    )
                    user.set_password('password123')
                    users.append(user)
            
            # Создаем пользователей
            User.objects.bulk_create(users) #1 запрос к БД вместо range и 10 запросов
            
            # Создаем профили для новых пользователей
            for user in users:
                user_type = random.choice(['client', 'employee'])
                
                profile = UserProfile(
                    user=user,
                    user_type=user_type,
                    fio=fake.name(),
                    birthday=fake.date_of_birth(minimum_age=18, maximum_age=65),
                )
                
                if user_type == 'client':
                    profile.company_name = fake.company()
                else:
                    profile.position = random.choice(['Менеджер', 'Разработчик', 'Дизайнер', 'Тестировщик'])
                
                profile.save()
        
        # Создание услуг
        favours = []
        
        with transaction.atomic():
            for i in range(10):
                favour = Favour(
                    name=fake.catch_phrase(),
                    description=fake.text(max_nb_chars=200),
                    price=round(random.uniform(1000, 50000), 2)
                )
                favours.append(favour)
            
            Favour.objects.bulk_create(favours)
        
        # Создание проектов
        projects = []
        
        client_profiles = UserProfile.objects.filter(user_type='client')
        client_users = [profile.user for profile in client_profiles]
        statuses = ['планирование', 'в работе', 'приостановлен', 'завершен', 'отменен']
        
        with transaction.atomic():
            for i in range(10):
                project = Project(
                    name=fake.catch_phrase(),
                    description=fake.text(max_nb_chars=300),
                    status=random.choice(statuses),
                    client_user=random.choice(client_users) if client_users else None
                )
                projects.append(project)
            
            Project.objects.bulk_create(projects)
        
        # Создание отзывов
        reviews = []
        
        project_objects = list(Project.objects.all())
        
        with transaction.atomic():
            for i in range(10):
                review = Review(
                    description=fake.text(max_nb_chars=150),
                    mark=random.randint(1, 5),
                    pr=random.choice(project_objects) if project_objects else None
                )
                reviews.append(review)
            
            Review.objects.bulk_create(reviews)
        
        # Создание услуг в проектах
        project_services = []
        
        employee_profiles = UserProfile.objects.filter(user_type='employee')
        employee_users = [profile.user for profile in employee_profiles]
        favour_objects = list(Favour.objects.all())
        
        with transaction.atomic():
            for i in range(10):
                if project_objects and favour_objects and employee_users:
                    project_service = ProjectService(
                        project=random.choice(project_objects),
                        favour=random.choice(favour_objects),
                        employee_user=random.choice(employee_users),
                        notes=fake.text(max_nb_chars=100)
                    )
                    project_services.append(project_service)
            
            ProjectService.objects.bulk_create(project_services)