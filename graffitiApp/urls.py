from django.conf.urls import url,include
from rest_framework import routers
from .views import index, PublicacionViewSet, UsuarioViewSet
from .apiviews import PublicacionDetail, UsuarioDetail, GraffitiList, GraffitiDetail, ComentarioDetail, PublicacionLike, UsuarioFollow, PublicacionList, UsuarioList, ComentarioList

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
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/graffitis/$', GraffitiList.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/graffitis/(?P<gpk>[a-zA-Z0-9-]+)$', GraffitiDetail.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/comentarios/$', ComentarioList.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/comentarios/(?P<cpk>[a-zA-Z0-9-]+)$', ComentarioDetail.as_view()),
]