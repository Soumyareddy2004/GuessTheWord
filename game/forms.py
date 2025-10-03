from django import forms
from django.contrib.auth.models import User
import re

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=5)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password", min_length=5)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 5:
            raise forms.ValidationError("Username must be at least 5 characters.")
        # require both upper and lower case letters
        if not (re.search(r'[a-z]', username) and re.search(r'[A-Z]', username)):
            raise forms.ValidationError("Username must include both uppercase and lowercase letters.")
        return username

    def clean_password(self):
        p = self.cleaned_data.get('password')
        if not re.search(r'[A-Za-z]', p):
            raise forms.ValidationError("Password must include letters.")
        if not re.search(r'\d', p):
            raise forms.ValidationError("Password must include at least one digit.")
        if not re.search(r'[$%*@]', p):
            raise forms.ValidationError("Password must include at least one of the special characters: $ % * @")
        return p

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            raise forms.ValidationError("Passwords do not match.")
