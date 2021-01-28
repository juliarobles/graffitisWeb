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
    
    @swagger_auto_schema(operation_description="Devuelve los graffitis. \n Ejemplo: id = 5fbab37bbcbecf56728297b0",
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

    @swagger_auto_schema(operation_description='Crea un nuevo graffiti, pasado mediante la petición, para la publicación seleccionada. \n Ejemplo: id = 5fbab37bbcbecf56728297b0\n data = \n {\n  "imagen": "https://cflvdg.avoz.es/default/2019/06/12/00121560338701711998500/Foto/i11j9026.jpg",\n"estado": "ok",\n  "fechaCaptura": "2020-11-28",\n  "autor": "5fbaaa1c875f83f6d3cb9a9d"\n}\n',
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
    
    @swagger_auto_schema(operation_description="Devuelve un graffiti de la publicación seleccionada según el id. \n Ejemplo : \n id = 5fbab37bbcbecf56728297b0 \n gpk = 5fbab37bbcbecf56728297ae",
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

    @swagger_auto_schema(operation_description="Borra el graffiti seleccionado. \n Ejemplo : \n id = 5fbab37bbcbecf56728297b0 \n gpk = 5fbab37bbcbecf56728297ae",
                         responses={204: 'Response vacía', 500: 'Una publicación debe tener al menos un graffiti'})
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

    @swagger_auto_schema(operation_description='Modifica un graffiti ya existente. \n Ejemplo : \n id = 5fbab37bbcbecf56728297b0 \n gpk = 5fbab37bbcbecf56728297ae \n data = \n {\n "imagen": "https://cflvdg.avoz.es/default/2019/06/12/00121560338701711998500/Foto/i11j9026.jpg",\n "estado": "perfecto",\n   "fechaCaptura": "2020-11-28",\n   "autor": "5fbaaade48f5052d28f3dffa"\n }\n ',
                         responses={202: GraffitiSerializer, 
                                    400: 'Bad request y causas del error'},
                         request_body=GraffitiSerializer)
    def put(self, request, pk, gpk):
        gpk = ObjectId(gpk)
        pk = ObjectId(pk)
        graffiti = self.get_object(pk,gpk)
        publicacion = PublicacionDetail.get_object(request,pk)
        index = publicacion.listaGraffitis.index(graffiti)
        publicacion.listaGraffitis.remove(graffiti)

        serializer = GraffitiSerializer(graffiti, data=request.data)
    
        if serializer.is_valid():
            serializer.save()
            publicacion.listaGraffitis.insert(index, graffiti)
            publicacion.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
