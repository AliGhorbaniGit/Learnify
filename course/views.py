from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.views import generic
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg

from ticket.models import Ticket
from core.models import UserProfile
from .models import Course, CourseVideo, Category, CourseAdditionRequest, CourseComment, CourseRate, Tag, Teacher
from .forms import CourseAdditionRequestForm, AddCourseForm, CourseVideoForm, CourseCommentForm, CourseRatingForm


class CourseList(generic.ListView):
    """
    A view that displays a paginated list of published courses.

    This view retrieves courses from the database where the
    status is 'a' (active) and allows users to navigate
    through the courses with pagination.

    Context:
        courses: A list of active courses.
        categories: A list of all  categories.
        top_rated_articles: A list of the top-rated articles.
        top_rated_courses: A list of top-rated courses.

    Pagination:
        The view will paginate results, showing a fixed number
        of courses per page (defined by `paginate_by`).
    """
    template_name = 'course/course-list.html'
    model = Course
    context_object_name = 'courses'
    paginate_by = 4

    http_method_names = ['get']

    def get_queryset(self):
        return Course.objects.filter(status='a').select_related('teacher__user')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context['top_rated_courses'] = Course.top_rated_courses(limit=4)
        return context


class CourseDetail(generic.DetailView):
    """
    A view that displays detailed information about a specific course,
    including comments, ratings, and related course.

    Attributes:
        model (course): The model associated with this view.
        template_name (str): The template to render for this view.
        form_class : The form class used for submitting comments.

    Methods:
        get_queryset(): Returns the queryset including the teacher's user profile for related objects.
        post(request, *args, **kwargs): Handles POST requests for submitting comments and ratings.
        handle_comment_form(request): Processes the comment submission form.
        handle_rating_form(request): Processes the rating submission form.
    """
    model = Course
    template_name = 'course/course-detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        return super().get_queryset().select_related('teacher__user__profile').prefetch_related('videos')

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["categories"] = Category.objects.all()

        # Get the top-rated courses
        context['top_rated_courses'] = Course.top_rated_courses(limit=3)

        # Get approved comments for the course ordered by submission date
        context['comments'] = CourseComment.objects.filter(course=self.object, status='a'). \
            select_related('user__profile')

        # Calculate the average rating for the current course
        context['average_rating'] = CourseRate.objects.filter(course=self.object).aggregate(Avg('score'))[
                                        'score__avg'] or 0
        # Get the user's rating for the course, if authenticated
        context['user_rating'] = self.object.ratings.filter(
            user=self.request.user).first() if self.request.user.is_authenticated else None

        # Retrieve categories of the current course to find similar courses
        current_course_categories = self.object.category.all()

        # Find similar courses by category, excluding the current course, and limit to 3
        similar_courses = Course.objects.filter(category__in=current_course_categories).exclude(
            id=self.object.id).distinct()[:3].select_related('teacher__user')
        # similar articles
        context['similar_courses'] = similar_courses
        # comment form
        context['comment_form'] = CourseCommentForm()

        # rating form
        context['rating_form'] = CourseRatingForm()

        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if 'comment_form' in request.POST:
            comment_form = CourseCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.course = self.object
                comment.user = request.user
                comment.save()
                messages.success(request,
                                 'Success! Your comment has been submitted and is awaiting approval. '
                                 'We appreciate your contributions!')
                return redirect('course:course-detail', slug=self.object.slug)
            else:
                messages.error(request,
                               'Oops! There was an issue with your comment submission.  '
                               'Please correct the following errors: ' + ', '.join(
                                   list(comment_form.errors.values())[0]))

        elif 'rating_form' in request.POST:
            rating_form = CourseRatingForm(request.POST)
            if rating_form.is_valid():
                if not CourseRate.objects.filter(course=self.object, user=request.user).exists():
                    CourseRate.objects.create(
                        course=self.object,
                        user=request.user,
                        score=rating_form.cleaned_data['score']
                    )
                    messages.success(request, 'Great! Your rating has been recorded. We appreciate your feedback!')
                    return redirect('course:course-detail', slug=self.object.slug)
            else:
                messages.error(request,
                               'Something went wrong with your submission. '
                               'Please correct the following errors: ' + ', '.join(
                                   list(rating_form.errors.values())[0]))
        else:
            messages.error(request, 'Your submission was not successful. Please fill in all fields correctly.')

        context['comment_form'] = CourseCommentForm(request.POST)
        context['rating_form'] = CourseRatingForm(request.POST)
        return self.render_to_response(context)


