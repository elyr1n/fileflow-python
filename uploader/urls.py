from django.urls import path
from . import views

app_name = "uploader"

urlpatterns = [
    path("", views.uploader, name="uploader"),
    path("file/all", views.all_file_details, name="all_file_details"),
    path("file/<slug:slug>/", views.file_detail, name="file_detail"),
    path("file/<slug:slug>/download/", views.file_download, name="file_download"),
    path("file/<slug:slug>/delete/", views.file_delete, name="file_delete"),
]