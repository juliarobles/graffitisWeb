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
from .models import Publicacion, Usuario, Graffiti
from .serializers import PublicacionSerializer, UsuarioSerializer, GraffitiSerializer, ComentarioSerializer, UsuarioIdSerializer
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
                         request_body=PublicacionSerializer)
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
    @swagger_auto_schema(operation_description="Devuelve a todos los usuarios a los que les guste la publicacion.",
                         responses={200:UsuarioSerializer(many=True), '404':'Publicacion no encontrada'})
    def get(self, request, pk):
        publicacion = PublicacionDetail.get_object(request, pk)
        serializer = UsuarioSerializer(publicacion.meGusta, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="El usuario pasado como parametro pasará a dar me gusta a la publicación.",
                         responses={200: UsuarioSerializer,
                                    400: 'Bad request',
                                    404: 'Publicacion no encontrada'},
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['usuario_id'],
                             properties={
                                 'usuario_id': openapi.Schema(type=openapi.TYPE_STRING)
                             }
                         ))
    def post(self, request, pk):
        publicacion = PublicacionDetail.get_object(request, pk)
        if request.data['usuario_id']:
            usuario = UsuarioDetail.get_object(request, request.data['usuario_id'])
            if usuario not in publicacion.meGusta: # like de la publicacion
                publicacion.meGusta.append(usuario)
            else: # quitar dislike de la publicacion
                publicacion.meGusta.remove(usuario)
            publicacion.save()
            serializer = PublicacionSerializer(publicacion)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST) 

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
    def get(self, request, pk):
        usuario = UsuarioDetail.get_object(request, pk)
        serializer = UsuarioSerializer(usuario.listaSeguimiento, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="El usuario actual seguirá al usuario pasado en la petición.",
                         responses={200: UsuarioSerializer,
                                    403: 'Un usuario no puede seguirse a si mismo',
                                    404: 'Not found'},
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['usuario_id'],
                             properties={
                                 'usuario_id': openapi.Schema(type=openapi.TYPE_STRING)
                             }
                         ))
    def post(self, request, pk):
        usuario = UsuarioDetail.get_object(request, pk)
        if request.data['usuario_id']:
            seguir = UsuarioDetail.get_object(request, request.data['usuario_id'])
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

class ComentarioList(APIView):
    #serializer_class = PublicacionSerializer
    def get_object(self,pk, cpk=None):
        try:
            pk = ObjectId(pk)
            publicacion = Publicacion.objects.get(pk=pk)
            comentario = publicacion.listaComentarios.get(_id=cpk)
            return comentario
        except Publicacion.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(operation_description="Devuelve todos los comentarios realizados en la publicación actual.",
                         responses={200: ComentarioSerializer(many=True), 404:'Publicacion o Comentario no encontrado'})
    def get(self, request, pk, cpk=None):
        pk = ObjectId(pk)
        if cpk:
            cpk = ObjectId(cpk)
            comentario = self.get_object(pk,cpk)
            serializer = ComentarioSerializer(comentario)
        else:
            comentario = Publicacion.objects.get(pk=pk).listaComentarios
            serializer = ComentarioSerializer(comentario, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Crea un nuevo comentario, pasado mediante la petición, para la publicación seleccionada.",
                         responses={201: ComentarioSerializer,
                                    400: 'Causas del error',
                                    404: 'Publicacion no encontrada'},
                         request_body=ComentarioSerializer)
    def post(self, request, pk=None):
        serializer = ComentarioSerializer(data=request.data)
        publicacion = PublicacionDetail.get_object(request, pk)
        if serializer.is_valid():
            publicacion.listaComentarios.append(serializer.save())
            publicacion.save()
            serializer.instance.autor.listaComentariosPublicaciones.append(publicacion)
            serializer.instance.autor.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    


class ComentarioDetail(APIView):
    #serializer_class = PublicacionSerializer
    def get_object(self,pk, cpk=None):
        try:
            pk = ObjectId(pk)
            publicacion = Publicacion.objects.get(pk=pk)
            comentario = publicacion.listaComentarios.get(_id=cpk)
            return comentario
        except Publicacion.DoesNotExist:
            raise Http404
    
    @swagger_auto_schema(operation_description="Devuelve un comentario de la publicación actual según el id.",
                         responses={200: ComentarioSerializer(many=True)})
    def get(self, request, pk, cpk=None):
        pk = ObjectId(pk)
        if cpk:
            cpk = ObjectId(cpk)
            comentario = self.get_object(pk,cpk)
            serializer = ComentarioSerializer(comentario)
        else:
            comentario = Publicacion.objects.get(pk=pk).listaComentarios
            serializer = ComentarioSerializer(comentario, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Borra el comentario seleccionado.",
                         responses={204: 'Response vacía', 404: 'Comentario o publicacion no encontrado'})
    def delete(self, request, pk, cpk):
        pk = ObjectId(pk)
        gpk = ObjectId(cpk)
        comentario = self.get_object(pk, gpk)
        publicacion = Publicacion.objects.get(pk=pk)
        comentario.autor.listaComentariosPublicaciones.remove(publicacion)
        comentario.autor.save()
        publicacion.listaComentarios.remove(comentario)
        publicacion.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

        
