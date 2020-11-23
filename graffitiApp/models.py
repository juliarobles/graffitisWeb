from mongoengine import Document, EmbeddedDocument, fields, CASCADE
from django.contrib.auth.models import User

class Usuario(Document):
    usuario = fields.StringField(required=True, max_length=30)
    password = fields.StringField(required=True, min_length=8)
    imagen = fields.URLField(required=False)
    descripcion = fields.StringField(max_length=500)
    listaSeguimiento = fields.ListField(fields.ReferenceField('Usuario'))
    listaPublicaciones = fields.ListField(fields.ReferenceField('Publicacion'))
    listaComentariosPublicaciones = fields.ListField(fields.ReferenceField('Publicacion'))
    listaGraffitisPublicaciones = fields.ListField(fields.ReferenceField('Publicacion'))

    # def __str__(self):
    #     return 

class Graffiti(EmbeddedDocument):
    _id = fields.ObjectIdField(required=True, default=lambda: fields.ObjectId())
    imagen = fields.URLField(required=True)
    estado = fields.StringField(required=True) #poner enumerado
    fechaCaptura = fields.DateField(required=True)
    autor = fields.ReferenceField(Usuario, required = True)

class Comentario(EmbeddedDocument):
    _id = fields.ObjectIdField(required=True, default=lambda: fields.ObjectId())
    texto = fields.StringField(max_length=200, required=True)
    autor = fields.ReferenceField(Usuario, required=True) #reverse_delete_rule = CASCADE -> HACER A MANO

class Publicacion(Document):
    titulo = fields.StringField(max_length=100, required=True, null=False)
    descripcion = fields.StringField(max_length=500)
    localizacion = fields.StringField(max_length=50, required=True)
    tematica = fields.ListField(fields.StringField(max_length=30))
    autor = fields.StringField(max_length=50)
    listaComentarios = fields.EmbeddedDocumentListField(Comentario)
    meGusta = fields.ListField(fields.ReferenceField(Usuario, reverse_delete_rule=CASCADE))
    creador = fields.ReferenceField(Usuario, reverse_delete_rule=CASCADE, required=True)
    listaGraffitis = fields.EmbeddedDocumentListField(Graffiti, required=True)

    #def __str__(self):
    #    return self.titulo

Usuario.register_delete_rule(Usuario, "listaSeguimiento", CASCADE)
Usuario.register_delete_rule(Publicacion, "listaComentariosPublicaciones", CASCADE)
Usuario.register_delete_rule(Publicacion, "listaGraffitisPublicaciones", CASCADE)
Usuario.register_delete_rule(Publicacion, "listaPublicaciones", CASCADE)
