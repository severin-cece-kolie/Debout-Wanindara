from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog, name='blog'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
