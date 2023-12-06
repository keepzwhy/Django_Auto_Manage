from app01 import models
from django import forms


class LogonModelForm(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['user_name', 'user_password', 'user_age', 'user_gender', 'user_depart', 'user_time']
        widgets = {
            'user_name': forms.TextInput(attrs={'class': 'form-control'}),
            'user_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'user_age': forms.TextInput(attrs={'class': 'form-control'}),
            'user_gender': forms.Select(attrs={'class': 'form-control'}),
            'user_depart': forms.Select(attrs={'class': 'form-control'}),
            'user_time': forms.DateTimeInput(attrs={'class': 'form-control', 'id': 'time'}),
        }
        # def __init__(self, *args, **kwargs):
        #     super.__init__(*args, **kwargs)
        #     for name, field in self.fields.items():
        #         field.widgets.attrs = {'class': "form-control"}


class EditModelForm(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['user_name', 'user_age', 'user_gender', 'user_depart', 'user_time']
        widgets = {
            'user_name': forms.TextInput(attrs={'class': 'form-control'}),

            'user_age': forms.TextInput(attrs={'class': 'form-control'}),
            'user_gender': forms.Select(attrs={'class': 'form-control'}),
            'user_depart': forms.Select(attrs={'class': 'form-control'}),
            'user_time': forms.DateTimeInput(attrs={'class': 'form-control', 'id': 'time'}),
        }


class LoginModelForm(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['user_name', 'user_password']
        widgets = {
            'user_name': forms.TextInput(attrs={'class': "input_box", 'placeholder': "用户名"}),
            'user_password': forms.PasswordInput(attrs={'class': "input_box", 'placeholder': "密码"}),
        }


class ChangePasswordForm(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['user_name', 'user_password']
        widgets = {
            'user_name': forms.TextInput(attrs={'class': 'form-control'}),
            'user_password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
