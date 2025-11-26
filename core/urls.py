
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('about/', views.about, name='about'),
    path('contact/', include('contact.urls')),
    path('actions/', include('action.urls')),
    path('join-us/', include('join.urls')),
    path('blog/', include('blog.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf.urls import handler403

handler403 = 'join.views.permission_denied_view'

