from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)
    profile = models.ImageField(upload_to='profiles/', null=True, blank=True)

class UserForm(UserCreationForm):
    birthday = forms.DateField(label='Birthday', required=False)
    profile = forms.ImageField(label='Profile', required=False)

    class Meta:
        model = User
        fields= ['username', 'password1', 'password2', 'email']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('이미 사용중인 이메일입니다.')
        return email