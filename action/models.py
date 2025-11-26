from django.db import models
from django.utils.text import slugify

class Action(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='actions/images/', blank=True, null=True)
    date = models.DateField()
    location = models.CharField(max_length=200)
    is_upcoming = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ActionGallery(models.Model):
    action = models.ForeignKey(Action, related_name='gallery_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='actions/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Action Galleries"

    def __str__(self):
        return f"Image for {self.action.title}"
