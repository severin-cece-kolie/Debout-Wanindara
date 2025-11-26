"""
Commande Django pour tester la connexion email
Usage: python manage.py test_email
"""
from django.core.management.base import BaseCommand
from core.email_utils import test_email_connection, send_email_direct_smtp
from core.email_diagnostic import test_smtp_connection_detailed
from django.conf import settings


class Command(BaseCommand):
    help = 'Teste la connexion email SMTP avec diagnostic complet'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Lancer un diagnostic détaillé complet',
        )

    def handle(self, *args, **options):
        if options['detailed']:
            # Diagnostic détaillé
            test_smtp_connection_detailed()
        else:
            # Test rapide
            self.stdout.write("=" * 60)
            self.stdout.write(self.style.SUCCESS("TEST DE CONNEXION EMAIL"))
            self.stdout.write("=" * 60)
            
            # Afficher la configuration
            self.stdout.write(f"\n📧 Configuration actuelle:")
            self.stdout.write(f"   Serveur: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
            self.stdout.write(f"   Utilisateur: {settings.EMAIL_HOST_USER}")
            self.stdout.write(f"   TLS: {settings.EMAIL_USE_TLS}")
            self.stdout.write(f"   SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
            self.stdout.write(f"   Mot de passe configuré: {'✅ Oui' if settings.EMAIL_HOST_PASSWORD else '❌ Non'}")
            
            # Test de connexion
            self.stdout.write(f"\n🔍 Test de connexion...")
            success, message = test_email_connection()
            
            if success:
                self.stdout.write(self.style.SUCCESS(f"\n✅ {message}"))
            else:
                self.stdout.write(self.style.ERROR(f"\n❌ {message}"))
            
            # Test d'envoi direct
            if settings.EMAIL_HOST_PASSWORD:
                self.stdout.write(f"\n📤 Test d'envoi direct SMTP...")
                test_success, test_msg = send_email_direct_smtp(
                    subject="Test Email - Debout Wanindara",
                    message="Ceci est un email de test pour vérifier la configuration SMTP.",
                    recipient_list=[settings.EMAIL_HOST_USER],
                    from_email=settings.EMAIL_HOST_USER
                )
                
                if test_success:
                    self.stdout.write(self.style.SUCCESS(f"✅ Email de test envoyé avec succès!"))
                else:
                    self.stdout.write(self.style.ERROR(f"❌ Échec envoi: {test_msg}"))
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("\n💡 Pour un diagnostic détaillé, utilisez: python manage.py test_email --detailed")