class GraffitiList(APIView):
    def get_object(self, pk, gpk):
        try:
            pk = ObjectId(pk)
            gpk = ObjectId(gpk)
            publicacion = Publicacion.objects.get(pk=pk)
            graffitis = publicacion.listaGraffitis.get(_id=gpk)
            return graffitis
        except Publicacion.DoesNotExist:  #esto
            raise Http404
    
    @swagger_auto_schema(operation_description="Devuelve los graffitis o un graffiti concreto de la publicación seleccionada",
                         responses={200: GraffitiSerializer, 404: 'Publicacion o Graffiti no encontrado'})
    def get(self, request, pk, gpk=None):
        if gpk: 
            pk = ObjectId(pk)
            gpk = ObjectId(gpk)
            graffiti = self.get_object(pk, gpk)
            serializer = GraffitiSerializer(graffiti)
                
        else:
            pk = ObjectId(pk)
            graffiti = Publicacion.objects.get(pk=pk).listaGraffitis
            serializer = GraffitiSerializer(graffiti, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Crea un nuevo graffiti, pasado mediante la petición, para la publicación seleccionada.",
                         responses={201: GraffitiSerializer,
                                    400: 'Causas del error',
                                    404: 'Publicacion no encontrada'},
                         request_body=GraffitiSerializer)
    def post(self, request, pk, gpk=None):

        serializer = GraffitiSerializer(data=request.data)
        publicacion = PublicacionDetail.get_object(request, pk)
        if serializer.is_valid():
            publicacion.listaGraffitis.append(serializer.save())
            publicacion.save()
            serializer.instance.autor.listaGraffitisPublicaciones.append(publicacion)
            serializer.instance.autor.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GraffitiDetail(APIView):
    def get_object(self, pk, gpk):
        try:
            pk = ObjectId(pk)
            gpk = ObjectId(gpk)
            publicacion = Publicacion.objects.get(pk=pk)
            graffitis = publicacion.listaGraffitis.get(_id=gpk)
            return graffitis
        except Publicacion.DoesNotExist:  #esto
            raise Http404
    
    @swagger_auto_schema(operation_description="Devuelve un graffiti de la publicación seleccionada según el id.",
                         responses={200: GraffitiSerializer}) 
    def get(self, request, pk, gpk=None):
        if gpk: 
            pk = ObjectId(pk)
            gpk = ObjectId(gpk)
            graffiti = self.get_object(pk, gpk)
            serializer = GraffitiSerializer(graffiti)
                
        else:
            pk = ObjectId(pk)
            graffiti = Publicacion.objects.get(pk=pk).listaGraffitis
            serializer = GraffitiSerializer(graffiti, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Borra el graffiti seleccionado.",
                         responses={204: 'Response vacía'})
    def delete(self, request, pk, gpk):
        pk = ObjectId(pk)
        gpk = ObjectId(gpk)
        graffiti = self.get_object(pk,gpk)
        publicacion = Publicacion.objects.get(pk=pk)
        graffiti.autor.listaGraffitisPublicaciones.remove(publicacion)
        graffiti.autor.save()
        publicacion.listaGraffitis.remove(graffiti)
        publicacion.save()

       
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(operation_description="Modifica un graffiti ya existente.",
                         responses={202: GraffitiSerializer, 
                                    400: 'Bad request y causas del error'},
                         request_body=GraffitiSerializer)
    def put(self, request, pk, gpk):
        gpk = ObjectId(gpk)
        pk = ObjectId(pk)
        graffiti = self.get_object(pk,gpk)
        publicacion = PublicacionDetail.get_object(request,pk)
        publicacion.listaGraffitis.remove(graffiti)

        serializer = GraffitiSerializer(graffiti, data=request.data)
        

        if serializer.is_valid():
            serializer.save()
            publicacion.listaGraffitis.append(graffiti)
            publicacion.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
#    {
#     "imagen": "http://www.imaaaaagen.com/",
#     "estado": "ok",
#     "fechaCaptura": "2020-05-06",
#     "autor": "5fb8e5cbb2abaebd2dd2b735"
# }

# Consultas parametrizadas
class UsuarioFilterName(APIView):
    @swagger_auto_schema(operation_description="Devuelve todos los usuarios que contengan en su nombre una cadena de texto.",
                            responses={200: 'OK', 400: 'Error en la cadena enviada'})
    def get(self, request, username):
        if username:
            usuarios = Usuario.objects.filter(usuario__contains=username)
            serializer = UsuarioSerializer(usuarios, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error":"No se ha proporcionado un username"}, status=status.HTTP_400_BAD_REQUEST)

class PublicacionFilterAuthor(APIView):
    @swagger_auto_schema(operation_description="Devuelve todas las publicaciones cuyo autor contenga la cadena de texto proporcionada.",
                            responses={200: 'OK', 400: 'Error con la cadena enviada'})
    def get(self, request, author):
        if author:
            publicaciones = Publicacion.objects.filter(autor__contains=author)
            serializer = PublicacionSerializer(publicaciones, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error":"No se ha proporcionado un autor"}, status=status.HTTP_400_BAD_REQUEST)
            