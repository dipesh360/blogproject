from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Profile

class SignUpForm(UserCreationForm):
	name = forms.CharField(label = ("Full Name"))
	username = forms.EmailField(label = ("Email"))

	class Meta:
		model = User
		fields = ('name', 'username', 'password1', 'password2')

class UserEditForm(forms.ModelForm):
    # user has no permission to change its Email so we have to attribute "readonly".
    username = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user',)
