from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from general.models import UserProfile
from business.models import Project, Review, Favour, ProjectService
from model_bakery import baker

# Create your tests here.
# триггееееррррр

class ProjectsViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.client_profile = UserProfile.objects.get(user=self.user)
        self.client_profile.user_type = 'client'
        self.client_profile.fio = "Тестовый Клиент"
        self.client_profile.company_name = "Test"
        self.client_profile.save()

        self.client.force_authenticate(user=self.user)
    
    def tests_get_list(self):
        project = Project.objects.create(
            name = "Создание веб-страницы",
            description = "Помочь клиенту соблюсти требования",
            status = "в работе",
            client_user = self.user
        )
        r = self.client.get('/api/projects/')

        data = r.json()
        print(data)

        assert project.name == data[0]['name']
        assert project.description== data[0]['description']
        assert len(data) == 1

    def tests_create_project(self):
        r = self.client.post("/api/projects/", {
            "name": "Новый проект",
            "description": "Выживаем",
            "status": "Планирование"
        }) 

        new_project_id = r.json()['id']       
        projects = Project.objects.all()
        assert len (projects)

        new_project = Project.objects.filter(id=new_project_id).first()
        assert new_project.name == 'Новый проект'
        assert new_project.client_user == self.user
        assert new_project.status == "Планирование"

    def tests_delete_project(self):
        projects = baker.make("Project", 10, client_user=self.user)
        
        r = self.client.get('/api/projects/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        assert len(data) == 10

        project_id_to_delete = projects[3].id
        response = self.client.delete(f'/api/projects/{project_id_to_delete}/')

        r = self.client.get('/api/projects/')
        data = r.json()
        assert len(data) == 9

        assert project_id_to_delete not in [i['id'] for i in data]
    
    def tests_update_project(self):
        projects = baker.make("Project", 10, client_user=self.user)
        project: Project = projects[3]

        r = self.client.get(f'/api/projects/{project.id}/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        assert data['name'] == project.name
        
        r = self.client.patch(f'/api/projects/{project.id}/', {
            "name": "Обновленный проект"
        })

        r = self.client.get(f'/api/projects/{project.id}/')
        data = r.json()
        assert data['name'] == "Обновленный проект"

        project.refresh_from_db()
        assert data['name'] == project.name

class FavoursViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def tests_get_list(self):
        favour = Favour.objects.create(
            name="Веб-разработка",
            description="Создание веб-приложений",
            price=50000.0
        )
        r = self.client.get('/api/favours/')

        data = r.json()
        print(data)

        assert favour.name == data[0]['name']
        assert favour.description == data[0]['description']
        assert len(data) == 1

    def tests_create_favour(self):
        r = self.client.post("/api/favours/", {
            "name": "Новая услуга",
            "description": "Описание новой услуги",
            "price": 10000.0
        }) 

        new_favour_id = r.json()['id']       
        favours = Favour.objects.all()
        assert len(favours) == 1

        new_favour = Favour.objects.filter(id=new_favour_id).first()
        assert new_favour.name == 'Новая услуга'
        assert new_favour.description == "Описание новой услуги"
        assert new_favour.price == 10000.0

    def tests_delete_favour(self):
        favours = baker.make("Favour", 10)
        r = self.client.get('/api/favours/')
        data = r.json()
        assert len(data) == 10

        favour_id_to_delete = favours[3].id
        self.client.delete(f'/api/favours/{favour_id_to_delete}/')

        r = self.client.get('/api/favours/')
        data = r.json()
        assert len(data) == 9

        assert favour_id_to_delete not in [i['id'] for i in data]
    
    def tests_update_favour(self):
        favours = baker.make("Favour", 10)
        favour: Favour = favours[3]

        r = self.client.get(f'/api/favours/{favour.id}/')
        data = r.json()
        assert data['name'] == favour.name
        
        r = self.client.patch(f'/api/favours/{favour.id}/', {
            "name": "Обновленная услуга"
        })
        assert r.status_code == 200

        r = self.client.get(f'/api/favours/{favour.id}/')
        data = r.json()
        assert data['name'] == "Обновленная услуга"

        favour.refresh_from_db()
        assert data['name'] == favour.name

class ReviewsViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.client_profile = UserProfile.objects.get(user=self.user)
        self.client_profile.user_type = 'client'
        self.client_profile.fio = "Тестовый Клиент"
        self.client_profile.company_name = "Test"
        self.client_profile.save()
    
    def tests_get_list(self):
        project = Project.objects.create(
            name="Тестовый проект",
            description="Описание проекта",
            status="в работе",
            client_user=self.user
        )
        
        review = Review.objects.create(
            description="Отличная работа!",
            mark=5,
            pr=project
        )
        
        r = self.client.get('/api/reviews/')

        data = r.json()
        print(data)

        assert len(data) == 1
        assert review.description == data[0]['description']
        assert review.mark == data[0]['mark']


    def tests_create_review(self):
        project = Project.objects.create(
            name="Проект для отзыва",
            description="Описание",
            status="завершен",
            client_user=self.user
        )
        
        r = self.client.post("/api/reviews/", {
            "description": "Хорошая работа",
            "mark": 4,
            "pr": project.id  
        }) 
        
        new_review_id = r.json()['id']       
        reviews = Review.objects.all()
        assert len(reviews) == 1

        new_review = Review.objects.filter(id=new_review_id).first()
        assert new_review.description == 'Хорошая работа'
        assert new_review.mark == 4
        assert new_review.pr == project

    def tests_delete_review(self):
        project = Project.objects.create(
            name="Проект для теста",
            description="Описание",
            status="в работе",
            client_user=self.user
        )

        reviews = baker.make("Review", 10, pr=project)
        
        r = self.client.get('/api/reviews/')
        data = r.json()
        
        assert len(data) == 10

        review_id_to_delete = reviews[3].id
        self.client.delete(f'/api/reviews/{review_id_to_delete}/')

        r = self.client.get('/api/reviews/')
        data = r.json()
        
        assert len(data) == 9

        assert review_id_to_delete not in [i['id'] for i in data]
    
    def tests_update_review(self):
        project = Project.objects.create(
            name="Проект для обновления",
            description="Описание",
            status="в работе",
            client_user=self.user
        )
        
        reviews = baker.make("Review", 10, pr=project)
        review: Review = reviews[3]

        r = self.client.get(f'/api/reviews/{review.id}/')
        data = r.json()
        assert data['description'] == review.description
        
        r = self.client.patch(f'/api/reviews/{review.id}/', {
            "description": "Обновленный отзыв"
        })
        
        assert r.status_code == 200

        r = self.client.get(f'/api/reviews/{review.id}/')
        data = r.json()
        assert data['description'] == "Обновленный отзыв"

        review.refresh_from_db()
        assert data['description'] == review.description
    
class ProjectServicesViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123222'
        )

        self.client_profile = UserProfile.objects.get(user=self.user1)
        self.client_profile.user_type = 'client'
        self.client_profile.fio = "Тестовый Клиент"
        self.client_profile.company_name = "Test"
        self.client_profile.save()

        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123221111'
        )

        self.client_profile = UserProfile.objects.get(user=self.user2)
        self.client_profile.user_type = 'employee'
        self.client_profile.fio = "Тестовый сотрудник"
        self.client_profile.position = "Test"
        self.client_profile.save()

        self.client.force_authenticate(user=self.user1)
    
    def tests_get_list(self):
        project = Project.objects.create(
            name="Тестовый проект",
            description="Описание проекта",
            status="в работе",
            client_user=self.user1
        )
        
        favour = Favour.objects.create(
            name="Веб-разработка",
            description="Создание веб-приложений",
            price=50000.0
        )
        
        project_service = ProjectService.objects.create(
            project=project,
            favour=favour,
            employee_user=self.user2,
            notes="Тестовые примечания"
        )
        
        r = self.client.get('/api/project_services/')

        data = r.json()
        print(data)

        assert len(data) == 1
        assert project_service.notes == data[0]['notes']

    def tests_create_project_service(self):
        project = Project.objects.create(
            name="Проект для услуги",
            description="Описание",
            status="в работе",
            client_user=self.user1
        )
        
        favour = Favour.objects.create(
            name="Дизайн",
            description="Дизайн сайта",
            price=30000.0
        )
        
        r = self.client.post("/api/project_services/", {
            "project": project.id,
            "favour": favour.id,
            "employee_user": self.user2.id,
            "notes": "Новые примечания"
        }) 
        
        new_project_service_id = r.json()['id']       
        project_services = ProjectService.objects.all()
        assert len(project_services) == 1

        new_project_service = ProjectService.objects.filter(id=new_project_service_id).first()
        assert new_project_service.project == project
        assert new_project_service.favour == favour
        assert new_project_service.employee_user == self.user2
        assert new_project_service.notes == "Новые примечания"

    def tests_delete_project_service(self):
        project = Project.objects.create(
            name="Проект для теста",
            description="Описание",
            status="в работе",
            client_user=self.user1
        )

        favour = Favour.objects.create(
            name="Услуга",
            description="Описание услуги",
            price=10000.0
        )

        project_services = baker.make("ProjectService", 10, project=project, favour=favour, employee_user=self.user1)
        
        r = self.client.get('/api/project_services/')
        data = r.json()
        
        assert len(data) == 10

        project_service_id_to_delete = project_services[3].id
        self.client.delete(f'/api/project_services/{project_service_id_to_delete}/')

        r = self.client.get('/api/project_services/')
        data = r.json()
        
        assert len(data) == 9

        assert project_service_id_to_delete not in [i['id'] for i in data]
    
    def tests_update_project_service(self):
        project = Project.objects.create(
            name="Проект для обновления",
            description="Описание",
            status="в работе",
            client_user=self.user1
        )
        
        favour = Favour.objects.create(
            name="Базовая услуга",
            description="Описание",
            price=20000.0
        )
        
        project_services = baker.make("ProjectService", 10, project=project, favour=favour, employee_user=self.user1)
        project_service: ProjectService = project_services[3]

        r = self.client.get(f'/api/project_services/{project_service.id}/')
        data = r.json()
        assert data['notes'] == project_service.notes
        
        r = self.client.patch(f'/api/project_services/{project_service.id}/', {
            "notes": "Обновленные примечания"
        })
        
        assert r.status_code == 200

        r = self.client.get(f'/api/project_services/{project_service.id}/')
        data = r.json()
        assert data['notes'] == "Обновленные примечания"

        project_service.refresh_from_db()
        assert data['notes'] == project_service.notes
