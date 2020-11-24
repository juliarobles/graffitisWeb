from rest_framework_mongoengine import serializers, fields as field 
from rest_framework import fields
from .models import Publicacion, Usuario, Graffiti, Comentario

class UsuarioSerializer(serializers.DocumentSerializer):
    class Meta:
        ref_name = 'Usuario'
        model = Usuario
        fields = '__all__'

class GraffitiSerializer(serializers.EmbeddedDocumentSerializer):
    class Meta:
        model = Graffiti
        fields = '__all__'
    
    def to_representation(self, instance):
        self.fields['autor'] = UsuarioSerializer()
        return super(GraffitiSerializer, self).to_representation(instance)

class ComentarioSerializer(serializers.EmbeddedDocumentSerializer):
    class Meta:
        model = Comentario
        fields = '__all__'
    
    def to_representation(self, instance):
        self.fields['autor'] = UsuarioSerializer()
        return super(ComentarioSerializer, self).to_representation(instance)

class PublicacionSerializer(serializers.DocumentSerializer):
    listaComentarios = ComentarioSerializer(many=True)
    listaGraffitis = GraffitiSerializer(many=True)
    class Meta:
        model = Publicacion
        fields = '__all__'