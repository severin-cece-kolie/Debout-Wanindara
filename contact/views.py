from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from core.email_utils import send_email_robust
from .models import ContactMessage
import logging
import os

logger = logging.getLogger(__name__)

def contact_view(request):
    return render(request, "contact/contact.html")

def submit_contact(request):
    if request.method == "POST":
        try:
            # Récupération des données
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            subject = request.POST.get('subject', '').strip()
            message_content = request.POST.get('message', '').strip()
            
            print(f"📨 Formulaire reçu: {name} - {email} - {subject}")
            
            # Validation
            if not all([name, email, subject, message_content]):
                return JsonResponse({
                    'success': False,
                    'message': 'Veuillez remplir tous les champs obligatoires.'
                })
            
            # Sauvegarde en base
            contact_msg = ContactMessage.objects.create(
                name=name, email=email, phone=phone,
                subject=subject, message=message_content
            )
            print("✅ Message sauvegardé en base de données")
            
            # Vérifier la configuration email
            email_configured = (
                hasattr(settings, 'EMAIL_HOST_PASSWORD') and 
                settings.EMAIL_HOST_PASSWORD and
                settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend'
            )
            
            # Envoi des emails - PRIORITÉ À L'EMAIL DE CONFIRMATION
            email_results = {'admin': False, 'user': False}
            email_errors = []
            
            # IMPORTANT: Envoyer d'abord l'email de confirmation à l'utilisateur
            # Email de confirmation à l'expéditeur - TOUJOURS ENVOYÉ
            user_subject = "✅ Confirmation de réception - Debout Wanindara"
            user_body = f"""Bonjour {name},

Nous accusons réception de votre message et vous en remercions.

📋 Récapitulatif de votre demande :
• Sujet: {subject}
• Date: {timezone.now().strftime('%d/%m/%Y à %H:%M')}
• Référence: #{contact_msg.id}

Notre équipe traite votre demande dans les plus brefs délais et vous répondra très rapidement.

Pour toute question urgente, vous pouvez nous contacter :
📞 +224 629829087
📧 deboutwanindara@gmail.com

Cordialement,
L'équipe Debout Wanindara

---
Ceci est un message automatique, merci de ne pas y répondre."""
            
            success, error_msg = send_email_robust(
                user_subject,
                user_body.strip(),
                [email],
                max_retries=2
            )
            
            if success:
                email_results['user'] = True
                print(f"✅ Email CONFIRMATION envoyé avec succès à {email}")
            else:
                print(f"❌ Erreur envoi email confirmation: {error_msg}")
                logger.error(f"Erreur envoi email confirmation: {error_msg}")
                email_errors.append("confirmation")
            
            # Ensuite, envoyer l'email à l'administration
            admin_subject = f"📧 Nouveau message: {subject}"
            admin_body = f"""Nouveau message de contact reçu :

👤 Nom: {name}
📧 Email: {email}
📞 Téléphone: {phone or 'Non renseigné'}
🎯 Sujet: {subject}
📅 Reçu le: {timezone.now().strftime('%d/%m/%Y à %H:%M')}

💬 Message:
{message_content}

---
ID Message: #{contact_msg.id}
Debout Wanindara - Formulaire de contact"""
            
            success, error_msg = send_email_robust(
                admin_subject,
                admin_body.strip(),
                ['deboutwanindara@gmail.com'],
                max_retries=2
            )
            
            if success:
                email_results['admin'] = True
                print(f"✅ Email ADMIN envoyé avec succès à deboutwanindara@gmail.com")
            else:
                print(f"❌ Erreur envoi email admin: {error_msg}")
                logger.error(f"Erreur envoi email admin: {error_msg}")
                email_errors.append("admin")
            
            # Message de succès - priorité à la confirmation
            if email_results['user']:
                success_message = '✅ Votre message a été envoyé avec succès! Vous recevrez une confirmation par email sous peu.'
            elif email_results['admin']:
                success_message = '✅ Votre message a été reçu! Notre équipe vous contactera rapidement.'
            else:
                success_message = '⚠️ Votre message a été enregistré. Notre équipe vous contactera prochainement.'
                
            if email_errors and email_configured:
                logger.warning(f"Emails non envoyés malgré la configuration: {email_errors}")
            
            return JsonResponse({
                'success': True,
                'message': success_message,
                'mode': 'production' if email_configured else 'development',
                'emails_sent': {
                    'admin': email_results['admin'],
                    'confirmation': email_results['user']
                }
            })
                
        except Exception as e:
            print(f"❌ Erreur générale: {e}")
            logger.error(f"Erreur générale contact: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Une erreur est survenue. Veuillez réessayer.'
            })
    
    return JsonResponse({
        'success': False, 
        'message': 'Méthode non autorisée.'
    })

def donate(request):
    """Page de donation"""
    return render(request, "contact/donate.html")