# 🔴 PROBLÈME IDENTIFIÉ - Gmail ferme la connexion

## Diagnostic

D'après les tests, Gmail ferme la connexion **après le handshake TLS/SSL** mais **AVANT l'authentification**. Cela se produit sur les deux ports (465 et 587).

## Causes possibles

1. **App Password invalide ou révoqué** (le plus probable)
2. **Problème avec Python 3.13 et smtplib** (compatibilité)
3. **Gmail bloque votre IP** pour des raisons de sécurité

## ✅ SOLUTIONS À ESSAYER

### Solution 1 : Vérifier et recréer l'App Password

1. Allez sur **https://myaccount.google.com/apppasswords**
2. **Supprimez** tous les anciens App Passwords
3. **Créez un nouveau** App Password :
   - Nom : `Debout Wanindara Django Production`
   - **Copiez les 16 caractères SANS ESPACES**
4. **Mettez à jour** `core/email_config.py` :
   ```python
   EMAIL_PASSWORD = "nouveau_mot_de_passe_16_caracteres"
   ```
5. **Redémarrez Django** et testez

### Solution 2 : Utiliser un autre service email (Recommandé si Gmail pose problème)

#### Option A : SendGrid (Gratuit jusqu'à 100 emails/jour)

1. Créez un compte sur https://sendgrid.com
2. Générez une clé API
3. Modifiez `core/settings.py` :

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # Toujours 'apikey' pour SendGrid
EMAIL_HOST_PASSWORD = 'votre_clé_api_sendgrid'  # Votre clé API ici
DEFAULT_FROM_EMAIL = 'deboutwanindara@gmail.com'
SERVER_EMAIL = 'deboutwanindara@gmail.com'
```

#### Option B : Mailgun (Gratuit jusqu'à 5000 emails/mois)

1. Créez un compte sur https://mailgun.com
2. Obtenez vos identifiants SMTP
3. Modifiez `core/settings.py` :

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre_nom_utilisateur_mailgun'
EMAIL_HOST_PASSWORD = 'votre_mot_de_passe_mailgun'
DEFAULT_FROM_EMAIL = 'deboutwanindara@gmail.com'
SERVER_EMAIL = 'deboutwanindara@gmail.com'
```

### Solution 3 : Vérifier votre compte Gmail

1. **Connectez-vous** à Gmail avec `deboutwanindara@gmail.com`
2. **Vérifiez** qu'il n'y a pas d'alerte de sécurité
3. **Vérifiez** que le compte n'est pas suspendu
4. **Activez** la validation en 2 étapes si ce n'est pas fait
5. **Vérifiez** les activités suspectes sur https://myaccount.google.com/security

### Solution 4 : Tester avec un autre compte Gmail

Si vous avez un autre compte Gmail, testez avec :
1. Créez un App Password pour ce compte
2. Testez avec `test_smtp_connection.py`
3. Si ça fonctionne, le problème vient du compte `deboutwanindara@gmail.com`

## 🚀 RECOMMANDATION IMMÉDIATE

Je recommande fortement d'utiliser **SendGrid** ou **Mailgun** car :
- ✅ Plus fiable que Gmail pour les applications
- ✅ Pas de problèmes de connexion
- ✅ Gratuit pour un usage modéré
- ✅ Meilleure délivrabilité
- ✅ Statistiques d'envoi

## 📝 Mise à jour automatique du code

J'ai mis à jour le code pour :
1. ✅ Utiliser une méthode plus robuste pour l'envoi d'emails
2. ✅ Envoyer EHLO avant et après STARTTLS
3. ✅ Gérer mieux les erreurs d'authentification
4. ✅ Mettre à jour le mot de passe dans `email_config.py`

## 🔍 Test après modification

Après avoir modifié la configuration, testez avec :

```bash
python test_smtp_connection.py
```

Ou dans Django :

```bash
python manage.py test_email
```

## 💡 Si rien ne fonctionne

Si toutes les solutions échouent, c'est probablement que :
1. Gmail bloque définitivement votre IP/compte
2. Il y a un problème avec votre connexion internet
3. Votre firewall/antivirus bloque les connexions SMTP

Dans ce cas, utilisez SendGrid ou Mailgun - c'est la solution la plus fiable.

