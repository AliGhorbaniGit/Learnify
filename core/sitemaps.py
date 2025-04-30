from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Article
from course.models import Course


class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return ['core:home', 'core:contact-us', 'core:terms', 'core:faq',
                'core:about-us', ]

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Article.objects.filter(status='a').all()

    def location(self, item):
        return reverse('blog:blog-detail', args=[item.slug])


class CourseSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Course.objects.filter(status='a').all()

    def location(self, item):
        return reverse('course:course-detail', args=[item.slug])
