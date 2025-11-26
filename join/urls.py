from django.urls import path
from . import views

app_name = 'join'

urlpatterns = [
    # Page principale - formulaire d'adhésion
    path('', views.join_view, name='join'),
    
    # Soumission du formulaire
    path('submit/', views.submit_application, name='submit'),
    
    # Bénévolat
    path('volunteer/', views.volunteer_view, name='volunteer'),
    
    # Liste des badges
    path('badges/', views.badge_list, name='badge_list'),
    
    # Vues pour les badges
    path('badge/<int:membre_id>/', views.badge_view, name='badge_view'),
    path('badge/<int:membre_id>/pdf/', views.badge_pdf_view, name='badge_pdf'),
    path('badge/<int:membre_id>/png/', views.badge_png_view, name='badge_png'),
    path('badge/<int:membre_id>/qr/', views.badge_qr_view, name='badge_qr'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('verify/<int:membre_id>/<str:signature>/', views.verify_badge, name='verify_badge'),
]
