from django.shortcuts import render

# Create your views here.
def uploader(request):
    return render(request, "uploader/uploader.html")