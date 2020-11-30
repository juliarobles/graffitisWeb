from django.shortcuts import render
from graffitiApp.models import Publicacion, Usuario, Graffiti #No deberiamos usar esto
from django.http import HttpResponse
from bson import ObjectId
from django.template.loader import get_template
from django.template import Context
import urllib3, json


# Prueba mover a app cliente
def inicio(request):
    t = get_template('inicio.html')
    res = t.render()
    return HttpResponse(res)

def eventos_list(request):
    http = urllib3.PoolManager()
    r = http.request(
        'GET',
        'http://127.0.0.1:8000/eventos/'
    )

    plt = get_template("eventos_list.html")
    dic={'eventos':json.loads(r.data)}
    res = plt.render(dic)
    return HttpResponse(res)

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