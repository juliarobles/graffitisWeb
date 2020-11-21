from django_mongoengine import mongo_admin as admin
from .models import Publicacion, Usuario, Graffiti

# Register your models here.
admin.site.register(Publicacion)
admin.site.register(Usuario)
