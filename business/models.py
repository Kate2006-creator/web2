from django.db import models
from django.contrib.auth.models import User
from general.models import UserProfile 


# Create your models here.

class Favour(models.Model):
    name = models.TextField("Название")
    description = models.TextField("Описание")
    price = models.FloatField("Цена")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self) -> str:
        return self.name

class Project(models.Model):
    name = models.TextField("Название")
    description = models.TextField("Описание")
    status = models.TextField("Статус")

    client_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        verbose_name="Клиент",
        null=True,
    )
    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self) -> str:
        return self.name

class Review(models.Model):
    description = models.TextField("Описание")
    mark = models.IntegerField("Оценка")
    pr = models.ForeignKey("Project", on_delete=models.CASCADE, null=True)
    picture = models.ImageField("Изображение", null=True, upload_to="business")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        
    def __str__(self) -> str:
        return self.description

class ProjectService(models.Model):
    project = models.ForeignKey("Project", on_delete=models.CASCADE, verbose_name="Проект", null=True)
    favour = models.ForeignKey("Favour", on_delete=models.CASCADE, verbose_name="Услуга",null=True)

    employee_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        verbose_name="Сотрудник",
        null=True,
    )
    notes = models.TextField("Примечания", blank=True)

    class Meta:
        verbose_name = "Услуга в проекте"
        verbose_name_plural = "Услуги в проектах"
    
    def __str__(self) -> str:
        return f"{self.favour.name} - {self.project.name}"



    