class CourseAdditionRequestView(LoginRequiredMixin, generic.CreateView):
    """
    View for creating a Course Addition Request.
    Requires the user to be logged in to access this view.
    """
    model = CourseAdditionRequest  #
    form_class = CourseAdditionRequestForm
    template_name = 'course/add-course-request.html'

    def form_valid(self, form):
        """
        associate the current user with the CourseAdditionRequest before saving it.
        also display a success message after the request is successfully created.
        """
        form.instance.user = self.request.user  # Assign the logged-in user to the request instance
        ticket = Ticket.objects.create(title='Application to Add a Course',
                                       description='I would like to add my course. Please review my request in the '
                                                   'Teach Requests section and provide feedback.',
                                       user=self.request.user, )
        response = super().form_valid(form)  # Save the request object and call the parent class's form_valid method

        # Display a success message to inform the user that their request was submitted
        messages.success(self.request, 'Thank you ! '
                                       'Weve received it and will review it promptly. Expect feedback shortly')

        return response  # Return the response object to redirect or render appropriately

    def form_invalid(self, form):
        messages.warning(self.request,
                         'We encountered an error with your submission. '
                         'Kindly check the form for any inaccuracies and resubmit')
        return super().form_invalid(form)

    # def get_success_url(self):
    #     return self.request.path

    def get_success_url(self):
        return reverse('core:profile')


class AddCourse(LoginRequiredMixin, generic.CreateView):
    """
    View for adding a new course. Only accessible to logged-in users as teachers.
    """
    model = Course
    form_class = AddCourseForm
    template_name = 'course/add-course.html'

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is a teacher
        if not request.user.profile.is_teacher:
            messages.warning(request, 'You do not have permission to add courses.')
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = UserProfile.objects.get(user=self.request.user)
        return context

    def form_valid(self, form):
        """
        If the form is valid, associate the current user with the course
        and display a success message.
        """

        # Get or create a Teacher instance for the logged-in user
        teacher, created = Teacher.objects.get_or_create(user=self.request.user)

        # Set the teacher instance to the form's instance
        form.instance.teacher = teacher

        response = super().form_valid(form)

        # Display a success message upon successful submission
        messages.success(self.request, 'Great job! Your course has been submitted. Now you can add your videos to '
                                       'this course using the "Add Videos To Your Course" form available in the menu.')

        return response

    def form_invalid(self, form):
        """
        If the form is invalid, display an error message to the user.
        This enhances user feedback regarding submission issues.
        """
        messages.warning(self.request, 'We encountered an issue with your course submission. '
                                       'Kindly review the highlighted areas and correct any errors.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('core:profile')  # Ensure to return the correct URL for redirection')


class AddVideo(LoginRequiredMixin, generic.CreateView):
    """View to add a video to a course, requiring user authentication."""

    model = CourseVideo
    form_class = CourseVideoForm
    template_name = 'course/course-video-form.html'

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is a teacher
        if not request.user.profile.is_teacher:
            messages.warning(request, 'You do not have permission to add courses.')
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            # Check if the Teacher object exists for the current user
            teacher = Teacher.objects.get(user=self.request.user)

            messages.info(request,
                          "Please select a course you’ve created and fill out the form to upload your video. "
                          "After submitting, you can add more videos or return to your profile "
                          "to review your course details. (The submission may take some time, "
                          "so please be patient while the message is displayed to you. )"
                          )

            return super().get(request, *args, **kwargs)  # Call the parent method to render the form

        except Teacher.DoesNotExist:
            messages.warning(request, 'Please add your course title before proceeding. '
                                      'This will help us organize your content effectively!')
            return redirect('core:profile')

    def get_context_data(self, **kwargs):
        """Add additional context data to the template, including user-specific courses."""
        context = super().get_context_data(**kwargs)
        context['profile'] = UserProfile.objects.get(user=self.request.user)
        return context

    def get_form(self, form_class=None):
        """Customize the form to restrict courses to the user's own courses."""
        form = super().get_form(form_class)
        # Set the queryset for the 'course' field to user-specific courses
        form.fields['course'].queryset = Course.objects.filter(teacher=self.request.user.teacher_profile)
        return form

    def form_valid(self, form):
        """Process the form when it is valid."""
        course = form.cleaned_data['course']  # Get the selected course from the form
        # Check if the user has permission to add videos to the selected course
        if course.teacher != self.request.user.teacher_profile:
            # Ensure the course belongs to the currently logged-in user
            messages.error(self.request, "You do not have permission to add videos to this course.")
            return redirect('course:add-video')  # Redirect to another view if permission is denied

        response = super().form_valid(form)  # Call the parent method to save the form data
        messages.success(self.request, 'Video uploaded successfully! ')
        return response

    def get_success_url(self):
        """Define where to redirect after successfully adding a video."""
        return reverse('course:add-video')
