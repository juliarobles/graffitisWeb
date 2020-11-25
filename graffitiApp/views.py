from django.shortcuts import render
from rest_framework import serializers
from rest_framework_mongoengine import viewsets
from .serializers import PublicacionSerializer, UsuarioSerializer, GraffitiSerializer
from .models import Publicacion, Usuario, Graffiti
from django.http import HttpResponse
from bson import ObjectId

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


class GraffitiViewSet(viewsets.ModelViewSet):

    lookup_field = 'id'
    serializer_class = GraffitiSerializer

    def get_queryset(self):
        return Graffiti.objects.all()

def base_view(request):
    return render(request, 'graffiti_list.html')

def list_publicaciones_views(request):
    publicaciones = Publicacion.objects.all()
    context = {
        "publicaciones": publicaciones
    }
    return render(request, 'publicaciones_list.html', context=context)

def publicaciones_detail_view(request, pk):
    pk = ObjectId(pk)
    publicacion = Publicacion.objects.get(pk=pk)
    context = {
        "publicacion": publicacion,
        "meGusta": len(publicacion.meGusta)
    }
    return render(request, 'publicacion_detail.html', context=context)

def usuarios_list(request):
    usuarios = Usuario.objects.all()
    context = {
        "usuarios": usuarios
    }
    return render(request, 'usuarios_list.html', context=context)

def usuarios_detail(request, pk):
    pk = ObjectId(pk)
    usuario = Usuario.objects.get(pk=pk)
    seguidores = Usuario.objects.filter(listaSeguimiento__contains=usuario)
    context = {
        "usuario": usuario,
        "seguidos": len(usuario.listaSeguimiento),
        "seguidores": len(seguidores)
    }
    return render(request, 'usuarios_detail.html', context=context)