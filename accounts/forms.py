from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Ник-нейм",
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition",
            }
        ),
        error_messages={
            "required": "Пожалуйста, введите Ваш ник-нейм!",
            "max_length": "Слишком длинный ник-нейм, максимум 32 символа!",
        },
    )
    email = forms.EmailField(
        label="Почта",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition",
            }
        ),
        required=True,
        error_messages={
            "required": "Пожалуйста, введите Вашу почту!",
            "invalid": "Введите корректную почту!",
        },
    )
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition",
            }
        ),
        error_messages={"required": "Пожалуйста, введите пароль!"},
    )
    password2 = forms.CharField(
        label="Повтор пароля",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition",
            }
        ),
        error_messages={
            "required": "Пожалуйста, подтвердите пароль!",
            "password_mismatch": "Пароли не совпадают!",
        },
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с такой почтой уже существует!")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким ником уже существует!")
        return username


from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Почта или Ник-нейм",
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition",
            }
        ),
        error_messages={
            "required": "Введите почту или ник-нейм!",
        },
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition",
            }
        ),
        error_messages={
            "required": "Введите пароль!",
        },
    )

    error_messages = {
        "invalid_login": "Неверная почта/ник-нейм или пароль. Проверьте правильность введенных данных.",
    }

    class Meta:
        model = CustomUser
        fields = ("username", "password")
