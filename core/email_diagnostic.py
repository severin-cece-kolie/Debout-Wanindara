"""
Diagnostic avancé pour les problèmes d'email SMTP
"""
import smtplib
import ssl
import socket
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def test_smtp_connection_detailed():
    """
    Test détaillé de la connexion SMTP avec diagnostic complet
    """
    results = {
        'network': {'status': 'unknown', 'message': ''},
        'password': {'status': 'unknown', 'message': ''},
        'authentication': {'status': 'unknown', 'message': ''},
        'overall': {'status': 'unknown', 'message': ''}
    }
    
    username = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD
    
    print("\n" + "="*70)
    print("🔍 DIAGNOSTIC COMPLET DE LA CONNEXION EMAIL")
    print("="*70)
    
    # TEST 1: Vérification du mot de passe
    print("\n📝 TEST 1: Vérification du mot de passe")
    print("-" * 70)
    if not password:
        results['password'] = {'status': 'error', 'message': 'Aucun mot de passe configuré'}
        print("❌ ERREUR: Aucun mot de passe configuré dans EMAIL_HOST_PASSWORD")
        return results
    
    if len(password) < 16:
        results['password'] = {'status': 'warning', 'message': f'Mot de passe trop court ({len(password)} caractères)'}
        print(f"⚠️  ATTENTION: Le mot de passe fait seulement {len(password)} caractères")
        print("   Un App Password Gmail doit faire exactement 16 caractères")
    elif len(password) == 16:
        results['password'] = {'status': 'ok', 'message': 'Longueur correcte (16 caractères)'}
        print(f"✅ Longueur du mot de passe correcte: {len(password)} caractères")
    else:
        results['password'] = {'status': 'warning', 'message': f'Mot de passe trop long ({len(password)} caractères)'}
        print(f"⚠️  ATTENTION: Le mot de passe fait {len(password)} caractères (normalement 16)")
    
    # Afficher les premiers caractères (masqué)
    if password:
        masked = password[:4] + "*" * (len(password) - 8) + password[-4:] if len(password) > 8 else "*" * len(password)
        print(f"   Mot de passe (masqué): {masked}")
    
    # TEST 2: Test de connexion réseau
    print("\n🌐 TEST 2: Test de connexion réseau")
    print("-" * 70)
    hosts_to_test = [
        ('smtp.gmail.com', 587, 'TLS'),
        ('smtp.gmail.com', 465, 'SSL'),
        ('google.com', 80, 'HTTP'),
    ]
    
    network_ok = False
    for host, port, protocol in hosts_to_test:
        try:
            sock = socket.create_connection((host, port), timeout=5)
            sock.close()
            print(f"✅ {host}:{port} ({protocol}) - Connexion réussie")
            if 'smtp.gmail.com' in host:
                network_ok = True
        except socket.timeout:
            print(f"❌ {host}:{port} ({protocol}) - Timeout (firewall?)")
        except socket.gaierror as e:
            print(f"❌ {host}:{port} ({protocol}) - Erreur DNS: {e}")
        except ConnectionRefusedError:
            print(f"❌ {host}:{port} ({protocol}) - Connexion refusée")
        except Exception as e:
            print(f"❌ {host}:{port} ({protocol}) - Erreur: {e}")
    
    if not network_ok:
        results['network'] = {'status': 'error', 'message': 'Impossible de se connecter à smtp.gmail.com'}
        print("\n⚠️  ATTENTION: Impossible de se connecter à smtp.gmail.com")
        print("   Vérifiez votre connexion internet et firewall")
    else:
        results['network'] = {'status': 'ok', 'message': 'Connexion réseau OK'}
    
    # TEST 3: Test SMTP détaillé avec différents ports
    print("\n📧 TEST 3: Test SMTP détaillé")
    print("-" * 70)
    
    configs = [
        {'port': 587, 'use_ssl': False, 'use_tls': True, 'name': 'STARTTLS (recommandé)'},
        {'port': 465, 'use_ssl': True, 'use_tls': False, 'name': 'SSL direct'},
    ]
    
    smtp_success = False
    auth_success = False
    last_error = None
    
    for config in configs:
        print(f"\n🔄 Test {config['name']} (port {config['port']})...")
        try:
            context = ssl.create_default_context()
            
            if config['use_ssl']:
                print(f"   → Connexion SSL directe...")
                server = smtplib.SMTP_SSL(
                    'smtp.gmail.com',
                    config['port'],
                    timeout=15,
                    context=context
                )
                print(f"   ✅ Connexion établie")
                smtp_success = True
            else:
                print(f"   → Connexion TCP...")
                server = smtplib.SMTP(
                    'smtp.gmail.com',
                    config['port'],
                    timeout=15
                )
                print(f"   ✅ Connexion TCP établie")
                
                print(f"   → Démarrage TLS...")
                server.starttls(context=context)
                print(f"   ✅ TLS démarré")
                smtp_success = True
            
            print(f"   → Authentification...")
            server.login(username, password)
            print(f"   ✅ Authentification réussie!")
            auth_success = True
            results['authentication'] = {'status': 'ok', 'message': f'Authentification réussie sur port {config["port"]}'}
            
            server.quit()
            print(f"\n🎉 SUCCÈS COMPLET avec {config['name']} (port {config['port']})!")
            break
            
        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"Connexion fermée immédiatement: {str(e)}"
            print(f"   ❌ {error_msg}")
            last_error = error_msg
            results['authentication'] = {'status': 'error', 'message': error_msg}
            
            # Diagnostic spécifique
            print(f"\n   🔍 DIAGNOSTIC:")
            print(f"   • Gmail ferme la connexion AVANT l'authentification")
            print(f"   • Cela signifie probablement que:")
            print(f"     1. Le mot de passe n'est PAS un App Password valide")
            print(f"     2. Le compte Gmail a des restrictions de sécurité")
            print(f"     3. L'IP est bloquée ou suspecte pour Gmail")
            continue
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Erreur d'authentification: {str(e)}"
            print(f"   ❌ {error_msg}")
            results['authentication'] = {'status': 'error', 'message': error_msg}
            
            print(f"\n   🔍 DIAGNOSTIC:")
            print(f"   • La connexion fonctionne mais l'authentification échoue")
            print(f"   • Solutions:")
            print(f"     1. Vérifiez que vous utilisez un App Password (pas le mot de passe du compte)")
            print(f"     2. Vérifiez que la validation en 2 étapes est activée")
            print(f"     3. Créez un nouveau App Password si nécessaire")
            last_error = error_msg
            continue
            
        except Exception as e:
            error_msg = f"Erreur inattendue: {str(e)}"
            print(f"   ❌ {error_msg}")
            last_error = error_msg
            import traceback
            print(f"   {traceback.format_exc()}")
            continue
    
    # Résumé final
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DU DIAGNOSTIC")
    print("="*70)
    
    if auth_success:
        results['overall'] = {'status': 'success', 'message': 'La connexion email fonctionne correctement!'}
        print("✅ SUCCÈS: La connexion email fonctionne!")
        print("   Vous pouvez maintenant envoyer des emails.")
    else:
        results['overall'] = {'status': 'error', 'message': last_error or 'Échec de connexion'}
        print("❌ ÉCHEC: Impossible de se connecter à Gmail")
        print("\n🔧 SOLUTIONS À ESSAYER:")
        print("1. VÉRIFIEZ QUE VOUS UTILISEZ UN APP PASSWORD:")
        print("   → https://myaccount.google.com/apppasswords")
        print("   → Créez un nouveau mot de passe d'application")
        print("   → Nom: 'Debout Wanindara Django'")
        print("   → Copiez les 16 caractères (SANS ESPACES)")
        print("   → Mettez à jour core/email_config.py")
        print("\n2. VÉRIFIEZ VOTRE COMPTE GMAIL:")
        print("   → Validation en 2 étapes activée?")
        print("   → Compte actif et non suspendu?")
        print("   → Pas de restrictions de sécurité?")
        print("\n3. VÉRIFIEZ VOTRE RÉSEAU:")
        print("   → Firewall bloque les ports 587/465?")
        print("   → Proxy/VPN interfère?")
        print("   → Connexion internet stable?")
    
    print("="*70 + "\n")
    
    return results

