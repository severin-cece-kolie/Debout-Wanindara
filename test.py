import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'votre_projet.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

try:
    result = send_mail(
        'Test Email Configuration',
        'Ceci est un test de configuration email.',
        settings.DEFAULT_FROM_EMAIL,
        ['deboutwanindara@gmail.com'],
        fail_silently=False,
    )
    print(f"✅ Email envoyé avec succès! Résultat: {result}")
except Exception as e:
    print(f"❌ Erreur: {e}")