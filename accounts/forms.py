from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PlayerProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='E-Mail-Adresse')
    first_name = forms.CharField(max_length=30, required=False, label='Vorname')
    last_name = forms.CharField(max_length=30, required=False, label='Nachname')
    gender = forms.ChoiceField(
        choices=PlayerProfile.GENDER_CHOICES,
        label='Geschlecht',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'gender', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            # Profile is created by signal; update gender
            user.profile.gender = self.cleaned_data['gender']
            user.profile.save(update_fields=['gender'])
        return user
