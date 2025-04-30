from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Course, Teacher, CourseVideo, CourseAdditionRequest, CourseComment, CourseRate


class CourseVidioInline(admin.TabularInline):
    model = CourseVideo
    fields = ['course', 'title', 'video_file', 'thumbnail', 'description', ]
    extra = 1


class CourseInline(admin.TabularInline):
    model = Course
    fields = ['title', 'intro_txt', 'hours', 'status', ]
    extra = 1


class AddCourseRequestInline(admin.TabularInline):
    model = CourseAdditionRequest
    fields = ['title', 'description', 'video']
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'clickable_title', 'hours', 'teacher', 'created_at', 'status', ]
    list_editable = ['status', 'hours']
    list_per_page = 20
    list_select_related = []
    search_fields = ["id", 'teacher', ]
    list_filter = ['title', 'hours', 'teacher', 'created_at', 'status', ]
    list_display_links = ['teacher']
    prepopulated_fields = {
        'slug': ['title', ]
    }
    inlines = [CourseVidioInline, ]

    def clickable_title(self, obj):
        url = reverse('admin:course_course_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.title)

    clickable_title.short_description = 'Title'


@admin.register(CourseRate)
class CourseRateAdmin(admin.ModelAdmin):
    list_display = ['id', 'clickable_title', 'score', 'submit_date', 'user']
    list_per_page = 20
    list_filter = ['course', 'submit_date', ]

    def clickable_title(self, obj):
        url = reverse('admin:course_courserate_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.course)

    clickable_title.short_description = 'course'


@admin.register(CourseComment)
class CourseCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'clickable_title', 'user', 'text', 'submit_date', 'status', ]
    list_editable = ['status', ]
    list_per_page = 20
    list_select_related = ['course', 'user', ]
    search_fields = ['course', 'status', 'submit_date', ]
    list_filter = ['status', 'submit_date', ]

    def clickable_title(self, obj):
        url = reverse('admin:course_coursecomment_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.id)

    clickable_title.short_description = 'Course'


@admin.register(CourseAdditionRequest)
class CourseAdditionRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'application_time', ]
    list_per_page = 20
    list_select_related = ['user', ]
    search_fields = ["id", 'user', 'application_time', ]
    list_filter = ['user', 'application_time', ]
    list_display_links = ['id', 'user']
    ordering = ['-application_time']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'hire_date', ]
    list_per_page = 20
    list_filter = ['user', 'hire_date', ]
    list_select_related = ['user', ]
    inlines = [CourseInline]
    list_display_links = ['user', 'id']
