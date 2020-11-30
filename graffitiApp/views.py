from django.shortcuts import render
from rest_framework import serializers
from rest_framework_mongoengine import viewsets
from .serializers import PublicacionSerializer, UsuarioSerializer, GraffitiSerializer
from .models import Publicacion, Usuario, Graffiti
from django.http import HttpResponse
from bson import ObjectId
from django.template.loader import get_template
from django.template import Context
import urllib3, json

def index(request):
        return HttpResponse('Success')

# Create your views here.
# Esta cosa no se usa no se si quitarlo o no
class PublicacionViewSet(viewsets.ModelViewSet):

    lookup_field = 'id'
    serializer_class = PublicacionSerializer

    def get_queryset(self):
        return Publicacion.objects.all()

class UsuarioViewSet(viewsets.ModelViewSet):

    lookup_field = 'id'
    serializer_class = UsuarioSerializer

    def get_queryset(self):
        return Usuario.objects.all()


class GraffitiViewSet(viewsets.ModelViewSet):

    lookup_field = 'id'
    serializer_class = GraffitiSerializer

    def get_queryset(self):
        return Graffiti.objects.all()