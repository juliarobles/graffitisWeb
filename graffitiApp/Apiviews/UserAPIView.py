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
from graffitiApp.serializers import PublicacionSerializer, UsuarioSerializer, GraffitiSerializer, ComentarioSerializer, UsuarioIdSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class UsuarioList(APIView):
    def get_object(self,pk):
        try:
            pk = ObjectId(pk)
            return Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            raise Http404
        
    @swagger_auto_schema(operation_description="Devuelve todos los usuarios o uno en concreto se se recibe un id.",
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

    @swagger_auto_schema(operation_description="Crea un nuevo usuario.",
                         responses={201: UsuarioSerializer,
                                    400: 'Causas del error'},
                         request_body=UsuarioSerializer)
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
        
    @swagger_auto_schema(operation_description="Devuelve un usuario según el id.",
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


    @swagger_auto_schema(operation_description="Actualiza al usuario especificado",
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

    @swagger_auto_schema(operation_description="Borra al usuario especificado",
                         responses={204: 'Usuario eliminado'})
    def delete(self, request, pk):
        pk = ObjectId(pk)
        usuario = self.get_object(pk)
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UsuarioFollow(APIView):
    @swagger_auto_schema(operation_description="Se devuelven todos los usuarios a los que el usuario actual sigue.",
                         responses={200: UsuarioSerializer(many=True)})
    def get(self, request, pk):
        usuario = UsuarioDetail.get_object(request, pk)
        serializer = UsuarioSerializer(usuario.listaSeguimiento, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="El usuario actual seguirá al usuario pasado en la petición.",
                         responses={200: UsuarioSerializer,
                                    403: 'Un usuario no puede seguirse a si mismo',
                                    404: 'Not found'},
                         request_body=UsuarioIdSerializer)
    def post(self, request, pk):
        usuario = UsuarioDetail.get_object(request, pk)
        if request.data['usuario']:
            seguir = UsuarioDetail.get_object(request, request.data['usuario'])
            if usuario == seguir:
                return Response(data={"error": "Un usuario no puede seguirse asi mismo"},status=status.HTTP_403_FORBIDDEN)

            if seguir not in usuario.listaSeguimiento: # follow
                usuario.listaSeguimiento.append(seguir)
            else: # unfollow
                usuario.listaSeguimiento.remove(seguir)
            usuario.save()
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class UsuarioFilterName(APIView):
    @swagger_auto_schema(operation_description="Devuelve todos los usuarios que contengan en su nombre una cadena de texto.",
                            responses={200: 'OK', 400: 'Error en la cadena enviada'})
    def get(self, request, username):
        if username:
            usuarios = Usuario.objects.filter(usuario__contains=username)
            serializer = UsuarioSerializer(usuarios, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error":"No se ha proporcionado un username"}, status=status.HTTP_400_BAD_REQUEST)