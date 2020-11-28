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
from graffitiApp.Apiviews.UserAPIView import UsuarioDetail
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class PublicacionList(APIView): 
    
    def get_object(self,pk):
        try:
            pk = ObjectId(pk)
            return Publicacion.objects.get(pk=pk)
        except Publicacion.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(responses={'200': PublicacionSerializer(many=True)})
    def get(self, request, pk=None):
        """Devuelve todas las publicaciones o una publicacion en concreto si hay un id en la url"""
        if pk: 
            pk = ObjectId(pk)
            publicacion = self.get_object(pk)
            serializer = PublicacionSerializer(publicacion)
            
        else:
            publicacion = Publicacion.objects.all()
            serializer = PublicacionSerializer(publicacion, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={'201':'Publicacion creada', '400': 'Peticion mal formada'}, 
                         request_body=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'titulo': openapi.Schema(type=openapi.TYPE_STRING),
                                    'descripcion': openapi.Schema(type=openapi.TYPE_STRING),
                                    'localizacion': openapi.Schema(type=openapi.TYPE_STRING),
                                    'tematica': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                                    'autor': openapi.Schema(type=openapi.TYPE_STRING),
                                    'creador': openapi.Schema(type=openapi.TYPE_STRING),
                                    'listaGraffitis': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                                        'imagen': openapi.Schema(type=openapi.TYPE_STRING),
                                        'estado': openapi.Schema(type=openapi.TYPE_STRING),
                                        'fechaCaptura':openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                                        'autor': openapi.Schema(type=openapi.TYPE_STRING)}))
                                }
                            ),
                            )
    def post(self, request, pk=None):
        """Permite crear una nueva publicacion, que deberá seguir el formato especificado. 
        Los cambos listaComentarios y meGusta deberán dejarse como listas vacías([]), mínimo deberá contener un graffiti y tanto el autor del graffiti como el creador de la publicación deberán ser identificadores de usuarios existentes en el sistema (Lo lógico es que sea el id del mismo usuario ya que es este el que está creando la publicación)."""
        serializer = PublicacionSerializer(data=request.data)
        if serializer.is_valid():
            publicacion = serializer.save() # Guardar la publicacion
           
            # Actualizar los campos de los usuarios
            publicacion.creador.listaPublicaciones.append(publicacion)
            publicacion.creador.save()

            # Actualizar Graffiti...
            for graffiti in publicacion.listaGraffitis:
                graffiti.autor.listaGraffitisPublicaciones.append(publicacion)
                graffiti.autor.save()

            # Actualizar Comentarios...
            for comentario in publicacion.listaComentarios:
                comentario.autor.listaComentariosPublicaciones.append(publicacion)
                comentario.autor.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicacionDetail(APIView): 
    
    def get_object(self,pk):
        try:
            pk = ObjectId(pk)
            return Publicacion.objects.get(pk=pk)
        except Publicacion.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(operation_description="Devuelve la publicación según el id.",
                         responses={200: PublicacionSerializer})
    def get(self, request, pk=None):
        if pk: 
            pk = ObjectId(pk)
            publicacion = self.get_object(pk)
            serializer = PublicacionSerializer(publicacion)
            
        else:
            publicacion = Publicacion.objects.all()
            serializer = PublicacionSerializer(publicacion, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Modifica una publicación existente. Para ello es recomendable que solo se incluyan los campos que van a ser modificados. NO modificar listaComentarios, listaGraffitis y meGusta ya que existen métodos específicos para ello que aseguran mantener la consistencia del sistema.",
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             properties={
                                 'titulo': openapi.Schema(type=openapi.TYPE_STRING),
                                 'descripcion': openapi.Schema(type=openapi.TYPE_STRING),
                                 'localizacion': openapi.Schema(type=openapi.TYPE_STRING),
                                 'tematica': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                                 'autor': openapi.Schema(type=openapi.TYPE_STRING),
                             }
                         ),
                         responses={202: "Modificación aceptada",
                                    400: "Error y sus causas"})
    def put(self, request, pk):
        pk = ObjectId(pk)
        publicacion = self.get_object(pk)
        publicacion.creador.listaPublicaciones.remove(publicacion)
        
        serializer = PublicacionSerializer(publicacion, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            publicacion.creador.listaPublicaciones.append(publicacion)
            publicacion.creador.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_description="Elimina una publicacion.",
                            responses={'204':'Publicacion Eliminada', 
                                       '404':'Publicacion no encontrada'})
    def delete(self, request, pk):
        pk = ObjectId(pk)
        publicacion = self.get_object(pk)
        # Actualizar la lista de publicaciones del creador
        publicacion.creador.listaPublicaciones.remove(publicacion)
        publicacion.creador.save()

        # Actualizar la lista de graffitis de cada usuario relacionado
        for graffiti in publicacion.listaGraffitis:
            graffiti.autor.listaGraffitisPublicaciones.remove(publicacion)
            graffiti.autor.save()

        for comentario in publicacion.listaComentarios:
            comentario.autor.listaComentariosPublicaciones.remove(publicacion)
            comentario.autor.save()

        publicacion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicacionLike(APIView):
    @swagger_auto_schema(operation_description="Devuelve a todos los usuarios que hayan dado like a la publicacion actual.",
                         responses={200:UsuarioSerializer(many=True), '404':'Publicacion no encontrada'})
    def get(self, request, pk):
        publicacion = PublicacionDetail.get_object(request, pk)
        serializer = UsuarioSerializer(publicacion.meGusta, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="El usuario cuyo nombre sea pasado como parametro pasará a dar me gusta a la publicación actual.",
                         responses={200: UsuarioSerializer,
                                    400: 'Bad request',
                                    404: 'Publicacion no encontrada'},
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             properties={
                                 'usuario': openapi.Schema(type=openapi.TYPE_STRING),
                             }
                         ),)
    def post(self, request, pk):
        publicacion = PublicacionDetail.get_object(request, pk)
        if request.data['usuario']:
            usuario = UsuarioDetail.get_object(request, request.data['usuario'])
            if usuario not in publicacion.meGusta: # like de la publicacion
                publicacion.meGusta.append(usuario)
            else: # quitar dislike de la publicacion
                publicacion.meGusta.remove(usuario)
            publicacion.save()
            serializer = PublicacionSerializer(publicacion)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class PublicacionFilterAuthor(APIView):
    @swagger_auto_schema(operation_description="Devuelve todas las publicaciones cuyo autor contenga la cadena de texto proporcionada.",
                            responses={200: 'OK', 400: 'Error con la cadena enviada'})
    def get(self, request, author):
        if author:
            publicaciones = Publicacion.objects.filter(autor__contains=author)
            serializer = PublicacionSerializer(publicaciones, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error":"No se ha proporcionado un autor"}, status=status.HTTP_400_BAD_REQUEST)