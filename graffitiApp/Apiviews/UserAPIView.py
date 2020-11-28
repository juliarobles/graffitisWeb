from enum import auto
import re
from typing import Any
from rest_framework import status
from rest_framework import serializers
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
from bson import ObjectId
from django.http import Http404
from graffitiApp.models import Publicacion, Usuario, Graffiti
from graffitiApp.serializers import PublicacionSerializer, UsuarioSerializer, GraffitiSerializer, ComentarioSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class UsuarioList(APIView):
    def get_object(self,pk):
        try:
            pk = ObjectId(pk)
            return Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            raise Http404
        
    @swagger_auto_schema(operation_description="Devuelve todos los usuarios. \n Ejemplo: http://127.0.0.1:8000/usuarios/",
                         responses={200: UsuarioSerializer(many=True), 404: 'Usuario no encontrado'})
    def get(self, request, pk=None):
        if pk: 
            pk = ObjectId(pk)
            usuario = self.get_object(pk)
            serializer = UsuarioSerializer(usuario)
            
        else:
            usuario = Usuario.objects.all()
            serializer = UsuarioSerializer(usuario, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description='Crea un nuevo usuario. \n Ejemplo: \n{\n  "usuario": "username",\n  "nombre": "prueba",\n  "email": "user@user.com",\n  "password": "passwordusername",\n  "imagen": "https://cdn.mos.cms.futurecdn.net/fvwERvZArRTyLWuMK48YuH-1200-80.jpg",\n  "descripcion": "Soy un usuario" \n }',
                         responses={201: UsuarioSerializer,
                                    400: 'Causas del error'},
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             properties={
                                 'usuario': openapi.Schema(type=openapi.TYPE_STRING),
                                 'nombre': openapi.Schema(type=openapi.TYPE_STRING),
                                 'email': openapi.Schema(type=openapi.TYPE_STRING),
                                 'password': openapi.Schema(type=openapi.TYPE_STRING),
                                 'imagen': openapi.Schema(type=openapi.TYPE_STRING),
                                 'descripcion': openapi.Schema(type=openapi.TYPE_STRING),
                             }
                         ),)
    def post(self, request, pk=None):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

class UsuarioDetail(APIView): 

    def get_object(self,pk):
        try:
            pk = ObjectId(pk)
            return Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            raise Http404
        
    @swagger_auto_schema(operation_description="Devuelve un usuario según el id. \n Ejemplo: http://127.0.0.1:8000/usuarios/5fbaabbb48f5052d28f3dffb/ ",
                         responses={200: UsuarioSerializer(many=True)})
    def get(self, request, pk=None):
        if pk: 
            pk = ObjectId(pk)
            usuario = self.get_object(pk)
            serializer = UsuarioSerializer(usuario)
            
        else:
            usuario = Usuario.objects.all()
            serializer = UsuarioSerializer(usuario, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(operation_description='Actualiza al usuario especificado.\n Ejemplo: ID = 5fbaabbb48f5052d28f3dffb  \n{\n  "usuario": "username",\n  "password": "passwordusername",\n  "imagen": "https://cdn.mos.cms.futurecdn.net/fvwERvZArRTyLWuMK48YuH-1200-80.jpg",\n  "descripcion": "Soy un usuario" \n }',
                         responses={204: UsuarioSerializer},
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             properties={
                                 'usuario': openapi.Schema(type=openapi.TYPE_STRING),
                                 'password': openapi.Schema(type=openapi.TYPE_STRING),
                                 'imagen': openapi.Schema(type=openapi.TYPE_STRING),
                                 'descripcion': openapi.Schema(type=openapi.TYPE_STRING)
                             }
                         ))
    def put(self, request, pk):
        pk = ObjectId(pk)
        usuario = self.get_object(pk)
        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_description="Borra al usuario especificado. Esta acción eliminará también elementos de las publicaciones, como comentarios, graffitis y me gusta. \n Ejemplo: ID = 5fbaabbb48f5052d28f3dffb",
                         responses={204: 'Usuario eliminado'})
    def delete(self, request, pk):
        pk = ObjectId(pk)
        usuario = self.get_object(pk)
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UsuarioFollow(APIView):
    @swagger_auto_schema(operation_description="Se devolverán todos los usuarios a los que el usuario actual sigue (id de la url). Esta acción no devolverá nada hasta que se realice el post /usuarios/id/follow \n Ejemplo: 5fbaaade48f5052d28f3dffa",
                         responses={200: UsuarioSerializer(many=True)})
    def get(self, request, pk):
        usuario = UsuarioDetail.get_object(request, pk)
        serializer = UsuarioSerializer(usuario.listaSeguidos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description='El usuario actual (id de la url) seguirá al usuario con el id pasado en la petición. En el caso de que ya lo siguiera, lo dejará de seguir. \n Ejemplo: id = 5fbaaade48f5052d28f3dffa \n data= \n {\n"usuario": "5fbaabbb48f5052d28f3dffb" \n}',
                         responses={200: UsuarioSerializer,
                                    403: 'Un usuario no puede seguirse a si mismo',
                                    404: 'Not found'},
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             properties={
                                 'usuario': openapi.Schema(type=openapi.TYPE_STRING),
                             }
                         ),)
    def post(self, request, pk):
        usuario = UsuarioDetail.get_object(request, pk)
        if request.data['usuario']:
            seguir = UsuarioDetail.get_object(request, request.data['usuario'])
            if usuario == seguir:
                return Response(data={"error": "Un usuario no puede seguirse asi mismo"},status=status.HTTP_403_FORBIDDEN)

            if seguir not in usuario.listaSeguidos: # follow
                usuario.listaSeguidos.append(seguir)
                seguir.listaSeguidores.append(usuario)
            else: # unfollow
                usuario.listaSeguidos.remove(seguir)
                seguir.listaSeguidores.remove(usuario)
            usuario.save()
            seguir.save()
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class UsuarioFollowers(APIView):
    @swagger_auto_schema(operation_description="Se devolverán todos los usuarios que siguen al usuario actual (id de la url). \nEjemplo: id = 5fbaabbb48f5052d28f3dffb",
                         responses={200: UsuarioSerializer(many=True)})
    def get(self, request, pk):
        usuario = UsuarioDetail.get_object(request, pk)
        serializer = UsuarioSerializer(usuario.listaSeguidores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UsuarioFilterName(APIView):
    @swagger_auto_schema(operation_description="Devuelve todos los usuarios que contengan en su nombre una cadena de texto.",
                            responses={200: 'OK', 400: 'Error en la cadena enviada'})
    def get(self, request, username):
        if username:
            usuarios = Usuario.objects.filter(usuario__contains=username)
            serializer = UsuarioSerializer(usuarios, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error":"No se ha proporcionado un username"}, status=status.HTTP_400_BAD_REQUEST)