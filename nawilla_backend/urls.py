"""
URL configuration for nawilla_backend project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Halaman Uji Coba Interaktif di Browser
    path('', TemplateView.as_view(template_name='test_page.html'), name='test_page'),
    path('admin/', admin.site.urls),
    # API endpoints v1
    path('api/v1/', include('sentiment_api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
