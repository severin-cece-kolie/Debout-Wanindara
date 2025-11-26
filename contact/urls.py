from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path("", views.contact_view, name="contact"),
    path('submit/', views.submit_contact, name='submit_contact'),
    path('donate/', views.donate, name='donate'),
]