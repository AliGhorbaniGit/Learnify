from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from ticket.models import Ticket, TicketResponse
from course.admin import AddCourseRequestInline
from .models import CustomUser, Language, UserProfile


class TicketInline(admin.TabularInline):
    model = Ticket
    fields = ['id', 'title', 'description', 'status', 'user', ]
    extra = 1


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    fields = ['id', 'is_teacher', 'age', 'nationality', 'bio',
              'languages', 'education', 'image', 'age_visible',
              'education_visible', 'article_visible', 'course_visible', ]
    extra = 1


class TicketResponseInline(admin.TabularInline):
    model = TicketResponse
    fields = ['id', 'ticket', 'response_text', 'admin_user']
    extra = 1

    def save_related(self, request, formset, change):
        # Set the admin_user field to the current user for each TicketResponse
        for ticket_response in formset.save(commit=False):
            ticket_response.admin_user = request.user  # Set the admin user
            ticket_response.save()  # Save the instance
        super().save_related(request, formset, change)


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "clickable_title", "first_name", "last_name", "email"]
    list_per_page = 20
    list_select_related = []
    list_filter = ["groups", ]
    search_fields = ["id", "username", "first_name", ]
    inlines = [UserProfileInline, TicketInline, AddCourseRequestInline, ]

    def clickable_title(self, obj):
        url = reverse('admin:core_customuser_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.username)

    clickable_title.short_description = 'Username'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "is_teacher", "age", "nationality", ]
    list_editable = ["is_teacher", ]
    list_per_page = 20
    list_select_related = ['user', ]
    list_filter = ["is_teacher", ]


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', ]
    list_per_page = 20
    list_display_links = ['name']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'status', 'submit_date', ]
    list_per_page = 20
    list_select_related = ['user', ]
    search_fields = ['id', 'user', 'submit_date', ]
    list_editable = ['status', ]
    list_filter = ['user', 'submit_date', 'status', ]
    list_display_links = ['id', 'user']
    inlines = [TicketResponseInline, ]
