from django.test import TestCase
from rest_framework.test import APIClient
from business.models import Project, Review, Favour, ProjectService
from model_bakery import baker

class ProjectsViewsetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # В бизнес-сервисе мы не создаем пользователей, 
        # мы просто используем их ID (например, 1) для связи.
        self.client_user_id = 1

    def tests_get_list(self):
        project = Project.objects.create(
            name = "Создание веб-страницы",
            description = "Помочь клиенту соблюсти требования",
            status = "в работе",
            client_user_id = self.client_user_id  # ИСПРАВЛЕНО
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
            "status": "Планирование",
            "client_user_id": self.client_user_id # Добавили ID клиента
        }) 

        new_project_id = r.json()['id']       
        projects = Project.objects.all()
        assert len (projects)

        new_project = Project.objects.filter(id=new_project_id).first()
        assert new_project.name == 'Новый проект'
        assert new_project.client_user_id == self.client_user_id # ИСПРАВЛЕНО
        assert new_project.status == "Планирование"

    def tests_delete_project(self):
        projects = baker.make("Project", 10, client_user_id=self.client_user_id) # ИСПРАВЛЕНО
        
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
        projects = baker.make("Project", 10, client_user_id=self.client_user_id) # ИСПРАВЛЕНО
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
        self.client_user_id = 1
    
    def tests_get_list(self):
        project = Project.objects.create(
            name="Тестовый проект",
            description="Описание проекта",
            status="в работе",
            client_user_id=self.client_user_id # ИСПРАВЛЕНО
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
            client_user_id=self.client_user_id # ИСПРАВЛЕНО
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
            client_user_id=self.client_user_id # ИСПРАВЛЕНО
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
            client_user_id=self.client_user_id # ИСПРАВЛЕНО
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
        self.client_user_id = 1
        self.employee_user_id = 2
    
    def tests_get_list(self):
        project = Project.objects.create(
            name="Тестовый проект",
            description="Описание проекта",
            status="в работе",
            client_user_id=self.client_user_id # ИСПРАВЛЕНО
        )
        
        favour = Favour.objects.create(
            name="Веб-разработка",
            description="Создание веб-приложений",
            price=50000.0
        )
        
        project_service = ProjectService.objects.create(
            project=project,
            favour=favour,
            employee_user_id=self.employee_user_id, # ИСПРАВЛЕНО
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
            client_user_id=self.client_user_id # ИСПРАВЛЕНО
        )
        
        favour = Favour.objects.create(
            name="Дизайн",
            description="Дизайн сайта",
            price=30000.0
        )
        
        r = self.client.post("/api/project_services/", {
            "project": project.id,
            "favour": favour.id,
            "employee_user_id": self.employee_user_id, # ИСПРАВЛЕНО
            "notes": "Новые примечания"
        }) 
        
        new_project_service_id = r.json()['id']       
        project_services = ProjectService.objects.all()
        assert len(project_services) == 1

        new_project_service = ProjectService.objects.filter(id=new_project_service_id).first()
        assert new_project_service.project == project
        assert new_project_service.favour == favour
        assert new_project_service.employee_user_id == self.employee_user_id # ИСПРАВЛЕНО
        assert new_project_service.notes == "Новые примечания"

    def tests_delete_project_service(self):
        project = Project.objects.create(
            name="Проект для теста",
            description="Описание",
            status="в работе",
            client_user_id=self.client_user_id # ИСПРАВЛЕНО
        )

        favour = Favour.objects.create(
            name="Услуга",
            description="Описание услуги",
            price=10000.0
        )

        project_services = baker.make("ProjectService", 10, project=project, favour=favour, employee_user_id=self.employee_user_id) # ИСПРАВЛЕНО
        
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
            client_user_id=self.client_user_id # ИСПРАВЛЕНО
        )
        
        favour = Favour.objects.create(
            name="Базовая услуга",
            description="Описание",
            price=20000.0
        )
        
        project_services = baker.make("ProjectService", 10, project=project, favour=favour, employee_user_id=self.employee_user_id) # ИСПРАВЛЕНО
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