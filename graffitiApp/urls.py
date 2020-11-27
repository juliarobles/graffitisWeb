from django.conf.urls import url,include
from rest_framework import routers
from .views import index, PublicacionViewSet, UsuarioViewSet, list_publicaciones_views, publicaciones_detail_view
#API Views
from .Apiviews.UserAPIView import UsuarioFollow, UsuarioFollowers, UsuarioList, UsuarioDetail, UsuarioFilterName
from .Apiviews.PublicacionAPIView import PublicacionDetail, PublicacionList, PublicacionLike, PublicacionFiltrar
from .Apiviews.GraffitiAPIView import GraffitiList, GraffitiDetail
from .Apiviews.ComentarioAPIView import ComentarioList, ComentarioDetail
from django.urls import path
# De momento no usamos routers
# --------------------------------------
#from django.urls import url_include

# router = routers.DefaultRouter()
# router.register(r'Publicacion', views.PublicacionViewSet, basename="Publicacion" )
# router.register(r'Usuario', views.UsuarioViewSet, basename="Usuario" )
# --------------------------------------

urlpatterns = [


    
    # url('', include(router.urls)), 
    url(r'^index', index),
    url(r'^publicaciones/$', PublicacionList.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/$', PublicacionDetail.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/like$', PublicacionLike.as_view()),
    url(r'^usuarios/$', UsuarioList.as_view()),
    url(r'^usuarios/(?P<pk>[a-zA-Z0-9-]+)/$', UsuarioDetail.as_view()),
    url(r'^usuarios/(?P<pk>[a-zA-Z0-9-]+)/follow$', UsuarioFollow.as_view()),
    url(r'^usuarios/(?P<pk>[a-zA-Z0-9-]+)/followers$', UsuarioFollowers.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/graffitis/$', GraffitiList.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/graffitis/(?P<gpk>[a-zA-Z0-9-]+)$', GraffitiDetail.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/comentarios/$', ComentarioList.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/comentarios/(?P<cpk>[a-zA-Z0-9-]+)$', ComentarioDetail.as_view()),
    url(r'^usuarios/username/(?P<username>[a-zA-Z0-9-]+)/$', UsuarioFilterName.as_view()),
    url(r'^publicaciones/(?P<campo>[a-zA-Z0-9-_]+)/(?P<contenido>[a-zA-Z0-9-_]+)$', PublicacionFiltrar.as_view())



    path('inicio/', inicio, name='inicio'),
    path('html/eventos/', eventos_list ,name='eventos-list'),
    path('html/eventos/{int:ID_ACTIVIDAD}', eventos_list ,name='eventos-details'),
    path('html/publicaciones/', list_publicaciones_views, name='publicaciones-list'),
    path('html/publicaciones/detalles/<str:pk>/', publicaciones_detail_view, name='publicacion-detail'),
    path('html/usuarios', usuarios_list, name='usuarios-list'),
    path('html/usuarios/detalles/<str:pk>/', usuarios_detail, name='usuarios-detail'),
]