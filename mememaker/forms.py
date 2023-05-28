from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class MemeInput(forms.Form):
    words = forms.CharField(label='Enter Words', max_length=100)

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=16)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
'''
class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=16)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
'''
class RegistrationForm(UserCreationForm):
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password1')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('confirm_password',)
