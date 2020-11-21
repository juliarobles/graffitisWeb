from django.shortcuts import render
from rest_framework_mongoengine import viewsets
from graffitiApp.serializers import PublicacionSerializer, UsuarioSerializer
from graffitiApp.models import Publicacion, Usuario
from django.http import HttpResponse

# Create your views here.


def index(request):
        return HttpResponse('Success')


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