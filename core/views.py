from django.shortcuts import render
from .models import GalleryPhoto


def about(request):
    return render(request, 'pages/about.html')


