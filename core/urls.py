from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import handler403

from core import views
from home import views as home_views   # pour about si c'est dans home
from join.views import permission_denied_view

# -------------------------------
#        HANDLER 403
# -------------------------------
handler403 = 'join.views.permission_denied_view'


# -------------------------------
#    URLS hors traduction
# -------------------------------
urlpatterns = [

    # --- Sélecteur de langue ---
    path('i18n/', include('django.conf.urls.i18n')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# -------------------------------
#   URLS Multilingues FR/EN
# -------------------------------
urlpatterns += i18n_patterns(

    # Django admin
    path('secure-debout-wanindara-2025/', admin.site.urls),

    # Home page
    path('', include('home.urls')),

    # About (si ton about est une view directe)
    path('about/', views.about, name='about'),

    # Contact
    path('contact/', include('contact.urls')),

    # Actions
    path('actions/', include('action.urls')),

    # Join-us
    path('join-us/', include('join.urls')),

    # Blog
    path('blog/', include('blog.urls')),
    

    prefix_default_language=False, 
)
