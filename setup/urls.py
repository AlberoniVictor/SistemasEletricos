from django.contrib import admin
from rest_framework.routers import DefaultRouter
from django.urls import path,include
from .api_root import APIRootView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", APIRootView.as_view(), name="api-root"),
    path('api/', include('apps.irradiacao.urls')),
    path('api/', include('apps.cliente.urls')),
    path('api/', include('apps.solar.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
