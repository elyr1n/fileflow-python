from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, CustomAuthenticationForm
from django.utils.translation import gettext_lazy as _


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request, _("Вы успешно зарегистрировались и вошли в систему.")
                )
            return redirect("uploader:uploader")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(
                request, _("Вы вошли как %(username)s") % {"username": user.username}
            )
            return redirect("uploader:uploader")
    else:
        form = CustomAuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, _("Вы вышли из системы."))
    return redirect("accounts:login")


@login_required
def profile(request):
    return render(request, "accounts/profile.html", {"user": request.user})
