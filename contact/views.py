from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.core.mail import EmailMessage, send_mail
from .models import ContactMessage
import logging

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

            if not all([name, email, subject, message_content]):
                return JsonResponse({
                    'success': False,
                    'message': 'Veuillez remplir tous les champs obligatoires.'
                })

            # Sauvegarde en base
            contact_msg = ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message_content
            )

            # -------------------------
            # 1️⃣ EMAIL CONFIRMATION USER
            # -------------------------
            user_subject = "✅ Confirmation de réception - Debout Wanindara"

            user_body = f"""
Bonjour {name},

Nous accusons réception de votre message et vous en remercions.

📋 Récapitulatif :
• Sujet: {subject}
• Date: {timezone.now().strftime('%d/%m/%Y à %H:%M')}
• Référence: #{contact_msg.id}

Notre équipe vous répondra dans les plus brefs délais.

📞 +224 629829087
📧 deboutwanindara@gmail.com

Cordialement,
L'équipe Debout Wanindara
"""

            user_mail_sent = False
            admin_mail_sent = False

            try:
                send_mail(
                    subject=user_subject,
                    message=user_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                user_mail_sent = True
                print("✅ Email confirmation envoyé")
            except Exception as e:
                logger.error(f"Erreur email confirmation: {e}")

            # -------------------------
            # 2️⃣ EMAIL ADMINISTRATION
            # -------------------------
            admin_subject = f"Nouveau message - {subject}"

            admin_body = f"""
Nouveau message reçu :

👤 Nom: {name}
📧 Email: {email}
📞 Téléphone: {phone or 'Non renseigné'}
🎯 Sujet: {subject}
📅 Reçu le: {timezone.now().strftime('%d/%m/%Y à %H:%M')}

💬 Message :
{message_content}

ID Message: #{contact_msg.id}
"""

            try:
                email_admin = EmailMessage(
                    subject=admin_subject,
                    body=admin_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=["deboutwanindara@gmail.com"],
                )
                email_admin.send(fail_silently=False)
                admin_mail_sent = True
                print("✅ Email admin envoyé")
            except Exception as e:
                logger.error(f"Erreur email admin: {e}")

            # -------------------------
            # MESSAGE DE RETOUR FRONT
            # -------------------------
            if user_mail_sent:
                msg = "Votre message a été envoyé avec succès. Un email de confirmation vous a été envoyé."
            elif admin_mail_sent:
                msg = "Votre message a été reçu. Notre équipe vous contactera bientôt."
            else:
                msg = "Votre message a été enregistré mais l'envoi d'email a échoué."

            return JsonResponse({
                'success': True,
                'message': msg,
                'emails_sent': {
                    'confirmation': user_mail_sent,
                    'admin': admin_mail_sent
                }
            })

        except Exception as e:
            logger.error(f"Erreur générale contact: {e}")
            return JsonResponse({
                'success': False,
                'message': "Une erreur est survenue. Veuillez réessayer."
            })

    return JsonResponse({
        'success': False,
        'message': "Méthode non autorisée."
    })


def donate(request):
    return render(request, "contact/donate.html")
