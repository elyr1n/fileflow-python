from django.contrib import admin
from .models import UploadFile

# Register your models here.
@admin.register(UploadFile)
class UploadFileAdmin(admin.ModelAdmin):
    list_display = ("original_name_file", "uploaded_at", "slug")
    list_filter = ("uploaded_at",)
    search_fields = ("original_name_file", "slug")