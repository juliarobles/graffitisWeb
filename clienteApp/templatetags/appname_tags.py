from django import template
register = template.Library()

#https://stackoverflow.com/questions/12893873/get-object-id-of-document-already-in-mongodb-collection-in-python(no encontraba el id de los documentos embebidos)
@register.filter("mongo_id")
def mongo_id(value):
    return str(value['_id'])