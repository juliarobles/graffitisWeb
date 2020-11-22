from enum import auto
from rest_framework import status
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
from bson import ObjectId
from django.http import Http404
from .models import Publicacion, Usuario, Graffiti
from .serializers import PublicacionSerializer, UsuarioSerializer, GraffitiSerializer, ComentarioSerializer

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
            publicacion = self.get_object(pk)
            serializer = PublicacionSerializer(publicacion)
            
        else:
            publicacion = Publicacion.objects.all()
            serializer = PublicacionSerializer(publicacion, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk=None):
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

    def put(self, request, pk):
        pk = ObjectId(pk)
        publicacion = self.get_object(pk)
        serializer = PublicacionSerializer(publicacion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


class UsuarioDetail(APIView): 

    def get_object(self,pk):
        try:
            pk = ObjectId(pk)
            return Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            raise Http404

    def get(self, request, pk=None):
        if pk: 
            pk = ObjectId(pk)
            usuario = self.get_object(pk)
            serializer = UsuarioSerializer(usuario)
            
        else:
            usuario = Usuario.objects.all()
            serializer = UsuarioSerializer(usuario, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk=None):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        pk = ObjectId(pk)
        usuario = self.get_object(pk)
        serializer = UsuarioSerializer(usuario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        pk = ObjectId(pk)
        usuario = self.get_object(pk)
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

    def post(self, request, pk, gpk=None):

        serializer = GraffitiSerializer(data=request.data)
        publicacion = PublicacionDetail.get_object(request, pk)
        if serializer.is_valid():
            publicacion.listaGraffitis.append(serializer.save())
            publicacion.save()
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