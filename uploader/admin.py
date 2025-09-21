from django.contrib import admin
from django.utils.html import format_html
from .models import UploadFile


@admin.register(UploadFile)
class UploadFileAdmin(admin.ModelAdmin):
    list_display = [
        "original_name",
        "file_category_display",
        "human_size_display",
        "uploaded_at",
        "download_link",
    ]
    list_filter = ["content_type", "uploaded_at", "extension"]
    search_fields = ["original_name", "slug", "content_type"]
    readonly_fields = [
        "slug",
        "size",
        "content_type",
        "extension",
        "uploaded_at",
        "human_size_display",
        "file_category_display",
        "preview_link",
    ]
    fieldsets = (
        ("Основная информация", {"fields": ("file", "original_name")}),
        (
            "Техническая информация",
            {
                "fields": (
                    "slug",
                    "size",
                    "human_size_display",
                    "content_type",
                    "extension",
                    "file_category_display",
                    "uploaded_at",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Предпросмотр", {"fields": ("preview_link",), "classes": ("collapse",)}),
    )

    def human_size_display(self, obj):
        return obj.human_size

    human_size_display.short_description = "Размер"

    def file_category_display(self, obj):
        return obj.file_category

    file_category_display.short_description = "Тип файла"

    def download_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank">Скачать</a>', obj.get_download_url()
        )

    download_link.short_description = "Ссылка"

    def preview_link(self, obj):
        if obj.is_previewable:
            return format_html(
                '<a href="{}" target="_blank">Просмотреть</a>', obj.get_view_url()
            )
        return "Недоступно"

    preview_link.short_description = "Предпросмотр"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
