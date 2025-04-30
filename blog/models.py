from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

from django.conf import settings
from ckeditor.fields import RichTextField
from course.models import Category, Tag


class Writer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='writer')
    bio = models.TextField(blank=True, )
    linkedin_address = models.CharField(blank=True, max_length=255)
    youtube_address = models.CharField(blank=True, max_length=255)
    facebook_address = models.CharField(blank=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Writer'
        verbose_name_plural = 'Writers'
        ordering = ['created_at']


# class ArticleManager(models.Manager):
#     def published(self):
#         return self.filter(status=Article.STATUS_APPROVED)

class Article(models.Model):
    STATUS_WAITING = 'w'
    STATUS_APPROVED = 'a'
    STATUS_NOT_APPROVED = 'na'

    # Choices for status
    STATUS_CHOICES = [
        (STATUS_WAITING, 'Waiting'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_NOT_APPROVED, 'Not Approved'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True,max_length=255)
    image = models.ImageField(upload_to='blog/article', blank=True, null=True, )

    intro_txt = models.TextField()
    description = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    category = models.ManyToManyField(Category, blank=True, related_name='articles')
    writer = models.ForeignKey(
        Writer,
        on_delete=models.PROTECT,
        related_name='articles'
    )
    tag = models.ManyToManyField(Tag, blank=True, related_name='articles')
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=STATUS_WAITING
    )

    # SEO fields
    seoT = models.CharField(blank=True, max_length=60, verbose_name=' SEO title ')
    seoD = models.CharField(blank=True, max_length=160, verbose_name=' SEO description')
    seoK = models.TextField(blank=True, verbose_name=' SEO keywords')
    # meta_tags = models.TextField(blank=True, help_text="Open Graph and Twitter Card metadata")

    related_articles = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='related_to',
                                              verbose_name='Related Articles')

    def get_meta_tags(self):
        """Generate Open Graph and Twitter meta tags for the article."""
        return {
            'og:title': self.seoT or self.title,
            'og:description': self.seoD or self.intro_txt,
            'twitter:title': self.seoT or self.title,
            'twitter:description': self.seoD or self.intro_txt,
            'og:image': self.image.url if self.image else None,
        }

    def __str__(self):
        return self.title

    # def get_comments(self):
    #     return self.comments.filter(status='a').order_by('-submit_date')

    # def get_comment_count(self):
    #     return self.comments.filter(status='a').count()

    @classmethod
    def top_rated_articles(cls, limit=3):
        """
        Get the top-rated articles based on average rating.

        """
        return (
            cls.objects.filter(status='a').annotate(avg_rating=Avg('ratings__score'))
            .order_by('-avg_rating')
            [:limit]
        )

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['created_at']


# class ArticleRateManager(models.Manager):
#     def average_rating(self, article):
#         ratings = self.filter(article=article)
#         return ratings.aggregate(models.Avg('score'))['score__avg'] or 0  # Use 'score' instead of 'rate'


class ArticleRate(models.Model):
    """  Model to store ratings for articles. """

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    submit_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Submit Date'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Score'
    )
    ip = models.GenericIPAddressField(
        verbose_name='User IP Address',
        null=True,
        blank=True
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles_rate')

    # article_rate_manager = ArticleRateManager()

    class Meta:
        verbose_name = 'Article Rate'
        verbose_name_plural = 'Article Rates'
        unique_together = ('article', 'user')

    def __str__(self):
        return f'Rating {self.score} for {self.article.title} on {self.submit_date}'

    # Method to get average rating for an article
    @classmethod
    def average_rating(cls, article):
        """
        Calculate the average rating for a given article.
        """
        ratings = cls.objects.filter(article=article)
        return ratings.aggregate(models.Avg('rate'))['rate__avg'] or 0


class ArticleComment(models.Model):
    STATUS_WAITING = 'w'
    STATUS_APPROVED = 'a'
    STATUS_NOT_APPROVED = 'na'

    # Choices for comment status
    COMMENT_STATUS_CHOICES = [
        (STATUS_WAITING, 'Waiting'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_NOT_APPROVED, 'Not Approved'),
    ]

    article = models.ForeignKey(
        'Article',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='article_comments'
    )

    text = models.TextField(max_length=1000)
    submit_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=2,
        choices=COMMENT_STATUS_CHOICES,
        default=STATUS_WAITING
    )

    class Meta:
        verbose_name = 'Article Comment'
        verbose_name_plural = 'Article Comments'
        ordering = ['-submit_date']

    def __str__(self):
        return f'Comment by {self.user} on {self.article} - Status: {self.status}'
