from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import UploadFile


@login_required
def uploader(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        if uploaded_file:
            max_size_bytes = request.user.max_file_size()
            if uploaded_file.size > max_size_bytes:
                messages.error(
                    request,
                    f"Файл превышает допустимый размер {max_size_bytes // (1024*1024)} МБ",
                )
                return redirect("uploader:uploader")
            obj = UploadFile(user=request.user, file=uploaded_file)
            obj.save()
            messages.success(request, "Файл успешно загружен!")
            return redirect("uploader:uploader")
        messages.error(request, "Вы не выбрали файл!")
    files = UploadFile.objects.filter(user=request.user).order_by("-uploaded_at")
    return render(request, "uploader/uploader.html", {"files": files})


@login_required
def all_file_details(request):
    files = UploadFile.objects.filter(user=request.user).order_by("-uploaded_at")
    return render(request, "uploader/all_file_details.html", {"files": files})


@login_required
def file_detail(request, slug):
    file = get_object_or_404(UploadFile, slug=slug)
    return render(request, "uploader/file_detail.html", {"file": file})


@login_required
def file_download(request, slug):
    file = get_object_or_404(UploadFile, slug=slug)
    if (
        not file.file
        or not file.file.path
        or not file.file.storage.exists(file.file.name)
    ):
        raise Http404("Файл не найден!")
    response = FileResponse(open(file.file.path, "rb"))
    response["Content-Disposition"] = f'attachment; filename="{file.original_name}"'
    return response


@login_required
@require_http_methods(["POST"])
def file_delete(request, slug):
    file = get_object_or_404(UploadFile, slug=slug, user=request.user)
    file.file.delete(save=False)
    file.delete()
    return redirect("uploader:uploader")


@login_required
@require_http_methods(["POST"])
def all_file_details_delete(request, slug):
    file = get_object_or_404(UploadFile, slug=slug, user=request.user)
    file.file.delete(save=False)
    file.delete()
    return redirect("uploader:all_file_details")
