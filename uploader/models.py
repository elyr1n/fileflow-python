import os
import shortuuid
import mimetypes
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse


def file_size_validator(max_size_mb=512):
    max_bytes = max_size_mb * 1024 ** 2

    def validator(file):
        if file and hasattr(file, "size") and file.size > max_bytes:
            raise ValidationError(f"Максимальный размер файла {max_size_mb} МБ")
    return validator



class UploadFile(models.Model):
    file = models.FileField(
        upload_to="uploads/%Y/%m/%d/",
        verbose_name="Файл",
        validators=[file_size_validator(512)],
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
        if self.file and hasattr(self.file, "size") and self.file.size > 512 * 1024 ** 2:
            raise ValidationError("Файл превышает допустимый размер 512 МБ")

        if not self.slug:
            self.slug = shortuuid.uuid()

        if self.file and not self.original_name:
            self.original_name = os.path.basename(self.file.name)

        if self.file:
            self.size = getattr(self.file, "size", None)
            self.extension = os.path.splitext(self.file.name)[1].lower().lstrip(".")
            if hasattr(self.file, "content_type"):
                self.content_type = self.file.content_type
            else:
                self.content_type, _ = mimetypes.guess_type(self.file.name)
                if not self.content_type:
                    self.content_type = "application/octet-stream"

        super().save(*args, **kwargs)

    def get_download_url(self):
        return reverse("uploader:file_download", args=[self.slug])

    def get_view_url(self):
        return reverse("uploader:file_detail", args=[self.slug])

    def human_size(self):
        if not self.size:
            return "-"
        size = float(self.size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0

    # Свойства для превью
    @property
    def is_image(self):
        return self.content_type.startswith("image/")

    @property
    def is_pdf(self):
        return self.content_type == "application/pdf"

    @property
    def is_text(self):
        return self.content_type.startswith("text/")

    @property
    def is_previewable(self):
        return self.is_image or self.is_pdf or self.is_text