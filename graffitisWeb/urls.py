"""graffitisWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django_mongoengine import mongo_admin

from rest_framework import permissions
from rest_framework.urlpatterns import format_suffix_patterns
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Para configurar drf_yasg
schema_view = get_schema_view(
   openapi.Info(
      title="Graffiti Web",
      default_version='v1',
      description="¡Bienvenido a la API-REST de <b>Graffiti Web!</b>\nAdemás de poder acceder a datos relativos a diferentes servicios del ámbito malagueño, podrá interactuar con nuestra aplicación <b>Graffiti App</b>",
      terms_of_service="https://www.grafittiApp.com/policies/terms/",
      contact=openapi.Contact(email="contact@graffitiApp.local"),
      license=openapi.License(name="Test License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('graffitiApp.urls', namespace='api')),
    path('', include('ayuntamientoApp.urls', namespace='ayuntamiento')),
    path('', include('clienteApp.urls')),
    #path('Publicacion/', include('graffitiApp.urls'))
    path('mongoadmin/', mongo_admin.site.urls),
    # OpenApi
    path('api/', schema_view.with_ui('swagger',
                                 cache_timeout=0), name="schema-swagger-ui"),
    path('redoc/', schema_view.with_ui('redoc',
                                      cache_timeout=0), name="schema-redoc"),
]

# let django built-in server serve static and media content
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html','xml'])