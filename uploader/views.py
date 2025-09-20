from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from django.views.decorators.http import require_http_methods
from .models import UploadFile

def uploader(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        if uploaded_file:
            max_size_bytes = 512 * 1024 ** 2
            if uploaded_file.size > max_size_bytes:
                messages.error(request, "Файл превышает допустимый размер 512 МБ")
                return redirect("uploader:uploader")

            obj = UploadFile(file=uploaded_file)
            obj.save()
            messages.success(request, "Файл успешно загружен!")
            return redirect("uploader:uploader")
        messages.error(request, "Вы не выбрали файл!")

    files = UploadFile.objects.all()
    return render(request, "uploader/uploader.html", {"files": files})


def file_detail(request, slug):
    file = get_object_or_404(UploadFile, slug=slug)
    return render(request, "uploader/file_detail.html", {"file": file})


def file_download(request, slug):
    file = get_object_or_404(UploadFile, slug=slug)
    if not file.file or not file.file.path or not file.file.storage.exists(file.file.name):
        raise Http404("Файл не найден!")
    response = FileResponse(open(file.file.path, "rb"))
    response["Content-Disposition"] = f'attachment; filename="{file.original_name}"'
    return response


@require_http_methods(["POST"])
def file_delete(request, slug):
    file = get_object_or_404(UploadFile, slug=slug)
    file.file.delete(save=False)
    file.delete()
    return redirect("uploader:uploader")

@require_http_methods(["POST"])
def all_file_details_delete(request, slug):
    file = get_object_or_404(UploadFile, slug=slug)
    file.file.delete(save=False)
    file.delete()
    return redirect("uploader:all_file_details")

def all_file_details(request):
    files = UploadFile.objects.all()
    return render(request, "uploader/all_file_details.html", {"files": files})