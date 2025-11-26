"""
Solution de contournement pour le problème de connexion Gmail
Utilise une approche différente pour contourner le problème Python 3.13 / Gmail
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_email_fixed(subject, message, recipient_list, from_email=None):
    """
    Envoie un email avec une méthode qui contourne le problème de connexion Gmail.
    Utilise une approche plus robuste avec gestion d'erreurs améliorée.
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    username = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD
    
    if not password:
        return False, "Mot de passe email non configuré"
    
    # Essayer le port 465 avec SSL (plus fiable)
    try:
        # Créer un contexte SSL avec moins de restrictions
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Connexion SSL directe
        logger.info("Tentative de connexion SSL sur le port 465...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30, context=context)
        
        # Activer le mode debug pour voir ce qui se passe
        server.set_debuglevel(1)
        
        # Authentification
        logger.info("Authentification en cours...")
        server.login(username, password)
        logger.info("Authentification réussie!")
        
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ', '.join(recipient_list) if isinstance(recipient_list, list) else recipient_list
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        # Envoyer
        text = msg.as_string()
        server.sendmail(from_email, recipient_list if isinstance(recipient_list, list) else [recipient_list], text)
        server.quit()
        
        logger.info(f"✅ Email envoyé avec succès via SSL (port 465)")
        return True, None
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Erreur d'authentification: {str(e)}"
        logger.error(error_msg)
        return False, error_msg + " - Vérifiez que votre App Password est valide et que la validation en 2 étapes est activée"
        
    except Exception as e:
        error_msg = f"Erreur SSL (port 465): {str(e)}"
        logger.warning(error_msg)
        
        # Essayer avec le port 587 et STARTTLS en utilisant une méthode différente
        try:
            logger.info("Tentative alternative avec port 587...")
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
            server.set_debuglevel(1)
            
            # Envoyer EHLO avant STARTTLS
            server.ehlo()
            server.starttls()
            server.ehlo()  # Re-envoyer EHLO après STARTTLS
            
            server.login(username, password)
            
            # Créer et envoyer le message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = ', '.join(recipient_list) if isinstance(recipient_list, list) else recipient_list
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            server.sendmail(from_email, recipient_list if isinstance(recipient_list, list) else [recipient_list], msg.as_string())
            server.quit()
            
            logger.info(f"✅ Email envoyé avec succès via STARTTLS (port 587)")
            return True, None
            
        except Exception as e2:
            return False, f"Toutes les méthodes ont échoué. Dernière erreur: {str(e2)}. Vérifiez votre App Password Gmail."

