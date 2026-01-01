from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Grievance, Feedback, Attachment


# =========================
# CUSTOM SIGNUP FORM (WITH EMAIL)
# =========================
class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    usernamme = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email address already in use.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    


# =========================
# GRIEVANCE FORM
# =========================
class GrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['category', 'title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
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
                'min': 1,
                'max': 5
            }),
            'comment': forms.Textarea(attrs={
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
