"""
Backend SMTP personnalisé pour Gmail avec gestion améliorée des erreurs
"""
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
import smtplib
import ssl
import logging

logger = logging.getLogger(__name__)


class GmailSMTPBackend(EmailBackend):
    """
    Backend SMTP personnalisé pour Gmail avec retry automatique
    et support pour différentes configurations.
    """
    
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None, **kwargs):
        
        # Configuration par défaut pour Gmail
        host = host or settings.EMAIL_HOST
        port = port or settings.EMAIL_PORT
        username = username or settings.EMAIL_HOST_USER
        password = password or settings.EMAIL_HOST_PASSWORD
        use_tls = use_tls if use_tls is not None else settings.EMAIL_USE_TLS
        use_ssl = use_ssl if use_ssl is not None else getattr(settings, 'EMAIL_USE_SSL', False)
        timeout = timeout or getattr(settings, 'EMAIL_TIMEOUT', 10)
        
        super().__init__(
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls,
            fail_silently=fail_silently,
            use_ssl=use_ssl,
            timeout=timeout,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            **kwargs
        )
    
    def open(self):
        """
        Ouvre une connexion SMTP avec retry et gestion d'erreurs améliorée.
        """
        if self.connection:
            return False
        
        try:
            # Créer un contexte SSL/TLS sécurisé
            context = ssl.create_default_context()
            
            # Essayer différentes méthodes de connexion
            connection_methods = []
            
            # Méthode 1: SSL direct (port 465)
            if self.use_ssl or self.port == 465:
                connection_methods.append(('ssl', 465))
            
            # Méthode 2: STARTTLS (port 587)
            if self.use_tls or self.port == 587:
                connection_methods.append(('starttls', 587))
            
            # Méthode 3: Configuration actuelle
            if not connection_methods:
                if self.use_ssl:
                    connection_methods.append(('ssl', self.port))
                else:
                    connection_methods.append(('starttls', self.port))
            
            # Essayer chaque méthode
            last_error = None
            for method, port in connection_methods:
                try:
                    logger.info(f"Tentative de connexion SMTP: {method} sur le port {port}")
                    
                    if method == 'ssl':
                        # Connexion SSL directe
                        self.connection = smtplib.SMTP_SSL(
                            self.host,
                            port,
                            timeout=self.timeout,
                            context=context
                        )
                    else:
                        # Connexion STARTTLS
                        self.connection = smtplib.SMTP(
                            self.host,
                            port,
                            timeout=self.timeout
                        )
                        self.connection.starttls(context=context)
                    
                    # Authentification
                    if self.username and self.password:
                        self.connection.login(self.username, self.password)
                    
                    logger.info(f"✅ Connexion SMTP réussie avec {method} sur le port {port}")
                    return True
                    
                except smtplib.SMTPServerDisconnected as e:
                    last_error = f"Connexion fermée ({method}, port {port}): {str(e)}"
                    logger.warning(last_error)
                    if self.connection:
                        try:
                            self.connection.quit()
                        except:
                            pass
                        self.connection = None
                    continue
                    
                except smtplib.SMTPAuthenticationError as e:
                    error_msg = f"Erreur d'authentification ({method}, port {port}): {str(e)}"
                    logger.error(error_msg)
                    raise
                    
                except Exception as e:
                    last_error = f"Erreur ({method}, port {port}): {str(e)}"
                    logger.warning(last_error)
                    if self.connection:
                        try:
                            self.connection.quit()
                        except:
                            pass
                        self.connection = None
                    continue
            
            # Si toutes les méthodes ont échoué
            if last_error:
                error_msg = f"Toutes les méthodes de connexion ont échoué. Dernière erreur: {last_error}"
                logger.error(error_msg)
                raise smtplib.SMTPException(error_msg)
            else:
                raise smtplib.SMTPException("Impossible de se connecter au serveur SMTP")
                
        except Exception as e:
            if not self.fail_silently:
                raise
            logger.error(f"Erreur lors de l'ouverture de la connexion SMTP: {e}", exc_info=True)
            return False

