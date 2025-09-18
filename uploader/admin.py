from django.contrib import admin
from .models import UploadFile


@admin.register(UploadFile)
class UploadFileAdmin(admin.ModelAdmin):
    list_display = ("original_name", "human_size_display", "extension", "uploaded_at", "slug")
    list_filter = ("extension", "uploaded_at")
    search_fields = ("original_name", "slug")
    readonly_fields = ("uploaded_at", "size", "content_type", "extension", "slug")

    fieldsets = (
        (None, {
            "fields": ("file", "original_name", "slug")
        }),
        ("Информация о файле", {
            "fields": ("size", "human_size_display", "extension", "content_type", "uploaded_at"),
        }),
    )

    def human_size_display(self, obj):
        return obj.human_size()
    human_size_display.short_description = "Размер"