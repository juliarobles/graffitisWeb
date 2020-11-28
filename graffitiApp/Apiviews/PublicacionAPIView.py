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
    
    @swagger_auto_schema(operation_description="Devuelve todos las publicaciones. \n Ejemplo: http://127.0.0.1:8000/publicaciones/",
                         responses={'200': PublicacionSerializer(many=True)})
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

    @swagger_auto_schema(operation_description='Crea una publicación. Mínimo deberá contener un graffiti y tanto el autor del graffiti como el creador de la publicación deberán ser identificadores de usuarios existentes en el sistema (Lo lógico es que sea el id del mismo usuario ya que es este el que está creando la publicación). \n Ejemplo: \n{\n"titulo": "Primer graffiti",\n"descripcion": "El primero de todos",\n"localizacion": "Malaga",\n"tematica": [\n"Perros",\n"Callejón"\n],\n"autor": "Marquitos",\n"creador": "5fbaaade48f5052d28f3dffa",\n"listaGraffitis": [\n {\n "imagen": "https://www.hola.com/imagenes/estar-bien/20190820147813/razas-perros-pequenos-parecen-grandes/0-711-550/razas-perro-pequenos-grandes-m.jpg",\n"estado": "perfecto",\n "fechaCaptura": "2020-11-26",\n "autor": "5fbaaa1c875f83f6d3cb9a9d"\n}\n]\n}',
                         responses={'201':'Publicacion creada', '400': 'Peticion mal formada'}, 
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
    
    @swagger_auto_schema(operation_description="Devuelve la publicación según el id. \n Ejemplo: id = 5fbab0abbcbecf56728297aa",
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

    @swagger_auto_schema(operation_description='Modifica una publicación existente. \n Ejemplo: id = 5fbab0abbcbecf56728297aa \n data = \n {\n"titulo": "Titulo",\n  "descripcion": "Descripcion",\n  "localizacion": "Localizacion",\n  "tematica": [\n"Gato"\n],\n  "autor": "Marco"\n}',
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

    @swagger_auto_schema(operation_description="Elimina una publicacion. Esto provocará cambios en los datos del usuario como listasComentariosPublicaciones y listasGraffitisPublicaciones  \n Ejemplo : id = 5fbab0abbcbecf56728297aa",
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
    @swagger_auto_schema(operation_description="Devuelve a todos los usuarios que hayan dado like a la publicacion actual. \n Ejemplo : \n id = 5fbab37bbcbecf56728297b0",
                         responses={200:UsuarioSerializer(many=True), '404':'Publicacion no encontrada'})
    def get(self, request, pk):
        publicacion = PublicacionDetail.get_object(request, pk)
        serializer = UsuarioSerializer(publicacion.meGusta, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description='El usuario cuyo nombre sea pasado como parametro pasará a dar me gusta a la publicación actual. Si ya le había dado me gusta, se quitará el me gusta  \n Ejemplo : \n id = 5fbab37bbcbecf56728297b0 \n data = \n{\n "usuario": "5fbaaa1c875f83f6d3cb9a9d"\n}\n',
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
    @swagger_auto_schema(operation_description="Devuelve todas las publicaciones cuyo autor contenga la cadena de texto proporcionada. \n Ejemplo: \n autor = Sonche",
                            responses={200: 'OK', 400: 'Error con la cadena enviada'})
    def get(self, request, author):
        if author:
            publicaciones = Publicacion.objects.filter(autor__contains=author)
            serializer = PublicacionSerializer(publicaciones, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error":"No se ha proporcionado un autor"}, status=status.HTTP_400_BAD_REQUEST)

class PublicacionFiltrar(APIView):
    @swagger_auto_schema(responses={200: 'OK', 404: 'Campo no existente/vacio o contenido vacio'}, operation_id="publicaciones_filtrar")
    
    def get(self, request, campo, contenido):
        """Devuelve las publicaciones que contengan la subcadena CONTENIDO en la propiedad CAMPO. 
        Campos permitidos: titulo, descripcion, creador, autor, localizacion, tematica. 
        En el caso de el creador y la localización la busqueda será EXACTA. 
        No utilizar tildes. 
        Si no encuentra ninguna publicación que corresponda con CONTENIDO, devuelve una lista vacia."""
        
        resultado = []
        print("hor")

        if(campo=='' and contenido==''):
            return Response(status= status.HTTP_404_NOT_FOUND)
        else:
            try:
                publicaciones = filtrarPor(campo, contenido)
                serializer = PublicacionSerializer(publicaciones, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except:
                return Response(status= status.HTTP_404_NOT_FOUND) 
            

def filtrarPor(campo, contenido):
    if(campo.lower() == "titulo"):
        return Publicacion.objects.filter(titulo__icontains=contenido)
    elif (campo.lower() == "descripcion"):
        return Publicacion.objects.filter(descripcion__icontains=contenido)
    elif (campo.lower() == "creador"):
        return Publicacion.objects.filter(creador__iexact=contenido)
    elif (campo.lower() == "localizacion"):
        return Publicacion.objects.filter(localizacion__iexact=contenido)
    elif (campo.lower() == "autor"):
        return Publicacion.objects.filter(autor__icontains=contenido)
    elif (campo.lower() == "tematica"):
        return Publicacion.objects.filter(tematica__icontains=contenido)
    else:
        return -1