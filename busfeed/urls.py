"""
URL configuration for busfeed project.

URLs principais do BusFeed - Sistema de transporte público inteligente para Brasília.
Configura as rotas para todos os apps e recursos do sistema.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Administração Django
    path('admin/', admin.site.urls),
    
    # App principal - Core
    path('', include('core.urls')),
    
    # Apps funcionais (serão implementados posteriormente)
    # path('rotas/', include('routes.urls')),
    # path('paradas/', include('stops.urls')),
    # path('horarios/', include('schedules.urls')),
    # path('usuario/', include('users.urls')),
    # path('notificacoes/', include('notifications.urls')),
]

# Configuração para servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
