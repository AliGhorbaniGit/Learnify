from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from .models import Article, ArticleComment, ArticleRate


class ArticleCommentForm(forms.ModelForm):
    class Meta:
        model = ArticleComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Leave a comment...',
                'rows': 4,
                'cols': 40,
                'class': 'form-control p-3',  # using Bootstrap
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


class AddArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'image', 'intro_txt', 'description',
                  'slug']
        widgets = {
            'category': forms.CheckboxSelectMultiple(),
            'tag': forms.CheckboxSelectMultiple(),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')

        if not title:
            raise forms.ValidationError("This field cannot be empty.")
        if len(title) < 5:
            raise forms.ValidationError("title must be at least 5 characters long.")

        return title

    def clean_intro_txt(self):
        intro_txt = self.cleaned_data.get('intro_txt')

        if not intro_txt:
            raise forms.ValidationError("This field cannot be empty.")
        if len(intro_txt) < 5:
            raise forms.ValidationError("Comment must be at least 5 characters long.")

        return intro_txt

    def clean_description(self):
        description = self.cleaned_data.get('description')

        if not description:
            raise forms.ValidationError("This field cannot be empty.")
        if len(description) < 100:
            raise forms.ValidationError("description must be at least 100 characters long.")

        return description

    def clean_image(self):
        """Validate the uploaded image to ensure it meets size and type requirements."""
        image = self.cleaned_data.get('image')

        # Check if the image is present and limit file size to 5MB
        if image and image.size > 5 * 1024 * 1024:  # 5 MB
            raise ValidationError(_('Image file too large ( > 2MB )'))

            # Check for valid mime types for the image
        valid_image_types = ['image/jpeg', 'image/png', 'image/gif']
        if image and image.content_type not in valid_image_types:
            raise ValidationError(_('Unsupported file type. Please upload a JPEG, PNG, or GIF image.'))

        return image

    def clean_slug(self):
        """Validate the slug to ensure it's not empty."""
        slug = self.cleaned_data.get('slug')

        # Ensure the slug is not empty
        if not slug:
            raise ValidationError(_('This field cannot be empty.'))

        return slug

    def save(self, commit=True):
        """Override the save method to automatically generate a slug from the title if not provided."""
        article = super().save(commit=False)

        if not article.slug:
            article.slug = slugify(article.title)

        if commit:
            article.save()

        return article  # Return the article instance


class ArticleRatingForm(forms.ModelForm):
    class Meta:
        model = ArticleRate
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }

    def clean_score(self):
        score = self.cleaned_data.get('score')
        if score is None or not (1 <= score <= 5):
            raise forms.ValidationError("Please provide a rating between 1 and 5.")
        return score
