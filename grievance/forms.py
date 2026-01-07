from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Grievance, Feedback, Attachment

# =========================
# CUSTOM SIGNUP FORM
# =========================
class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Standard UserCreationForm fields + our required email
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap styling to all fields automatically
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email address already in use.")
        return email

# =========================
# GRIEVANCE FORM
# =========================
class GrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['category', 'title', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a short title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your grievance clearly...'
            })
        }

# =========================
# FEEDBACK FORM
# =========================
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your experience...'
            })
        }

# =========================
# ATTACHMENT FORM
# =========================
class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }