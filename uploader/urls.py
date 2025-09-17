from django.urls import path
from . import views

app_name = "uploader"

urlpatterns = [
    path("", views.uploader, name="uploader")
]
