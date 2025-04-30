from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Article, ArticleComment, ArticleRate, Writer


class ArticleInline(admin.TabularInline):
    model = Article
    fields = ['title', 'slug', 'category', 'writer', 'tag']
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'clickable_title', 'writer', 'status', 'created_at', ]
    list_editable = ['status', ]
    list_per_page = 20
    list_select_related = []
    search_fields = ["id", 'teacher', ]
    list_filter = ['title', 'writer', 'status', 'created_at', ]
    list_display_links = ['writer']
    prepopulated_fields = {
        'slug': ['title', ]
    }
    autocomplete_fields = ['writer', ]

    def clickable_title(self, obj):
        url = reverse('admin:blog_article_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.title)

    clickable_title.short_description = 'Title'


@admin.register(ArticleRate)
class ArticleRateAdmin(admin.ModelAdmin):
    list_display = ['id', 'clickable_title', 'score', 'submit_date', 'user']
    list_per_page = 20
    list_filter = ['article', 'submit_date', ]

    def clickable_title(self, obj):
        url = reverse('admin:blog_articlerate_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.article)

    clickable_title.short_description = 'Article'


@admin.register(Writer)
class WriterAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', ]
    search_fields = ['user', ]
    list_per_page = 20
    list_filter = ['user', 'created_at', ]
    list_select_related = ['user', ]
    inlines = [ArticleInline]
    list_display_links = ['user', 'id']


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'clickable_title', 'user', 'text', 'submit_date', 'status', ]
    list_editable = ['status', ]
    list_per_page = 20
    list_select_related = ['article', 'user', ]
    search_fields = ['article', 'status', 'submit_date', ]
    list_filter = ['status', 'submit_date', ]

    def clickable_title(self, obj):
        url = reverse('admin:blog_articlecomment_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.id)

    clickable_title.short_description = 'Article'
