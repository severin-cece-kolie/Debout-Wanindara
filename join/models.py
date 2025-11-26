from django.db import models
import uuid


def photo_upload_to(instance, filename):
    # store in media/badges/photos/<uuid>_<filename>
    uid = uuid.uuid4().hex
    return f'badges/photos/{uid}_{filename}'


class Applicant(models.Model):
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
    
    LANGUAGES_CHOICES = [
        ('FR', 'Français'),
        ('ANG', 'Anglais'),
        ('SOU', 'Soussou'),
        ('PEU', 'Peul'),
        ('MAL', 'Malinké'),
        ('KIS', 'Kissi'),
        ('GUE', 'Guerzé'),
        ('TON', 'Toma'),
        ('AUTRE', 'Autre langue')
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

    QUARTIERS_CONAKRY = [
        ('KALOUM', 'Kaloum'),
        ('DIXINN', 'Dixinn'),
        ('MATAM', 'Matam'),
        ('RATOMA', 'Ratoma'),
        ('MATOTO', 'Matoto'),
        ('AUTRE', 'Autre quartier')
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
    
    nom_complet = models.CharField(max_length=200, verbose_name='Nom complet')
    position = models.CharField(max_length=150, verbose_name='Poste', blank=True, default='')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=50, verbose_name='Téléphone', blank=True, default='')
    numero_id = models.CharField(max_length=50, verbose_name='Numéro ID', unique=True)
    photo = models.ImageField(upload_to=photo_upload_to, verbose_name='Photo', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Membre'
        verbose_name_plural = 'Membres'

    def __str__(self):
        return f"{self.nom_complet} ({self.numero_id})"

class GalleryPhoto(models.Model):
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
    
    
