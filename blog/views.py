from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.utils.html import strip_tags
from django.views import generic
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg


from course.models import Course
from .models import Article, Category, ArticleComment, ArticleRate, Writer
from .forms import ArticleCommentForm, ArticleRatingForm, AddArticleForm


class BlogList(generic.ListView):
    """
    A view that displays a paginated list of published blog articles.

    This view retrieves articles from the database where the
    status is 'a' (active) and allows users to navigate
    through the articles with pagination.

    Context:
        blogs: A list of active articles.
        categories: A list of all categories.
        top_rated_articles: A list of the top-rated articles.
        top_rated_courses: A list of top-rated courses.

    Pagination:
        The view will paginate results, showing a fixed number
        of articles per page (defined by `paginate_by`).
    """

    template_name = 'blog/blog-list.html'
    model = Article
    context_object_name = 'blogs'
    paginate_by = 4

    http_method_names = ['get']

    def get_queryset(self):
        return Article.objects.filter(status='a').select_related('writer__user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context['top_rated_articles'] = Article.top_rated_articles(limit=4)
        context['top_rated_courses'] = Course.top_rated_courses(limit=4)
        return context


class BlogDetail(generic.DetailView):
    """
    A view that displays detailed information about a specific blog article,
    including comments, ratings, and related articles.

    Attributes:
        model (Article): The model associated with this view.
        template_name (str): The template to render for this view.
        form_class (ArticleCommentForm): The form class used for submitting comments.

    Methods:
        get_queryset(): Returns the queryset including the writer's user profile for related objects.        post(request, *args, **kwargs): Handles POST requests for submitting comments and ratings.
        handle_comment_form(request): Processes the comment submission form.
        handle_rating_form(request): Processes the rating submission form.
    """
    model = Article
    template_name = 'blog/blog-detail.html'
    form_class = ArticleCommentForm

    def get_queryset(self):
        return super().get_queryset().select_related('writer__user__profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # all available categories
        context["categories"] = Category.objects.all()

        # Fetch top-rated articles, limit to 3
        context['top_rated_articles'] = Article.top_rated_articles(limit=3)

        # Fetch top-rated courses, limit to 3
        context['top_rated_courses'] = Course.top_rated_courses(limit=4)

        # Get approved comments for the current article
        context['comments'] = ArticleComment.objects.filter(article=self.object, status='a').select_related(
            'user__profile')

        # Calculate the average rating for the current article
        context['average_rating'] = ArticleRate.objects.filter(article=self.object).aggregate(Avg('score'))[
                                        'score__avg'] or 0

        # Get the user's rating for the current article if authenticated
        context['user_rating'] = (
            self.object.ratings.filter(user=self.request.user).first() if self.request.user.is_authenticated else None
        )

        # Get the current article's categories
        current_article_categories = self.object.category.all()

        # Retrieve other articles that have similar categories, excluding the current article
        similar_articles = Article.objects.filter(
            category__in=current_article_categories
        ).exclude(id=self.object.id).distinct()[:3].select_related('writer__user')  # Limit to 3 similar articles

        # similar articles
        context['similar_articles'] = similar_articles
        # comment form
        context['comment_form'] = self.form_class()

        # rating form
        context['rating_form'] = ArticleRatingForm()

        return context
        

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        # Get the current article object
        self.object = self.get_object()

        # Check if the comment form was submitted
        if 'comment_form' in request.POST:
            return self.handle_comment_form(request)

        # Check if the rating form was submitted
        elif 'rating_form' in request.POST:
            return self.handle_rating_form(request)

        # If neither form is valid, return the same context again
        context = self.get_context_data(object=self.object)
        context['comment_form'] = ArticleCommentForm(request.POST)
        context['rating_form'] = ArticleRatingForm(request.POST)
        return self.render_to_response(context)

    def handle_comment_form(self, request):
        comment_form = ArticleCommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = self.object
            comment.user = request.user

            # Sanitize the comment content to prevent XSS attacks
            comment.text = strip_tags(comment.text)

            comment.save()

            messages.success(request,
                             'Success! Your comment has been submitted and is awaiting approval. '
                             'We appreciate your contributions!')
            return redirect('blog:blog-detail', slug=self.object.slug)
        else:
            messages.warning(request,
                             'Oops! There was an issue with your comment submission. '
                             'Please check the errors and try again.')

            for error in comment_form.errors.values():
                messages.error(request, ', '.join(error))

            context = self.get_context_data(object=self.object)
            context['comment_form'] = comment_form
            return self.render_to_response(context)

    def handle_rating_form(self, request):
        rating_form = ArticleRatingForm(request.POST)

        if rating_form.is_valid():
            if not ArticleRate.objects.filter(article=self.object, user=request.user).exists():
                ArticleRate.objects.create(
                    article=self.object,
                    user=request.user,
                    score=rating_form.cleaned_data['score']
                )

                messages.success(request, 'Great! Your rating has been recorded. We appreciate your feedback!')
                return redirect('blog:blog-detail', slug=self.object.slug)

            else:
                messages.warning(request, 'You have already rated this article.')

        else:
            messages.warning(request,
                             'Something went wrong with your submission. Please check for mistakes and try again.')

        context = self.get_context_data(object=self.object)
        context['rating_form'] = rating_form
        return self.render_to_response(context)


class AddArticle(LoginRequiredMixin, generic.CreateView):
    model = Article
    form_class = AddArticleForm
    template_name = 'blog/add-article.html'  # Template to render the form

    def post(self, request, *args, **kwargs):
        # Create a form instance with POST data and uploaded files
        article_form = self.form_class(request.POST, request.FILES)

        if article_form.is_valid():
            # Create or get the Writer object for the logged-in user
            writer, created = Writer.objects.get_or_create(user=request.user)

            # Create the article instance without saving it to the database yet
            article = article_form.save(commit=False)
            article.writer = writer  # Associate the article with the writer

            # Save the article instance
            article.save()

            # Set a success message
            messages.success(request, 'Great job! Your article has been submitted. '
                                      'It will be reviewed by our admin team and published upon approval.')
            return redirect(self.get_success_url())  # Redirect to success URL
        else:
            # If form is not valid, set an error message
            messages.warning(request, 'Oops! Your article wasnt submitted due to some errors. '
                                      'Please check the form and submit it again.')

        # Render the form again with the errors
        return render(request, self.template_name, {'form': article_form})

    def get_success_url(self):
        # Redirect to the profile page after successful submission
        return reverse('core:profile')
