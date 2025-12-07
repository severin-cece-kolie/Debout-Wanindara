# join/urls.py
from django.urls import path
from . import views

app_name = 'join'

urlpatterns = [
    # Pages principales
    path('', views.join_view, name='join'),
    path('volunteer/', views.volunteer_view, name='volunteer'),
    path('submit/', views.submit_application, name='submit_application'),
    
    # Badge - Affichage et téléchargement
    path('badge/<int:membre_id>/', views.badge_view, name='badge_view'),
    path('badge/<int:membre_id>/pdf/', views.badge_pdf_view, name='badge_pdf'),
    path('badge/<int:membre_id>/png/', views.badge_png_view, name='badge_png'),
    path('badge/<int:membre_id>/qr/', views.badge_qr_view, name='badge_qr'),
    
    # Page de succès
    path('badge/<int:membre_id>/success/', views.badge_success_view, name='badge_success'),
    
    # Vérification du badge
    path('verify/<int:membre_id>/<str:signature>/', views.verify_badge, name='verify_badge'),
    
    # Admin - Liste des badges
    path('badges/', views.badge_list, name='badge_list'),
    
    # Galerie
    path('gallery/', views.gallery_view, name='gallery'),
]