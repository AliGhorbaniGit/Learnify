from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogList.as_view(), name='blogs-list'),
    path('add-article/', views.AddArticle.as_view(), name='add-article'),
    path('<slug:slug>/', views.BlogDetail.as_view(), name='blog-detail'),

]
