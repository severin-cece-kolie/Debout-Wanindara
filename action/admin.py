from django.contrib import admin
from .models import Action, ActionGallery

class ActionGalleryInline(admin.TabularInline):
    model = ActionGallery
    extra = 1

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'is_upcoming')
    list_filter = ('is_upcoming', 'date')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ActionGalleryInline]

@admin.register(ActionGallery)
class ActionGalleryAdmin(admin.ModelAdmin):
    list_display = ('action', 'caption', 'created_at')
    list_filter = ('action', 'created_at')
