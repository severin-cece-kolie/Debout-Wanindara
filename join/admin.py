from django.contrib import admin
from .models import Applicant, Membre


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
	list_display = ('first_name', 'last_name', 'email', 'phone', 'status')
	search_fields = ('first_name', 'last_name', 'email', 'phone')


@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
	list_display = ('nom_complet', 'numero_id', 'position', 'email', 'created_at')
	search_fields = ('nom_complet', 'numero_id', 'email')
	list_filter = ('created_at',)
	
	def save_model(self, request, obj, form, change):
		# Générer automatiquement le numéro ID s'il n'existe pas
		if not obj.numero_id:
			# Utiliser le nombre total de membres + 1 pour éviter les collisions
			count = Membre.objects.count()
			next_id = count + 1
			# Vérifier que le numéro n'existe pas déjà (au cas où)
			while Membre.objects.filter(numero_id=f"DW-{next_id:04d}").exists():
				next_id += 1
			obj.numero_id = f"DW-{next_id:04d}"
		super().save_model(request, obj, form, change)




from django.contrib import admin
from .models import GalleryPhoto

@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'date_taken', 'featured', 'created_at']
    list_filter = ['category', 'featured', 'date_taken']
    search_fields = ['title', 'description']
    list_editable = ['featured']
    date_hierarchy = 'date_taken'
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'description', 'category')
        }),
        ('Image', {
            'fields': ('image', 'featured')
        }),
        ('Dates', {
            'fields': ('date_taken',)
        }),
    )
