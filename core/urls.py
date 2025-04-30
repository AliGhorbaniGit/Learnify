from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('contact-us/', views.ContactUs.as_view(), name='contact-us'),
    path('terms/', views.TermsList.as_view(), name='terms'),
    path('faq/', views.Faq.as_view(), name='faq'),
    path('aboutus/', views.about, name='about-us'),
    path('filter/<slug:slug>/', views.filter_view, name='filter'),
    path('search/', views.search_view, name='search'),
    path('profile/', views.profile, name='profile'),
    path('profile-overview/<str:username>/', views.profile_overview, name='profile-overview'),
    path('profile-update/', views.profile_update, name='profile-update'),
]
