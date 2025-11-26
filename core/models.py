from django.db import models

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
        app_label = 'core'
        verbose_name = "Photo de galerie"
        verbose_name_plural = "Photos de galerie"
        ordering = ['-date_taken', '-created_at']
    
    def __str__(self):
        return self.title