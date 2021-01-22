from django.conf.urls import url,include
from django.urls import path
from clienteApp.views.views import *
from clienteApp.views.loginViews import *

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



# Paginas principales
urlpatterns = [

    # General #
    path('inicio/', inicio, name='inicio'),
    path('', principal, name='principal'),
    path('registro/', registro, name='registro'),
    path('html/politica-de-privacidad/', privacidad, name='privacidad'),
    path('html/inicio/<str:pk>/like', like_inicio, name='inicio-like'),
    path('ajax/paleta/', cargar_paleta_API, name='crear-paleta'),

    # Eventos #

    path('html/eventos/', eventos_list ,name='eventos-list'),
    path('html/eventos/<int:ID_ACTIVIDAD>/', eventos_details ,name='eventos-details'),
    path('ajax/eventos', cargar_eventos_ajax, name='cargar-eventos-ajax'),
    path('ajax/eventos/<int:ID_ACTIVIDAD>/', cargar_evento_id_ajax, name='cargar-eventos-id'),

    # Publicaciones # 

    path('html/publicaciones/', list_publicaciones_views, name='publicaciones-list'),
    path('html/publicaciones/detalles/<str:pk>/', publicaciones_detail_view, name='publicacion-detail'),
    path('html/nuevapublicacion/', publicaciones_formulario_view, name='publicacion-formulario'),
    path('html/nuevapublicacion/publicar', crear_publicacion, name='crear-publicacion'),
    path('html/publicaciones/eliminar/<str:pk>', eliminar_publicacion, name='publicacion-delete'),
    path('html/publicaciones/editar/<str:pk>/<str:gpk>', editar_publicacion, name='editar-publicacion'),
    path('html/publicaciones/detalles/<str:pk>/like', like_publicacion, name='publicacion-like'),

    # Graffitis #

    path('html/publicaciones/detalles/<str:ppk>/graffitis/<str:gpk>/delete', eliminar_graffiti, name='graffiti-delete'),
    path('html/publicacion/<str:pk>/graffiti/', graffiti_form, name='graffiti-form'),
    path('html/publicacion/<str:id_pub>/graffiti/<str:id_graf>/editar/', editar_graffiti, name='editar-graffiti'),
    path('html/publicacion/<str:id_pub>/graffiti/<str:id_graf>/guardar/', guardar_editar_graffiti, name='guardar-graffiti'),

    # Usuarios #

    path('html/usuarios', usuarios_list, name='usuarios-list'),
    path('html/usuarios/detalles/<str:pk>/', usuarios_detail, name='usuarios-detail'),
    path('html/usuarios/detalles/<str:pk>/follow/', usuario_follow, name='usuario-follow'),

    # Comentario #
    path('html/publicaciones/detalles/<str:pk>/comentarios', crear_comentario, name='crear-comentario'),
    path('html/publicaciones/detalles/<str:pk>/comentarios/<str:cpk>', delete_comentario, name='delete-comentario'),
    
]

# Login
urlpatterns += [
    path('loginInToken', action_loginInToken, name='action_loginInToken'),
    path('loginIn', action_login, name='action_login'),
    path('loginOut', action_logout, name='action_logout')
]