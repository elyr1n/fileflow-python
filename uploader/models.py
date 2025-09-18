import os
import shortuuid
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse


def validate_file_size(max_size_gb: int):
    def validator(value):
        if value.size > max_size_gb * 1024**3:
            raise ValidationError(f"Максимальный размер файла {max_size_gb} ГБ")
    return validator


class UploadFile(models.Model):
    file = models.FileField(
        upload_to="uploads/%Y/%m/%d/",
        verbose_name="Файл",
        validators=[validate_file_size(1)],
    )
    original_name = models.CharField("Имя файла", max_length=255, blank=True)
    uploaded_at = models.DateTimeField("Дата загрузки", auto_now_add=True)
    slug = models.SlugField("URL", max_length=255, unique=True, blank=True)

    size = models.BigIntegerField("Размер (байт)", null=True, blank=True)
    content_type = models.CharField("Тип содержимого", max_length=100, blank=True)
    extension = models.CharField("Расширение", max_length=20, blank=True)

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.original_name or "Без имени"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = shortuuid.uuid()

        if self.file and not self.original_name:
            self.original_name = os.path.basename(self.file.name)

        if self.file:
            self.size = getattr(self.file, "size", None)
            self.extension = os.path.splitext(self.file.name)[1].lower().lstrip(".")
            self.content_type = getattr(self.file, "content_type", "")

        super().save(*args, **kwargs)

    def get_download_url(self):
        return reverse("uploader:file_download", args=[self.slug])

    def get_view_url(self):
        return reverse("uploader:file_detail", args=[self.slug])

    def human_size(self):
        if not self.size:
            return "-"
        size = self.size
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

    @property
    def is_previewable(self):
        return (
            self.content_type.startswith("image/")
            or self.content_type.startswith("text/")
            or self.content_type == "application/pdf"
        )
