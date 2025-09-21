import os
import shortuuid
import mimetypes

from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse


MIME_CATEGORIES = {
    "image": "Изображение",
    "text": "Документ",
    "application/pdf": "PDF-документ",
    "application/msword": "Документ Word",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Документ Word",
    "application/vnd.ms-excel": "Таблица Excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Таблица Excel",
    "application/vnd.ms-powerpoint": "Презентация PowerPoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "Презентация PowerPoint",
    "application/zip": "Архив ZIP",
    "application/x-rar-compressed": "Архив RAR",
    "application/x-msdownload": "Исполняемый файл Windows",
    "application/x-iso9660-image": "ISO-образ",
    "audio": "Аудио",
    "video": "Видео",
}

EXTENSION_CATEGORIES = {
    "exe": "Исполняемый файл",
    "msi": "Инсталлятор",
    "iso": "ISO-образ",
    "txt": "Текстовый документ",
    "md": "Текстовый документ",
    "csv": "Таблица/CSV",
    "json": "JSON",
    "xml": "XML",
    "jpg": "Изображение",
    "jpeg": "Изображение",
    "png": "Изображение",
    "gif": "Изображение",
    "pdf": "PDF-документ",
    "doc": "Документ Word",
    "docx": "Документ Word",
    "xls": "Таблица Excel",
    "xlsx": "Таблица Excel",
    "ppt": "Презентация",
    "pptx": "Презентация",
    "zip": "Архив ZIP",
    "rar": "Архив RAR",
    "mp3": "Аудио",
    "wav": "Аудио",
    "mp4": "Видео",
    "mov": "Видео",
}


def validate_file_size_512mb(file):
    if not file:
        return
    size = getattr(file, "size", None)
    if size and size > 512 * 1024 * 1024:
        raise ValidationError("Максимальный размер файла — 512 МБ")


class UploadFile(models.Model):
    file = models.FileField(
        upload_to="uploads/%Y/%m/%d/",
        verbose_name="Файл",
        validators=[validate_file_size_512mb],
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
            filename = getattr(self.file, "name", "") or ""
            self.extension = os.path.splitext(filename)[1].lower().lstrip(".")
            content_type_from_file = getattr(self.file, "content_type", None)
            if content_type_from_file:
                self.content_type = content_type_from_file
            else:
                guessed, _ = mimetypes.guess_type(filename)
                self.content_type = guessed or "application/octet-stream"
        super().save(*args, **kwargs)

    def get_download_url(self):
        return reverse("uploader:file_download", args=[self.slug])

    def get_view_url(self):
        return reverse("uploader:file_detail", args=[self.slug])

    @property
    def human_size(self):
        if not self.size:
            return "-"
        size = float(self.size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    @property
    def file_category(self):
        if not self.content_type:
            ext = (self.extension or "").lower()
            return EXTENSION_CATEGORIES.get(ext, "Файл")
        if self.content_type in MIME_CATEGORIES:
            return MIME_CATEGORIES[self.content_type]
        if self.content_type.startswith("image/"):
            return "Изображение"
        if self.content_type.startswith("text/"):
            return "Документ"
        if self.content_type.startswith("audio/"):
            return "Аудио"
        if self.content_type.startswith("video/"):
            return "Видео"
        ext = (self.extension or "").lower()
        return EXTENSION_CATEGORIES.get(ext, "Файл")

    @property
    def is_image(self):
        return bool(self.content_type and self.content_type.startswith("image/"))

    @property
    def is_pdf(self):
        return self.content_type == "application/pdf"

    @property
    def is_text(self):
        return bool(self.content_type and self.content_type.startswith("text/"))

    @property
    def is_previewable(self):
        return self.is_image or self.is_pdf or self.is_text
