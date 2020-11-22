from django.conf.urls import url,include
from rest_framework import routers
from graffitiApp import views
from .apiviews import PublicacionDetail, UsuarioDetail, GraffitiList, GraffitiDetail
#from django.urls import url_include

# router = routers.DefaultRouter()
# router.register(r'Publicacion', views.PublicacionViewSet, basename="Publicacion" )
# router.register(r'Usuario', views.UsuarioViewSet, basename="Usuario" )

urlpatterns = [
    # url('', include(router.urls)), 
    url(r'^index', views.index),
    url(r'^publicaciones/$', PublicacionDetail.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/$', PublicacionDetail.as_view()),
    url(r'^usuarios/$', UsuarioDetail.as_view()),
    url(r'^usuarios/(?P<pk>[a-zA-Z0-9-]+)/$', UsuarioDetail.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/graffiti/$', GraffitiList.as_view()),
    url(r'^publicaciones/(?P<pk>[a-zA-Z0-9-]+)/graffiti/(?P<gpk>[a-zA-Z0-9-]+)$', GraffitiDetail.as_view()),
]