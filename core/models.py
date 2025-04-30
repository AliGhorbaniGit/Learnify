from django.contrib.auth.models import AbstractUser
from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator


class Language(models.Model):
    """ user language model """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """Creating a Custom user extending from AbstractUser."""
    email = models.EmailField(null=False, blank=False, unique=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField(blank=True, null=True, validators=[
        MinValueValidator(7),
        MaxValueValidator(90)
    ])
    nationality = models.CharField(max_length=200, blank=True, )
    bio = models.TextField(max_length=1000, blank=True, )
    languages = models.ManyToManyField(Language, blank=True)
    education = models.CharField(max_length=600, blank=True, verbose_name='Education')
    image = models.ImageField(blank=True, null=True, upload_to='core/user_images')
    age_visible = models.BooleanField(default=True)
    education_visible = models.BooleanField(default=True)
    article_visible = models.BooleanField(default=True)
    course_visible = models.BooleanField(default=True)

    is_teacher = models.BooleanField(default=False, verbose_name='is teacher')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'Users Profile'
