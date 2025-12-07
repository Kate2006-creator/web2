from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    if created:
        from general.models import UserProfile
        UserProfile.objects.create(user=instance)


class UserProfile(models.Model):
    USER_TYPES = (
        ('client', 'Клиент'),
        ('employee', 'Сотрудник'),
    )

    birthday = models.DateField("Дата рождения", null=True, blank=True)
    fio = models.TextField("ФИО", null=True, blank=True)
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )

    user_type = models.CharField(
        "Тип пользователя", 
        max_length=10, 
        choices=USER_TYPES
    )

    picture = models.ImageField("Изображение", null=True, upload_to="business")

    # ПОЛЯ ДЛЯ КЛИЕНТОВ
    company_name = models.CharField("Название компании", max_length=200, blank=True)

    # ПОЛЯ ДЛЯ СОТРУДНИКОВ
    position = models.CharField("Должность", max_length=50, blank=True)

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
