from django.db import models
from django.db.models import Avg, Count
from django.core.validators import MinValueValidator, MaxValueValidator

from django.conf import settings
from common.models import Category, Tag


class Teacher(models.Model):
    """ Model representing a teacher with a one-to-one relationship to the user model."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='teacher_profile'
    )
    bio = models.TextField(max_length=1000, blank=True)
    hire_date = models.DateField(auto_now_add=True)
    linkedin_address = models.CharField(blank=True, max_length=255)
    youtube_address = models.CharField(blank=True, max_length=255)
    facebook_address = models.CharField(blank=True, max_length=255)

    def __str__(self):
        """Returns the username of the associated user."""
        return self.user.username

    class Meta:
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'
        ordering = ['hire_date']


class CourseAdditionRequest(models.Model):
    """Model representing a request for teaching or tutoring services."""
    STATUS_WAITING = 'w'
    STATUS_APPROVED = 'a'
    STATUS_NOT_APPROVED = 'na'

    # Choices for status
    STATUS_CHOICES = [
        (STATUS_WAITING, 'Waiting'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_NOT_APPROVED, 'Not Approved'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teach_requests'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, )
    video = models.FileField(upload_to='course/add_course_request/')
    application_time = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=STATUS_WAITING
    )

    def __str__(self):
        """Returns a string representation of the TeachRequest, usually the title."""
        return f'{self.user} : {self.title}'

    class Meta:
        verbose_name = 'Course Addition Request '
        verbose_name_plural = 'Addition Requests'
        ordering = ['application_time']


class Course(models.Model):
    """Model representing a course with associated details."""
    STATUS_WAITING = 'w'
    STATUS_APPROVED = 'a'
    STATUS_NOT_APPROVED = 'na'

    # Choices for status
    STATUS_CHOICES = [
        (STATUS_WAITING, 'Waiting'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_NOT_APPROVED, 'Not Approved'),
    ]

    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, max_length=255)  # Slug for SEO-friendly URLs
    image = models.ImageField(blank=True, null=True, upload_to='course/course_images/')
    intro_txt = models.TextField(blank=True, )
    hours = models.PositiveIntegerField(blank=True, default=1)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT,
                                related_name='courses')
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                      related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    category = models.ManyToManyField(Category, blank=True, related_name='courses')
    tag = models.ManyToManyField(Tag, blank=True, related_name='courses')
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set on update

    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=STATUS_WAITING
    )

    # SEO fields
    seo_title = models.CharField(max_length=60, blank=True, verbose_name='SEO Title')
    seo_description = models.CharField(max_length=160, blank=True, verbose_name='SEO Description')
    seo_keywords = models.TextField(blank=True, verbose_name='SEO Keywords')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['title']

    def get_comments(self):
        return self.comments.filter(status='a').order_by('-datetime_created')

    def get_comment_count(self):
        return self.comments.filter(status='a').count()

    @classmethod
    def top_rated_courses(cls, limit=3):
        """
        Get the top-rated articles based on average rating.

        This method prefetches related ratings and videos to optimize
        query performance, especially when these related fields are accessed.

        """
        return (
            cls.objects.filter(status='a').annotate(video_count=Count('videos')).annotate(
                avg_rating=Avg('ratings__score'))
            .order_by('-avg_rating')
            [:limit]  # Limit the number of results
        )

    @classmethod
    def course_video_count(cls):
        """
        Get all courses with the count of their associated videos.
        """
        return (
            cls.objects.annotate(video_count=Count('videos'))  # Count related CourseVideo instances
        )


class CourseVideo(models.Model):
    """Model representing a video associated with a course."""
    STATUS_WAITING = 'w'
    STATUS_APPROVED = 'a'
    STATUS_NOT_APPROVED = 'na'

    COMMENT_STATUS_CHOICES = [
        (STATUS_WAITING, 'Waiting'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_NOT_APPROVED, 'Not Approved'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='course/course_videos/')
    thumbnail = models.ImageField(upload_to='course/course_thumbnails/', blank=True, null=True)
    description = models.TextField(blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=2,
        choices=COMMENT_STATUS_CHOICES,
        default=STATUS_WAITING
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'


# class CourseRateManager(models.Manager):
#     def average_rating(self, course):
#         ratings = self.filter(article=course)
#         return ratings.aggregate(models.Avg('score'))['score__avg'] or 0


class CourseRate(models.Model):
    """ Model representing a rating for a course. """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='ratings'
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submit_date = models.DateTimeField(auto_now_add=True, )

    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    ip = models.GenericIPAddressField(null=True, blank=True)

    # course_rate_manager = CourseRateManager()

    class Meta:
        unique_together = ('course', 'user')

    def __str__(self):
        return f"{self.course.title} rated {self.score} by {self.ip} on {self.submit_date}"


class CourseComment(models.Model):
    STATUS_WAITING = 'w'
    STATUS_APPROVED = 'a'
    STATUS_NOT_APPROVED = 'na'

    COMMENT_STATUS_CHOICES = [
        (STATUS_WAITING, 'Waiting'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_NOT_APPROVED, 'Not Approved'),
    ]

    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_comments'
    )

    text = models.TextField(max_length=1000)
    submit_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=2,
        choices=COMMENT_STATUS_CHOICES,
        default=STATUS_WAITING
    )

    class Meta:
        verbose_name = 'Course Comment'
        verbose_name_plural = 'Course Comments'
        ordering = ['-submit_date']

    def __str__(self):
        return f'Comment by {self.user} on {self.course} - Status: {self.status}'
