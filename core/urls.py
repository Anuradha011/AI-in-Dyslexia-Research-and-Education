from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('assessment/', include('assessment.urls')),
    path('learning/', include('learning.urls')),
    path('speech/', include('speech.urls')),
    path('neuroimaging/', include('neuroimaging.urls')),
    path('accessibility/', include('accessibility.urls')),
    path('reports/', include('reports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)