"""
Script standalone pour tester la connexion SMTP Gmail
Exécutez: python test_smtp_connection.py
"""
import smtplib
import ssl
import socket

# Configuration - À MODIFIER
GMAIL_USER = "deboutwanindara@gmail.com"
GMAIL_PASSWORD = "zkmeqklyrswjozdt"  # Votre App Password ici

print("="*70)
print("TEST DE CONNEXION SMTP GMAIL - DIAGNOSTIC COMPLET")
print("="*70)

# Test 1: Vérification du mot de passe
print("\n📝 TEST 1: Vérification du mot de passe")
print("-"*70)
if len(GMAIL_PASSWORD) == 16:
    print(f"✅ Longueur correcte: {len(GMAIL_PASSWORD)} caractères")
    masked = GMAIL_PASSWORD[:4] + "*" * 8 + GMAIL_PASSWORD[-4:]
    print(f"   Mot de passe (masqué): {masked}")
else:
    print(f"❌ Longueur incorrecte: {len(GMAIL_PASSWORD)} caractères (devrait être 16)")
    print("   ⚠️  Assurez-vous d'utiliser un App Password Gmail")

# Test 2: Connexion réseau
print("\n🌐 TEST 2: Test de connexion réseau")
print("-"*70)
try:
    sock = socket.create_connection(('smtp.gmail.com', 587), timeout=5)
    sock.close()
    print("✅ Connexion à smtp.gmail.com:587 réussie")
except Exception as e:
    print(f"❌ Impossible de se connecter à smtp.gmail.com:587: {e}")
    print("   Vérifiez votre connexion internet et firewall")

# Test 3: Test SMTP Port 587 (STARTTLS)
print("\n📧 TEST 3: Test SMTP Port 587 (STARTTLS)")
print("-"*70)
try:
    print("   → Connexion TCP...")
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
    print("   ✅ Connexion TCP établie")
    
    print("   → Démarrage TLS...")
    context = ssl.create_default_context()
    server.starttls(context=context)
    print("   ✅ TLS démarré")
    
    print("   → Authentification...")
    server.login(GMAIL_USER, GMAIL_PASSWORD)
    print("   ✅ AUTHENTIFICATION RÉUSSIE!")
    
    server.quit()
    print("\n🎉 SUCCÈS COMPLET sur le port 587!")
    
except smtplib.SMTPServerDisconnected as e:
    print(f"   ❌ Connexion fermée immédiatement: {e}")
    print("\n   🔍 DIAGNOSTIC:")
    print("   • Gmail ferme la connexion AVANT l'authentification")
    print("   • Cela signifie probablement que:")
    print("     1. ❌ Le mot de passe n'est PAS un App Password valide")
    print("     2. ❌ Le compte Gmail a des restrictions de sécurité")
    print("     3. ❌ L'IP est bloquée par Gmail")
    print("\n   💡 SOLUTION:")
    print("   → Allez sur https://myaccount.google.com/apppasswords")
    print("   → Créez un NOUVEAU App Password")
    print("   → Nom: 'Debout Wanindara Django'")
    print("   → Copiez les 16 caractères (SANS ESPACES)")
    print("   → Remplacez GMAIL_PASSWORD dans ce script")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"   ❌ Erreur d'authentification: {e}")
    print("\n   🔍 DIAGNOSTIC:")
    print("   • La connexion fonctionne mais l'authentification échoue")
    print("   • Vérifiez que:")
    print("     1. Vous utilisez un App Password (pas le mot de passe du compte)")
    print("     2. La validation en 2 étapes est activée")
    print("     3. Le mot de passe n'a pas d'espaces")
    
except Exception as e:
    print(f"   ❌ Erreur inattendue: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test SMTP Port 465 (SSL)
print("\n📧 TEST 4: Test SMTP Port 465 (SSL)")
print("-"*70)
try:
    print("   → Connexion SSL directe...")
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15, context=context)
    print("   ✅ Connexion SSL établie")
    
    print("   → Authentification...")
    server.login(GMAIL_USER, GMAIL_PASSWORD)
    print("   ✅ AUTHENTIFICATION RÉUSSIE!")
    
    server.quit()
    print("\n🎉 SUCCÈS COMPLET sur le port 465!")
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "="*70)
print("FIN DU TEST")
print("="*70)

