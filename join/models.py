# join/models.py
from django.db import models
import uuid


def photo_upload_to(instance, filename):
    """Store in media/badges/photos/<uuid>_<filename>"""
    uid = uuid.uuid4().hex
    return f'badges/photos/{uid}_{filename}'


class Applicant(models.Model):
    """Modèle pour les candidatures d'adhésion"""
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre')
    ]
    
    DIPLOMA_CHOICES = [
        ('BAC', 'Baccalauréat'),
        ('BTS', 'Brevet de Technicien Supérieur (BTS)'),
        ('LIC', 'Licence'),
        ('MASTER', 'Master'),
        ('DOC', 'Doctorat'),
        ('DUT', 'DUT'),
        ('CAP', 'Certificat d\'Aptitude Professionnelle'),
        ('BEP', 'Brevet d\'Études Professionnelles'),
        ('AUTRE', 'Autre diplôme')
    ]
    
    CITY_CHOICES = [
        ('CONAKRY', 'Conakry'),
        ('KAMSAR', 'Kamsar'),
        ('BOKE', 'Boké'),
        ('KINDIA', 'Kindia'),
        ('MAMOU', 'Mamou'),
        ('LABE', 'Labé'),
        ('KANKAN', 'Kankan'),
        ('NZEREKORE', 'N\'Zérékoré'),
        ('AUTRE', 'Autre ville')
    ]
    
    COUNTRY_CHOICES = [
        ('GIN', 'Guinée'),
        ('FRA', 'France'),
        ('USA', 'États-Unis'),
        ('CAN', 'Canada'),
        ('GBR', 'Royaume-Uni'),
        ('BEL', 'Belgique'),
        ('DEU', 'Allemagne'),
        ('ITA', 'Italie'),
        ('ESP', 'Espagne'),
        ('CHE', 'Suisse'),
        ('SEN', 'Sénégal'),
        ('CIV', 'Côte d\'Ivoire'),
        ('MLI', 'Mali'),
        ('MAR', 'Maroc'),
        ('AUTRE', 'Autre pays')
    ]
    
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=100, verbose_name='Prénom', blank=True, default='')
    last_name = models.CharField(max_length=100, verbose_name='Nom', blank=True, default='')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Sexe', blank=True, default='O')
    phone = models.CharField(max_length=50, verbose_name='Contact', blank=True, default='')
    email = models.EmailField(verbose_name='Adresse mail')
    position = models.CharField(max_length=200, verbose_name='Poste', blank=True, default='')
    diploma = models.CharField(max_length=10, choices=DIPLOMA_CHOICES, verbose_name='Diplôme', blank=True, default='')
    skills = models.TextField(verbose_name='Compétences', blank=True, default='')
    languages = models.CharField(max_length=200, verbose_name='Langues parlées', help_text='Sélectionnez une ou plusieurs langues', blank=True, default='')
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, verbose_name='Pays de résidence', blank=True, default='GIN')
    city = models.CharField(max_length=20, choices=CITY_CHOICES, verbose_name='Ville de résidence', blank=True, default='CONAKRY')
    district = models.CharField(max_length=20, verbose_name='Quartier', blank=True, default='')
    photo = models.ImageField(upload_to=photo_upload_to, verbose_name='Photo', blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return f"Applicant {self.first_name} {self.last_name} <{self.email}>"


class Membre(models.Model):
    """Modèle pour les membres avec catégories et badges"""
    
    # Catégories de membres
    CATEGORIE_CHOICES = [
        ('MEMBRE', 'Membre'),
        ('INVITE', 'Invité'),
        ('PRESIDENT', 'Président'),
        ('VICE_PRESIDENT', 'Vice-Président'),
        ('SECRETAIRE_GENERAL', 'Secrétaire Général'),
        ('TRESORIER', 'Trésorier'),
        ('DIRECTEUR', 'Directeur'),
        ('PARTENAIRE', 'Partenaire'),
        ('BENEVOLE', 'Bénévole'),
        ('MEMBRE_HONNEUR', 'Membre d\'Honneur'),
    ]
    
    # Niveaux d'accès
    NIVEAU_ACCES_CHOICES = [
        ('BASIQUE', 'Accès Basique'),
        ('STANDARD', 'Accès Standard'),
        ('PRIVILEGIE', 'Accès Privilégié'),
        ('COMPLET', 'Accès Complet'),
    ]
    
    # Statut du badge
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('SUSPENDU', 'Suspendu'),
        ('EXPIRE', 'Expiré'),
        ('REVOQUE', 'Révoqué'),
    ]
    
    nom_complet = models.CharField(max_length=200, verbose_name='Nom complet')
    position = models.CharField(max_length=150, verbose_name='Poste', blank=True, default='')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=50, verbose_name='Téléphone', blank=True, default='')
    
    # Nouveaux champs
    categorie = models.CharField(
        max_length=30, 
        choices=CATEGORIE_CHOICES, 
        default='MEMBRE',
        verbose_name='Catégorie de membre',
        help_text='Type de membre dans l\'organisation'
    )
    
    niveau_acces = models.CharField(
        max_length=20,
        choices=NIVEAU_ACCES_CHOICES,
        default='BASIQUE',
        verbose_name='Niveau d\'accès',
        help_text='Niveau d\'accès aux ressources de l\'organisation'
    )
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='ACTIF',
        verbose_name='Statut du badge',
        help_text='État actuel du badge'
    )
    
    numero_id = models.CharField(max_length=50, unique=True, verbose_name='Numéro ID')
    photo = models.ImageField(upload_to=photo_upload_to, verbose_name='Photo', blank=True, null=True)
    
    # Dates importantes
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    date_expiration = models.DateField(null=True, blank=True, verbose_name='Date d\'expiration')
    derniere_modification = models.DateTimeField(auto_now=True, verbose_name='Dernière modification')
    
    # Informations supplémentaires
    departement = models.CharField(max_length=100, blank=True, default='', verbose_name='Département')
    notes = models.TextField(blank=True, default='', verbose_name='Notes internes')
    
    class Meta:
        verbose_name = 'Membre'
        verbose_name_plural = 'Membres'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nom_complet} ({self.numero_id}) - {self.get_categorie_display()}"
    
    def get_couleur_badge(self):
        """Retourne la couleur du badge selon la catégorie"""
        couleurs = {
            'MEMBRE': '#3b82f6',  # Bleu
            'INVITE': '#10b981',  # Vert
            'PRESIDENT': '#dc2626',  # Rouge
            'VICE_PRESIDENT': '#ea580c',  # Orange
            'SECRETAIRE_GENERAL': '#8b5cf6',  # Violet
            'TRESORIER': '#eab308',  # Jaune
            'DIRECTEUR': '#06b6d4',  # Cyan
            'PARTENAIRE': '#f59e0b',  # Ambre
            'BENEVOLE': '#84cc16',  # Lime
            'MEMBRE_HONNEUR': '#d946ef',  # Fuchsia
        }
        return couleurs.get(self.categorie, '#3b82f6')
    
    def get_icone_categorie(self):
        """Retourne l'icône Font Awesome selon la catégorie"""
        icones = {
            'MEMBRE': 'fa-user',
            'INVITE': 'fa-user-tag',
            'PRESIDENT': 'fa-crown',
            'VICE_PRESIDENT': 'fa-star',
            'SECRETAIRE_GENERAL': 'fa-file-alt',
            'TRESORIER': 'fa-coins',
            'DIRECTEUR': 'fa-briefcase',
            'PARTENAIRE': 'fa-handshake',
            'BENEVOLE': 'fa-hands-helping',
            'MEMBRE_HONNEUR': 'fa-medal',
        }
        return icones.get(self.categorie, 'fa-user')
    
    def est_actif(self):
        """Vérifie si le badge est actif"""
        return self.statut == 'ACTIF'
    
    def est_expire(self):
        """Vérifie si le badge est expiré"""
        if self.date_expiration:
            from django.utils import timezone
            return timezone.now().date() > self.date_expiration
        return False


class GalleryPhoto(models.Model):
    """Modèle pour la galerie photos"""
    CATEGORY_CHOICES = [
        ('EVENTS', 'Événements'),
        ('TEAM', 'Équipe'),
        ('PROJECTS', 'Projets'),
        ('COMMUNITY', 'Communauté'),
        ('ACTIVITIES', 'Activités'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='gallery/', verbose_name="Photo")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='EVENTS')
    date_taken = models.DateField(verbose_name="Date de prise de vue")
    featured = models.BooleanField(default=False, verbose_name="Photo à la une")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Photo de galerie"
        verbose_name_plural = "Photos de galerie"
        ordering = ['-date_taken', '-created_at']
    
    def __str__(self):
        return self.title