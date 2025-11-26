"""
Utilitaires pour l'envoi d'emails avec gestion améliorée des erreurs
"""
from django.core.mail import send_mail
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
import smtplib
import ssl
import socket
import logging

logger = logging.getLogger(__name__)


def send_email_direct_smtp(subject, message, recipient_list, from_email=None):
    """
    Envoie un email en utilisant directement smtplib pour plus de contrôle.
    Essaie plusieurs configurations SMTP avec une approche plus robuste.
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    username = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD
    
    if not password:
        return False, "Mot de passe email non configuré"
    
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Essayer d'abord le port 465 avec SSL (méthode la plus fiable)
    try:
        logger.info("Tentative connexion SSL directe (port 465)...")
        
        # Créer un contexte SSL plus permissif
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30, context=context)
        
        # EHLO avant authentification
        server.ehlo()
        
        # Authentification
        server.login(username, password)
        
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ', '.join(recipient_list) if isinstance(recipient_list, list) else recipient_list
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        # Envoyer
        to_addresses = recipient_list if isinstance(recipient_list, list) else [recipient_list]
        server.sendmail(from_email, to_addresses, msg.as_string())
        server.quit()
        
        logger.info("✅ Email envoyé avec succès via SSL (port 465)")
        return True, None
        
    except Exception as e:
        logger.warning(f"Échec port 465: {str(e)}")
        
        # Essayer le port 587 avec STARTTLS (méthode alternative)
        try:
            logger.info("Tentative alternative STARTTLS (port 587)...")
            
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
            
            # EHLO initial
            server.ehlo()
            
            # STARTTLS
            context = ssl.create_default_context()
            server.starttls(context=context)
            
            # EHLO après STARTTLS (IMPORTANT!)
            server.ehlo()
            
            # Authentification
            server.login(username, password)
            
            # Créer et envoyer le message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = ', '.join(recipient_list) if isinstance(recipient_list, list) else recipient_list
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            to_addresses = recipient_list if isinstance(recipient_list, list) else [recipient_list]
            server.sendmail(from_email, to_addresses, msg.as_string())
            server.quit()
            
            logger.info("✅ Email envoyé avec succès via STARTTLS (port 587)")
            return True, None
            
        except smtplib.SMTPAuthenticationError as e:
            return False, f"Erreur d'authentification: {str(e)}. Vérifiez que votre App Password Gmail est valide."
            
        except Exception as e2:
            return False, f"Toutes les méthodes ont échoué. Dernière erreur: {str(e2)}"


def send_email_robust(subject, message, recipient_list, from_email=None, max_retries=2):
    """
    Envoie un email avec retry automatique et meilleure gestion d'erreurs.
    Essaie d'abord Django send_mail, puis smtplib direct si ça échoue.
    
    Args:
        subject: Sujet de l'email
        message: Corps du message
        recipient_list: Liste des destinataires
        from_email: Email de l'expéditeur (par défaut DEFAULT_FROM_EMAIL)
        max_retries: Nombre maximum de tentatives (défaut: 2)
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    # Essayer d'abord avec Django send_mail (méthode normale)
    for attempt in range(1, max_retries + 1):
        try:
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
            logger.info(f"Email envoyé avec succès à {recipient_list} (tentative {attempt})")
            return True, None
            
        except smtplib.SMTPServerDisconnected as e:
            logger.warning(f"Connexion SMTP fermée (tentative {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                import time
                time.sleep(2)
            else:
                # Si Django send_mail échoue, essayer connexion directe SMTP
                logger.info("Tentative avec connexion SMTP directe...")
                return send_email_direct_smtp(subject, message, recipient_list, from_email)
                
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Erreur d'authentification SMTP: {str(e)}"
            logger.error(error_msg)
            return False, error_msg + " (vérifiez votre App Password Gmail)"
            
        except Exception as e:
            error_msg = f"Erreur (tentative {attempt}/{max_retries}): {str(e)}"
            logger.warning(error_msg)
            if attempt < max_retries:
                import time
                time.sleep(2)
            else:
                # Si Django send_mail échoue, essayer connexion directe SMTP
                logger.info("Tentative avec connexion SMTP directe...")
                return send_email_direct_smtp(subject, message, recipient_list, from_email)
    
    # Dernière tentative avec connexion directe
    return send_email_direct_smtp(subject, message, recipient_list, from_email)


def test_email_connection():
    """
    Teste la connexion SMTP pour diagnostiquer les problèmes.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        backend = EmailBackend(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
            use_ssl=settings.EMAIL_USE_SSL,
            timeout=settings.EMAIL_TIMEOUT,
        )
        
        # Tester la connexion
        backend.open()
        backend.close()
        
        return True, "Connexion SMTP réussie"
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        
        diagnostic = f"Erreur de connexion SMTP ({error_type}): {error_msg}\n\n"
        
        if "SMTPServerDisconnected" in error_type:
            diagnostic += "💡 SOLUTIONS POSSIBLES:\n"
            diagnostic += "1. Vérifiez que vous utilisez un 'App Password' Gmail (pas le mot de passe normal)\n"
            diagnostic += "   → Aller dans: Compte Google > Sécurité > Validation en 2 étapes > Mots de passe des applications\n"
            diagnostic += "2. Activez la validation en 2 étapes sur votre compte Gmail\n"
            diagnostic += "3. Vérifiez que les connexions moins sécurisées sont autorisées (si nécessaire)\n"
            diagnostic += "4. Vérifiez votre connexion internet et firewall\n"
        
        elif "SMTPAuthenticationError" in error_type:
            diagnostic += "💡 PROBLÈME D'AUTHENTIFICATION:\n"
            diagnostic += "1. Vérifiez que EMAIL_HOST_USER et EMAIL_HOST_PASSWORD sont corrects\n"
            diagnostic += "2. Utilisez un 'App Password' Gmail (pas le mot de passe du compte)\n"
        
        logger.error(diagnostic)
        return False, diagnostic

