from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
from bson import ObjectId
from django.http import Http404
from graffitiApp.models import Publicacion, Usuario
from graffitiApp.serializers import PublicacionSerializer, UsuarioSerializer


class PublicacionDetail(APIView): 

    def get_object(self,pk):
        try:
            pk = ObjectId(pk)
            return Publicacion.objects.get(pk=pk)
        except Publicacion.DoesNotExist:
            raise Http404

    def get(self, request, pk=None):
        if pk: 
            pk = ObjectId(pk)
            publicacion = self.get_object(pk=pk)
            serializer = PublicacionSerializer(publicacion)
            publicacion
       # else:
            #publicacion = Publicacion
            #serializer = PublicacionSerializer(publicacion, many=True)
        #return Response(serializer.data, status=status.HTTP_200_OK)