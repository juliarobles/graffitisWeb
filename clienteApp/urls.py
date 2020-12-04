from django.conf.urls import url,include
from django.urls import path
from clienteApp.views import *
# De momento no usamos routers
# --------------------------------------
#from django.urls import url_include

# router = routers.DefaultRouter()
# router.register(r'Publicacion', views.PublicacionViewSet, basename="Publicacion" )
# router.register(r'Usuario', views.UsuarioViewSet, basename="Usuario" )
# --------------------------------------

#  ** Información API IMGUR**
#  ** Cuenta: graffitisweb@gmail.com
#  ** Pass: graffiti1$
#  **  client_id = '6f71c692857b528'
#  **  client_secret = 'fdd4159d0389284b15e33c8c80018700b0a8f5c0'

# **
# ** flicker clave
# ** 75b8452aae39dc0967a42c37c139e8a0
# ** flicker secreto
# ** 15075131b9983f9b
# ** Cuenta: graffitisweb@gmail.com
# ** Pass: graffitigraffiti
# ** user_id: 191270823@N05



urlpatterns = [
    path('inicio/', inicio, name='inicio'),
    path('principal/', principal, name='principal'),
    path('registro/', registro, name='registro'),
    path('html/eventos/$', eventos_list ,name='eventos-list'),
    path('html/eventos/<int:ID_ACTIVIDAD>/$', eventos_details ,name='eventos-details'),
    path('html/publicaciones/', list_publicaciones_views, name='publicaciones-list'),
    path('html/publicaciones/detalles/<str:pk>/', publicaciones_detail_view, name='publicacion-detail'),
    path('html/nuevapublicacion/', publicaciones_formulario_view, name='publicacion-formulario'),
    path('html/nuevapublicacion/publicar', crear_publicacion, name='crear-publicacion'),
    path('html/usuarios', usuarios_list, name='usuarios-list'),
    path('html/usuarios/detalles/<str:pk>/', usuarios_detail, name='usuarios-detail'),
    path('ajax/eventos', cargar_eventos_ajax, name='cargar-eventos-ajax'),
    path('ajax/eventos/<int:ID_ACTIVIDAD>/', cargar_evento_id_ajax, name='cargar-eventos-id'),
]