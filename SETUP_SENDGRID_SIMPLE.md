# ✅ Configuration SendGrid - Simple et Rapide

## 🎯 Pour un Étudiant - C'est Gratuit et Simple !

SendGrid est **gratuit jusqu'à 100 emails/jour** - parfait pour vos tests et votre projet étudiant.

## 📝 Étapes Simples (5 minutes)

### 1. Créer un compte SendGrid (2 minutes)

1. Allez sur : **https://signup.sendgrid.com**
2. Remplissez :
   - Email : votre email
   - Mot de passe : choisissez un mot de passe
   - Nom : votre nom
3. Cliquez sur **"Create Account"**
4. Confirmez votre email

### 2. Créer une clé API (2 minutes)

1. Une fois connecté, cliquez sur **"Settings"** (en haut à droite)
2. Cliquez sur **"API Keys"** dans le menu
3. Cliquez sur **"Create API Key"** (bouton bleu)
4. Donnez un nom : `Debout Wanindara`
5. Sélectionnez **"Restricted Access"** puis cochez seulement **"Mail Send"**
6. Cliquez sur **"Create & View"**
7. **IMPORTANT : COPIEZ la clé API maintenant** (elle commence par `SG.`)
   - Vous ne pourrez plus la voir après !
   - Collez-la quelque part temporairement

### 3. Mettre la clé dans le code (1 minute)

1. Ouvrez le fichier `core/email_config.py`
2. Remplacez le contenu par :
```python
# Configuration SendGrid - GRATUIT jusqu'à 100 emails/jour
SENDGRID_API_KEY = "SG.votre_clé_api_ici_collée"
```

3. Remplacez `votre_clé_api_ici_collée` par la clé que vous avez copiée

### 4. Mettre à jour settings.py

J'ai déjà modifié `core/settings.py` pour vous - il détecte automatiquement SendGrid si la clé est dans `email_config.py`.

### 5. Tester !

Redémarrez Django et testez un formulaire de badge ou de contact.

## ✅ C'est Tout !

Vos emails fonctionneront maintenant. Aucune autre configuration nécessaire.

## 💡 Avantages pour un Étudiant

- ✅ **100% gratuit** jusqu'à 100 emails/jour
- ✅ **Simple** - pas de complications
- ✅ **Fiable** - ça marche tout le temps
- ✅ **Parfait pour les projets étudiants**

## ❓ Besoin d'aide ?

Si vous avez un problème :
1. Vérifiez que la clé API commence bien par `SG.`
2. Vérifiez qu'elle est bien dans `core/email_config.py`
3. Redémarrez Django

Voilà ! Simple et efficace ! 🚀

