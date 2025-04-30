"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import sitemaps
from django.urls import path
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import StaticViewSitemap, BlogSitemap, CourseSitemap
from django.views.defaults import server_error
from django.conf.urls import handler404, handler403, handler400, handler500

from core.views import custom_bad_request_view, custom_forbidden_view, custom_500_view, custom_404_view

sitemaps = {
    'static': StaticViewSitemap(),
    'blog': BlogSitemap(),
    'course': CourseSitemap(),
}

admin.site.site_header = 'Admin'
admin.site.index_title = 'Edrock'

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('admin/', admin.site.urls),  # default
    path('__debug__/', include('debug_toolbar.urls')),  # debug toolbar url
    path('accounts/', include('allauth.urls')),  # allauth
    path('', include('core.urls')),  # custom app
    path('blogs/', include('blog.urls')),  # custom app
    path('courses/', include('course.urls')),  # custom app

    # for maintenance situations make it uncomment and make comment the above urls
    # path('', TemplateView.as_view(template_name='core/maintenance.html'), name='maintenance')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# ERROR HANDLERS :
handler404 = custom_404_view
handler403 = custom_forbidden_view
handler400 = custom_bad_request_view
handler500 = custom_500_view
