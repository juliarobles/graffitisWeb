from django.conf.urls import url,include
from django.urls import path
from .views import *
# De momento no usamos routers
# --------------------------------------
#from django.urls import url_include

# router = routers.DefaultRouter()
# router.register(r'Publicacion', views.PublicacionViewSet, basename="Publicacion" )
# router.register(r'Usuario', views.UsuarioViewSet, basename="Usuario" )
# --------------------------------------

urlpatterns = [
    path('inicio/', inicio, name='inicio'),
    path('html/eventos/', eventos_list ,name='eventos-list'),
    path('html/eventos/{int:ID_ACTIVIDAD}', eventos_list ,name='eventos-details'),
    path('html/publicaciones/', list_publicaciones_views, name='publicaciones-list'),
    path('html/publicaciones/detalles/<str:pk>/', publicaciones_detail_view, name='publicacion-detail'),
    path('html/usuarios', usuarios_list, name='usuarios-list'),
    path('html/usuarios/detalles/<str:pk>/', usuarios_detail, name='usuarios-detail'),
]