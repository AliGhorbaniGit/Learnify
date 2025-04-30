from django.urls import path

from . import views

app_name = 'course'

urlpatterns = [
    path('request/', views.CourseAdditionRequestView.as_view(), name='add-course-request'),
    path('add-course/', views.AddCourse.as_view(), name='add-course'),
    path('add-video/', views.AddVideo.as_view(), name='add-video'),
    path('', views.CourseList.as_view(), name='courses-list'),
    path('<slug:slug>/', views.CourseDetail.as_view(), name='course-detail'),

    ]
