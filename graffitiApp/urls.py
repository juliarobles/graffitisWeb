from django.conf.urls import url,include
from rest_framework import routers
from graffitiApp import views
from ayuntamientoApp.views import leer_objeto
from graffitiApp.apiviews import PublicacionDetail, UsuarioDetail, GraffitiDetail
#from django.urls import url_include

router = routers.DefaultRouter()
router.register(r'publicaciones', views.PublicacionViewSet, basename="Publicacion" )
router.register(r'usuarios', views.UsuarioViewSet, basename="Usuario" )

urlpatterns = [
    url('', include(router.urls)), 
    url(r'^index', views.index),
    url(r'^publicaciones/$', PublicacionDetail.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/$', PublicacionDetail.as_view()),
    url(r'^usuarios/$', UsuarioDetail.as_view()),
    url(r'^usuarios/(?P<pk>[a-zA-Z0-9-]+)/$', UsuarioDetail.as_view()),
    

    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/graffiti/$', GraffitiDetail.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/graffiti/(?P<gpk>[a-zA-Z0-9-]+)$', GraffitiDetail.as_view()),
    url('pruebas/', leer_objeto)
]