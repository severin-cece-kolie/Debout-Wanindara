from django.urls import path
from . import views

app_name = 'action'

urlpatterns = [
    path('', views.action, name='action')
]
