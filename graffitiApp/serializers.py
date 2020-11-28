from rest_framework_mongoengine import serializers, fields as field 
from rest_framework import fields
from .models import Publicacion, Usuario, Graffiti, Comentario

class UsuarioSerializer(serializers.DocumentSerializer):
    class Meta:
        ref_name = 'Usuario'
        model = Usuario
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.usuario = validated_data.get('usuario', instance.usuario)
        instance.password = validated_data.get('password', instance.password)
        instance.imagen = validated_data.get('imagen', instance.imagen)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
        instance.save()
        return instance

class UsuarioIdSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Usuario
        fields = ['usuario']


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
    listaComentarios = ComentarioSerializer(many=True, required=False)
    listaGraffitis = GraffitiSerializer(many=True)
    class Meta:
        model = Publicacion
        fields = '__all__'

    def create(self, validated_data):
        return Publicacion.objects.create(**validated_data)

    def update(self, instance, validated_data):


        instance.titulo = validated_data.get('titulo', instance.titulo)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
        instance.localizacion = validated_data.get('localizacion', instance.localizacion)
        instance.tematica = validated_data.get('tematica', instance.tematica)
        instance.autor = validated_data.get('autor', instance.autor)
        instance.meGusta = validated_data.get('meGusta', instance.meGusta)
        instance.creador = validated_data.get('creador', instance.creador)
        instance.save()

        return instance