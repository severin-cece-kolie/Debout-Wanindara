from django.contrib import admin
from .models import GalleryPhoto

@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'date_taken', 'featured', 'created_at']
    list_filter = ['category', 'featured', 'date_taken']
    search_fields = ['title', 'description']
    list_editable = ['featured']
    date_hierarchy = 'date_taken'