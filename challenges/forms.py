from django import forms
from django.contrib.auth.models import User


class MatchResultForm(forms.Form):
    winner = forms.ChoiceField(label='Sieger', choices=[], widget=forms.RadioSelect)
    score = forms.CharField(
        max_length=64, required=False, label='Ergebnis',
        help_text='z.B. "21-15, 21-18"',
        widget=forms.TextInput(attrs={'placeholder': '21-15, 21-18'}),
    )

    def __init__(self, challenge, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['winner'].choices = [
            (challenge.challenger.pk, challenge.challenger.get_full_name() or challenge.challenger.username),
            (challenge.challenged.pk, challenge.challenged.get_full_name() or challenge.challenged.username),
        ]
