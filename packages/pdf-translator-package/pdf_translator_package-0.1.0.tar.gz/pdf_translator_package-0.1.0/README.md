Et dans ton projet principal urls.py (ex: config/urls.py) :

python
Copier
Modifier
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pdf/', include('pdf_translator_app.urls')),
]

# pour servir les fichiers PDF
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
⚙️ 5. Configuration settings.py
Ajoute en bas du fichier :

python
Copier
Modifier
import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')