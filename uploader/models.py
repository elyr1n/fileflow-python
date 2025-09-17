import uuid
from django.db import models

# Create your models here.
class UploadFile(models.Model):
    file = models.FileField(upload_to="uploads/%Y/%m/%d/", verbose_name="Файл")
    original_name_file = models.CharField(max_length=255, verbose_name="Имя файла", blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL", blank=True)

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.original_name_file} ({self.uploaded_at})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())

        if not self.original_name_file and self.file:
            self.original_name_file = self.file.name

        super().save(*args, **kwargs)