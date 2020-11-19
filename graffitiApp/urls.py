from django.urls import path, include
from rest_framework import routers
from graffitiApp import views
from graffitiApp.apiviews import PublicacionDetail
#from django.urls import url_include

# router = routers.DefaultRouter()
# router.register(r'Publicacion', views.PublicacionViewSet, basename="Publicacion" )

# urlpatterns = [
#     url('', include(router.urls)), 
#     url(r'^index', views.index),
#     url('/Publicacion', PublicacionDetail.as_view()),

# ]