from django.conf.urls import url,include
from rest_framework import routers
from graffitiApp import views
from .apiviews import PublicacionDetail, UsuarioDetail
#from django.urls import url_include

# router = routers.DefaultRouter()
# router.register(r'Publicacion', views.PublicacionViewSet, basename="Publicacion" )
# router.register(r'Usuario', views.UsuarioViewSet, basename="Usuario" )

urlpatterns = [
    # url('', include(router.urls)), 
    url(r'^index', views.index),
    url(r'^Publicacion/$', PublicacionDetail.as_view()),
    url(r'^Publicacion/(?P<pk>[a-zA-Z0-9-]+)/$', PublicacionDetail.as_view()),
    url(r'^Usuario/$', UsuarioDetail.as_view()),
    url(r'^Usuario/(?P<pk>[a-zA-Z0-9-]+)/$', UsuarioDetail.as_view()),
]