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
from graffitiApp.Apiviews.PublicacionAPIView import PublicacionDetail
from graffitiApp.serializers import PublicacionSerializer, UsuarioSerializer, GraffitiSerializer, ComentarioSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

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