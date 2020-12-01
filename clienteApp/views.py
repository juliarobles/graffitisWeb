from django.shortcuts import render
from graffitiApp.models import Publicacion, Usuario, Graffiti #No deberiamos usar esto
from django.http import HttpResponse
from bson import ObjectId
from django.template.loader import get_template
from django.template import Context
from django.http import HttpRequest
import urllib3, json

def eliminar_eventos_repetidos(lista):
    # AYUNTAMIENTO CUTREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
    ids = []
    res = []
    nombres = []
    for elem in lista:
        if elem['ID_ACTIVIDAD'] not in ids and elem['NOMBRE'] not in nombres:
            elem['NOMBRE'] = limpiar_nombre(elem['NOMBRE'])
            res.append(elem)
            ids.append(elem['ID_ACTIVIDAD']) 
            nombres.append(elem['NOMBRE'])
    return res

def limpiar_nombre(cadena):
    # AYUNTAMIENTO MUY CUTREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
    if('<b>' in cadena or '<B>' in cadena or '<BR>'in cadena ):
        cadena = cadena.replace('<b>', '').replace('</b>', '')
        cadena = cadena.replace('<B>', '').replace('</B>', '')
        cadena = cadena.replace('<BR>', '')
    return cadena

# Prueba mover a app cliente
def inicio(request):
    t = get_template('inicio.html')
    res = t.render()
    return HttpResponse(res)

def eventos_details(request, ID_ACTIVIDAD):
    http = urllib3.PoolManager()
    r = http.request(
        'GET',
         'http://127.0.0.1:8000/eventosID/' + str(ID_ACTIVIDAD),
    )
    context={'evento':json.loads(r.data)}
    if 'NOMBRE' in context['evento']:
        context['evento']['NOMBRE'] = limpiar_nombre( context['evento']['NOMBRE']) 
    return render(request, 'eventos_details.html', context=context)

def eventos_list(request):
    http = urllib3.PoolManager()
    r = http.request(
        'GET',
    'http://127.0.0.1:8000/eventos/'
    )
    context={'eventos':eliminar_eventos_repetidos(json.loads(r.data))}
    return render(request, 'eventos_list.html', context=context)

def base_view(request):
    return render(request, 'graffiti_list.html')

def list_publicaciones_views(request):
    publicaciones = Publicacion.objects.all()
    context = {
        "publicaciones": publicaciones
    }
    return render(request, 'publicaciones_list.html', context=context)

def publicaciones_detail_view(request, pk):
    pk = ObjectId(pk)
    publicacion = Publicacion.objects.get(pk=pk)
    context = {
        "publicacion": publicacion,
        "meGusta": len(publicacion.meGusta)
    }
    return render(request, 'publicacion_detail.html', context=context)

def publicaciones_formulario_view(request):
    return render(request, 'publicacion_formulario_crear.html')

def usuarios_list(request):
    usuarios = Usuario.objects.all()
    context = {
        "usuarios": usuarios
    }
    return render(request, 'usuarios_list.html', context=context)

def usuarios_detail(request, pk):
    pk = ObjectId(pk)
    usuario = Usuario.objects.get(pk=pk)
    seguidores = Usuario.objects.filter(listaSeguimiento__contains=usuario)
    context = {
        "usuario": usuario,
        "seguidos": len(usuario.listaSeguimiento),
        "seguidores": len(seguidores)
    }
    return render(request, 'usuarios_detail.html', context=context)