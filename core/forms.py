from django import forms

from .models import CustomUser, Language, UserProfile


class LanguageForm(forms.ModelForm):
    languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = ['languages']


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=True,
        strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search...',
            'minlength': 1
        }),
        help_text="Enter keywords related to what you're looking for."
    )

    def clean_query(self):
        query = self.cleaned_data.get('query')
        if not query.strip():
            raise forms.ValidationError("Search query cannot be empty or just whitespace.")
        return query


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', ]

        help_texts = {
            'username': 'Enter your desired username.',
            'email': 'We will send a confirmation to this email address.',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # def clean_username(self):
    #     username = self.cleaned_data.get('username')
    #     if CustomUser.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
    #         raise forms.ValidationError("This username is already taken.")
    #     return username


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'education', 'nationality', 'bio', 'languages', 'image',
                  'age_visible', 'education_visible', 'article_visible', 'course_visible', ]

    widgets = {
        'languages': forms.CheckboxSelectMultiple()
    }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 4 * 1024 * 1024:  # Limit to 4MB
            raise forms.ValidationError("Image file too large (max 4MB).")
        return image

    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        if len(bio) > 950:
            raise forms.ValidationError("Bio cannot exceed 900 characters.")
        return bio

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and (age < 7 or age > 90):
            raise forms.ValidationError("Age must be between 7 and 90.")
        return age

    def clean_nationality(self):
        nationality = self.cleaned_data.get('nationality')
        if nationality and len(nationality) > 200:
            raise forms.ValidationError("Nationality cannot exceed 100 characters.")
        return nationality

    def clean_education(self):
        education = self.cleaned_data.get('education')
        if education and len(education) > 400:
            raise forms.ValidationError("Education details cannot exceed 300 characters.")
        return education

    def clean_languages(self):
        languages = self.cleaned_data.get('languages')
        if languages is None:
            raise forms.ValidationError("Please select a valid language.")
        return languages
