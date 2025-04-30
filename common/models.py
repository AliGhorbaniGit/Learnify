from django.db import models
from django.db.models import Avg, Count
from django.core.validators import MinValueValidator, MaxValueValidator

from django.conf import settings


class Category(models.Model):
    """Model representing a category for organizing items (e.g., courses, requests)."""

    title = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=600, blank=True)
    slug = models.SlugField(unique=True, max_length=255)

    def __str__(self):
        """Returns a string representation of the Category, typically the title."""
        return self.title

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['title']


class Tag(models.Model):
    """Model representing a tag for categorizing items (e.g., articles, requests)."""

    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['title']
