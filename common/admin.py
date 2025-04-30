from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Tag, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'clickable_title', 'slug', ]
    list_per_page = 20
    list_filter = ['title', ]
    prepopulated_fields = {
        'slug': ['title', ]
    }

    def clickable_title(self, obj):
        url = reverse('admin:common_category_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.title)

    clickable_title.short_description = 'Title'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'clickable_title', 'slug']
    list_per_page = 20
    list_filter = ['title', ]
    prepopulated_fields = {
        'slug': ['title', ]
    }

    def clickable_title(self, obj):
        url = reverse('admin:common_tag_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.title)

    clickable_title.short_description = 'Title'
