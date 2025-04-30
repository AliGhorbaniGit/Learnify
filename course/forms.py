from django import forms
from django.core.exceptions import ValidationError

from .models import CourseAdditionRequest, Course, CourseVideo, CourseComment, CourseRate


class CourseCommentForm(forms.ModelForm):
    class Meta:
        model = CourseComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Add your comment here...',
                'rows': 4,
                'cols': 40,
                'class': 'form-control p-3',
            }),
        }
        help_texts = {
            'text': 'Keep your comment respectful and constructive.',
        }

    def clean_text(self):
        text = self.cleaned_data.get('text')

        if not text:
            raise forms.ValidationError("This field cannot be empty.")
        if len(text) < 5:
            raise forms.ValidationError("Comment must be at least 5 characters long.")

        return text


class CourseAdditionRequestForm(forms.ModelForm):
    class Meta:
        model = CourseAdditionRequest
        fields = ('title', 'description', 'video',)

    def clean_video(self):
        """
        Validate the uploaded video file.
        - Check that the file type is allowed.
        - Check that the file size does not exceed 100 MB.
        """
        video = self.cleaned_data.get('video')

        if video:
            allowed_extensions = ['.mp4', '.mov', '.avi']
            if not any(video.name.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError("Unsupported file type. Please upload a video file (mp4, mov, avi).")

            # Check file size (limit to 100MB)
            max_size = 100 * 1024 * 1024  # 100 MB in bytes
            if video.size > max_size:
                raise forms.ValidationError("File size exceeds the limit of 100MB.")

        return video

    def clean_title(self):
        """Validate the title field to ensure it is not empty."""
        title = self.cleaned_data.get('title')
        if not title or title.strip() == '':
            raise forms.ValidationError("Title cannot be empty.")
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long.")

        return title

    def clean_description(self):
        """Validate the description field to ensure it is not empty."""
        description = self.cleaned_data.get('description')
        if not description or description.strip() == '':
            raise forms.ValidationError("Description cannot be empty.")
        if len(description) < 5:
            raise forms.ValidationError("Description must be at least 5 characters long.")

        return description

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class AddCourseForm(forms.ModelForm):
    """
    Form for adding a new course. Uses Django's ModelForm to automatically
    handle form rendering and validation based on the Course model.
    """

    class Meta:
        model = Course
        fields = ['title', 'image', 'description', 'slug']

    def clean_slug(self):
        """
        Validate the slug field to ensure it is unique.
        Raises a ValidationError if the slug already exists in the database.
        """
        slug = self.cleaned_data.get('slug')
        if Course.objects.filter(slug=slug).exists():
            raise ValidationError("This slug is already taken. Please choose a different one.")
        return slug

    def clean_title(self):
        """Validate the title field to ensure it is not empty."""
        title = self.cleaned_data.get('title')
        if not title or title.strip() == '':
            raise forms.ValidationError("Title cannot be empty.")
        if len(title) < 10:
            raise forms.ValidationError("Title must be at least 10 characters long.")

        return title

    def clean_description(self):
        """Validate the title field to ensure it is not empty."""
        description = self.cleaned_data.get('description')
        if not description or description.strip() == '':
            raise forms.ValidationError("Description cannot be empty.")
        if len(description) < 50:
            raise forms.ValidationError("Description must be at least 50 characters long.")

        return description

    def clean_image(self):
        """
        Validate the uploaded image field for size and type.
        Raises ValidationError if the image size exceeds the limit or if the file type is unsupported.
        """
        image = self.cleaned_data.get('image')
        if image:
            # Check the file size (example: limit to 5MB)
            max_size = 5 * 1024 * 1024
            if image.size > max_size:
                raise ValidationError("Image file size exceeds the limit of 5MB.")

                # Check for valid image formats
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if not any(image.name.endswith(ext) for ext in valid_extensions):
                raise ValidationError(
                    "Unsupported file type. Please upload a JPG, PNG, or GIF image.")
        return image


class CourseVideoForm(forms.ModelForm):
    """Form for creating and updating CourseVideo instances."""

    class Meta:
        model = CourseVideo
        fields = ('course', 'title', 'video_file', 'description',)

    def clean_title(self):
        """Validate the title field to ensure it is not empty."""
        title = self.cleaned_data.get('title')
        if not title or title.strip() == '':
            raise forms.ValidationError("Title cannot be empty.")
        if len(title) < 15:
            raise forms.ValidationError("Title must be at least 15 characters long.")

        return title

    def clean_description(self):
        """Validate the title field to ensure it is not empty."""
        description = self.cleaned_data.get('description')
        if not description or description.strip() == '':
            raise forms.ValidationError("Description cannot be empty.")
        if len(description) < 50:
            raise forms.ValidationError("Description must be at least 50 characters long.")

        return description

    def clean_video_file(self):
        """Custom validation for the uploaded video file."""
        video_file = self.cleaned_data.get('video_file')

        if video_file:
            # Check file size (limit to 100 MB)
            if video_file.size > 1024 * 1024 * 100:  # 100 MB
                raise ValidationError("File size must be under 100 MB.")

                # Check file type (allow specific formats)
            valid_extensions = ('.mp4', '.avi', '.mov')  # Define allowed video formats
            if not video_file.name.endswith(valid_extensions):
                raise ValidationError("Unsupported file type. Please upload a video file in MP4, AVI, or MOV format.")

        return video_file


class CourseRatingForm(forms.ModelForm):
    class Meta:
        model = CourseRate
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }

    def clean_score(self):
        score = self.cleaned_data.get('score')
        if score is None or not (1 <= score <= 5):
            raise forms.ValidationError("Please provide a rating between 1 and 5.")
        return score
