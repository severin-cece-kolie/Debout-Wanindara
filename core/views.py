from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation
from django.urls import translate_url


def about(request):
    return render(request, 'pages/about.html')

