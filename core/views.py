from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib import messages
import logging
from django.views.decorators.http import require_http_methods

from course.models import Course, Tag, Category
from blog.models import Article
from ticket.models import Ticket
from ticket.forms import TicketForm
from .models import CustomUser, UserProfile
from .forms import SearchForm, LanguageForm, UserUpdateForm, UserProfileUpdateForm

logger = logging.getLogger(__name__)


class Home(generic.TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["random_tags"] = Tag.objects.order_by('?')[:5]
        context['top_rated_courses'] = Course.top_rated_courses(limit=3).select_related('teacher__user')
        context['current_path'] = self.request.path
        return context


def filter_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if category:
        blogs = Article.objects.filter(category=category).select_related('writer__user')
        courses = Course.objects.filter(category=category).select_related('teacher__user')

        if not courses.exists() and not blogs.exists():
            messages.warning(request, 'Nothing Found: There are no articles or courses available in that category.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            top_rated_courses = Course.top_rated_courses(limit=3)
            categories = Category.objects.all()

            return render(request, 'core/search-and-filter-list.html',
                          {'blogs': blogs, 'courses': courses, 'categories': categories,
                           'top_rated_courses': top_rated_courses}
                          )


@require_http_methods(["GET"])
def about(request):
    """
     Render the about page with top-rated courses.

     Args:
         request: The HTTP request object.

     Returns:
         HttpResponse: Rendered HTML for the about page with context.
     """

    try:
        top_rated_courses = Course.top_rated_courses(limit=4)
    except Exception as e:
        top_rated_courses = []

    context = {
        'top_rated_courses': top_rated_courses,
        'about_page': 'about_page'
    }

    return render(request, 'core/about.html', context=context)


class Faq(generic.TemplateView):
    """
       A view that renders the FAQ page.
    """
    template_name = 'core/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_rated_courses'] = Course.top_rated_courses(limit=4)
        return context


def search_view(request):
    """
    View function to handle search requests.

    It processes a search form submitted via GET request, validates the input,
    performs searches for courses and articles based on the query, and renders
    the search results. It also handles user feedback through messages.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered template with search results or redirects with a message
        if the input is invalid.
    """
    form = SearchForm(request.GET)

    if form.is_valid():
        query = form.cleaned_data['query']
        logger.info(f'Search performed for query: "{query}"')

        if not query.strip():
            messages.warning(request, 'Oops! It seems you forgot to enter a search term. Please try again.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Perform case-insensitive search for courses and articles
        courses = Course.objects.filter(title__icontains=query)
        articles = Article.objects.filter(title__icontains=query)

        if not courses.exists() and not articles.exists():
            messages.info(request, 'No results were found for your search. Please try different keywords.')

        categories = Category.objects.all()

        top_rated_courses = Course.top_rated_courses(limit=3)
        context = {
            'courses': courses,
            'blogs': articles,
            'query': query,
            'categories': categories,
            'top_rated_courses': top_rated_courses,
            'form': form,
        }

        return render(request, 'core/search-and-filter-list.html', context)

    else:
        messages.warning(request,
                         'It looks like your search input isn’t quite right. Please enter a valid search term.')
        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def profile(request):
    """
       View function to display and update user profile information.
    """
    user = request.user

    custom_user = get_object_or_404(CustomUser.objects.select_related(
        'profile',
        'writer',
        'teacher_profile'
    ).prefetch_related(
        'profile__languages',
        'writer__articles',
        'teacher_profile__courses__videos',
        'teach_requests',
        'tickets__responses__admin_user__profile'
    ), username=user.username)

    language_form = LanguageForm
    context = {
        'language_form': language_form,
        'custom_user': custom_user,
    }

    if request.method == 'POST':
        added_language = LanguageForm(request.POST)
        if added_language.is_valid():
            form = LanguageForm(request.POST, instance=custom_user.profile)
            form.save()
            messages.success(request, 'Language updated')
        else:
            messages.error(request, 'Something went wrong, Try again')

    return render(request, 'core/profile.html', context)


# @ratelimit(key='ip', rate='1/m', method='ALL', block=True)

@require_http_methods(["GET"])
def profile_overview(request, username):
    """
      Display an overview of a user's profile, including their articles and courses.

      This view fetches a user based on the given username and retrieves all
      published articles and courses associated with that user. If the user is
      not found, a 404 error is raised.
    """
    user = get_object_or_404(CustomUser.objects.select_related('profile'), username=username)

    articles = Article.objects.filter(writer__user=user, status='a')
    courses = Course.objects.filter(teacher__user=user, status='a').prefetch_related('videos')

    context = {
        'user': user,
        'articles': articles,
        'courses': courses
    }
    return render(request, 'core/profile-overview.html', context)


class ContactUs(generic.CreateView):
    """
    Handle user ticket submissions through a contact form.

    This view allows authenticated users to submit a ticket for
    support or inquiries. It uses a form to gather ticket details
    and provides user feedback upon submission.
    """

    model = Ticket
    form_class = TicketForm
    template_name = 'core/contact.html'

    def form_valid(self, form):
        """Called when the form is valid."""
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, 'Your ticket has been submitted successfully. We will reply shortly. '
                                           'You can view the response in your profile.'
                             )
            return response
        else:
            messages.warning(self.request, 'You need to be logged in to submit a ticket.')
            return redirect(self.request.META.get('HTTP_REFERER', '/'))

    def form_invalid(self, form):
        """Called when the form is invalid."""
        messages.warning(self.request,
                         '!! Your submission was not sent. Please ensure that the ticket title has at least '
                         '5 characters and the ticket description has at least 10 characters.')

        referer_url = self.request.META.get('HTTP_REFERER', '/')
        return redirect(referer_url)  # Redirect to the referring URL

    def get_context_data(self, **kwargs):
        """Add additional context data for rendering the template."""
        context = super().get_context_data(**kwargs)
        context['top_rated_courses'] = Course.top_rated_courses(limit=4)
        context['contact_page'] = 'page'

        return context

    def get_success_url(self):
        """Redirect to the referring URL or a default one after a successful submission."""
        return self.request.META.get('HTTP_REFERER', '/')


@login_required
def profile_update(request):
    """
      Update the user's profile information.

      This view allows authenticated users to update their personal
      information and additional profile details. It handles both the
      user and profile forms, validating input and saving changes
      upon successful submission.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    user_form = UserUpdateForm(instance=request.user)
    profile_form = UserProfileUpdateForm(instance=profile)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been successfully updated!')
            return redirect('core:profile')

        else:
            messages.warning(request, 'Please correct the errors below. ')
            context = {
                'user_form': user_form,
                'profile_form': profile_form,
                'profile': profile,
            }
            return render(request, 'core/profile-update.html', context)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    }

    return render(request, 'core/profile-update.html', context)


def redirect_user(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class TermsList(generic.TemplateView):
    """
     A view to display the terms and conditions page.

     This view renders a template containing the terms and conditions
     of the application and also includes a list of top-rated courses
     to provide users with recommended content.
    """

    template_name = 'core/terms-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top_rated_courses'] = Course.top_rated_courses(limit=4)

        return context


def custom_bad_request_view(request, exception):
    return render(request, 'core/400.html', {'exception': exception}, status=400)


def custom_forbidden_view(request, exception):
    return render(request, 'core/403.html', {'exception': exception}, status=403)


def custom_404_view(request, exception):
    return render(request, 'core/404.html', {'exception': exception}, status=404)


def custom_500_view(request):
    return render(request, 'core/500.html', status=500)
