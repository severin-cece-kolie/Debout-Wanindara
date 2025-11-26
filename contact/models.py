from django.db import models

# Create your models here.
from django.db import models

class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('signaler un probleme', 'Signaler un problème'),
        ('demande de formation', 'Demande de formation'),
        ('demande de rendez vous', 'Demande de rendez-vous'),
        ('demande de soutien', 'Demande de soutien'),
        ('demande d\'invitation', 'Demande d\'invitation'),
        ('autre', 'Autre'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    
    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"