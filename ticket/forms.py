from django import forms

from .models import Ticket, TicketResponse


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', ]

    def clean_title(self):
        """Validate that the title is not empty."""
        title = self.cleaned_data.get('title')
        if not title or len(title) < 5:
            raise forms.ValidationError('Title must be at least 10 characters long.')
        return title

    def clean_description(self):
        """Validate that the description meets the criteria."""
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise forms.ValidationError(
                'Description must be at least 10 characters long.')  # Must be at least 10 characters
        return description


class TicketResponseForm(forms.ModelForm):
    class Meta:
        model = TicketResponse
        fields = ['response_text']
