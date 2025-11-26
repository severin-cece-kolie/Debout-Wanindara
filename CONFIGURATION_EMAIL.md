# Configuration Email - Gmail App Password

## Problème courant : "Connection unexpectedly closed"

Si vous rencontrez l'erreur `SMTPServerDisconnected: Connection unexpectedly closed`, c'est probablement parce que Gmail nécessite maintenant un **"App Password"** (mot de passe d'application) au lieu du mot de passe normal de votre compte.

## Solution : Créer un App Password Gmail

### Étape 1 : Activer la validation en 2 étapes

1. Allez sur votre compte Google : https://myaccount.google.com/
2. Cliquez sur **Sécurité** dans le menu de gauche
3. Sous "Connexion à Google", cliquez sur **Validation en 2 étapes**
4. Suivez les instructions pour activer la validation en 2 étapes si ce n'est pas déjà fait

### Étape 2 : Créer un App Password

1. Toujours dans **Sécurité** > **Validation en 2 étapes**
2. Descendez jusqu'à la section **Mots de passe des applications**
3. Cliquez sur **Mots de passe des applications**
4. Sélectionnez "Autre (nom personnalisé)" dans le menu déroulant
5. Entrez un nom descriptif (ex: "Debout Wanindara Django")
6. Cliquez sur **Générer**
7. **COPIEZ le mot de passe généré** (16 caractères, espacés par groupes de 4)

### Étape 3 : Mettre à jour la configuration

1. Ouvrez le fichier `core/email_config.py`
2. Remplacez `EMAIL_PASSWORD` par le mot de passe d'application que vous venez de générer :

```python
EMAIL_PASSWORD = "xxxx xxxx xxxx xxxx"  # Remplacez par votre App Password (sans espaces)
```

**Important** : Enlevez les espaces du mot de passe ! Si Gmail affiche "xxxx xxxx xxxx xxxx", utilisez "xxxxxxxxxxxxxxxx" (16 caractères sans espaces).

### Étape 4 : Redémarrer Django

Après avoir mis à jour le fichier, redémarrez votre serveur Django :

```bash
python manage.py runserver
```

## Vérification

Vous devriez voir dans la console Django :
```
✅ Configuration email SMTP activée - les emails sont envoyés réellement
✅ Serveur SMTP: smtp.gmail.com:587
```

## Test de la connexion

Pour tester la connexion email, vous pouvez utiliser Django shell :

```python
python manage.py shell
```

Puis :
```python
from core.email_utils import test_email_connection
success, message = test_email_connection()
print(message)
```

## Note importante

- **Ne partagez JAMAIS** votre App Password
- Le fichier `core/email_config.py` est dans `.gitignore` et ne sera pas versionné
- Si vous perdez votre App Password, supprimez-le et créez-en un nouveau dans les paramètres Google

## Dépannage

### Erreur "Authentication failed"
- Vérifiez que vous utilisez bien un App Password, pas le mot de passe normal
- Vérifiez que la validation en 2 étapes est activée

### Erreur "Connection refused"
- Vérifiez votre connexion internet
- Vérifiez que votre firewall n'bloque pas le port 587

### Les emails ne partent toujours pas
- Vérifiez les logs Django pour plus de détails
- Utilisez `test_email_connection()` pour diagnostiquer

