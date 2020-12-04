from django.shortcuts import render, redirect
from graffitiApp.models import Publicacion, Usuario, Graffiti #No deberiamos usar esto
from django.http import HttpResponse
from django.urls import reverse
from bson import ObjectId
from django.template.loader import get_template
from django.template import Context
from django.http import HttpRequest, JsonResponse
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
import urllib3, json
import requests

http = urllib3.PoolManager()

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

def cargar_eventos_ajax(request):
    print('Cargando eventos')
    if request.is_ajax and request.method == "GET":
        http = urllib3.PoolManager()
        r = http.request(
        'GET',
        'http://127.0.0.1:8000/eventos/'
        )
        data = {'eventos':eliminar_eventos_repetidos(json.loads(r.data))}
        return render(request, 'eventos_panel.html', data)

def cargar_evento_id_ajax(request, ID_ACTIVIDAD):
    if request.is_ajax and request.method == "GET":
        r = http.request(
            'GET',
            'http://127.0.0.1:8000/eventosID/'+str(ID_ACTIVIDAD),
        )
        data={'evento_seleccionado':json.loads(r.data)}
        # data['evento_seleccionado']['DESCRIPCION']= limpiar_nombre(data['evento_seleccionado']['DESCRIPCION'])
        data['evento_seleccionado']['NOMBRE']= limpiar_nombre(data['evento_seleccionado']['NOMBRE'])
        return render(request, 'info-card.html', data )
# Prueba mover a app cliente

def principal(request):
    if request.session.has_key('usuario'):
        return redirect('/inicio/')
        
    else:
        return render(request, 'log.html')

def inicio(request):
    publicaciones = []
    if "busqueda" in request.GET:
        busqueda = request.GET.get("busqueda")
        if "#" in busqueda: #Busco por temática
            listaHT = busqueda.split("#")
            for ht in listaHT:
                if ht != '':
                    url = 'http://127.0.0.1:8000/publicaciones/tematica/' + str(ht).strip()
                    try:
                        r = requests.get(url)
                        data = r.json()
                        for dato in data:
                            publicaciones.append(dato)
                    except ValueError:
                        print("Response content is not valid JSON")
        elif "@" in busqueda: #Busco por usuario
            listaUsers = busqueda.split('@')
            for user in listaUsers:
                if user != '':
                    try:
                        r = http.request('GET', 'http://127.0.0.1:8000/usuarios/username/' + str(user).strip())
                        usuario = json.loads(r.data)
                        id = usuario[0]['id']
                        r = http.request('GET', 'http://127.0.0.1:8000/publicaciones/creador/' + str(id))
                        data = json.loads(r.data)
                        for dato in data:
                            publicaciones.append(dato)
                    except:
                        pass

        else: #Busco por nombre y descripcion
            listaWords = busqueda.split(' ')
            for word in listaWords:
                if word != '':
                    try:
                        word = str(word).strip()
                        r = http.request('GET', 'http://127.0.0.1:8000/publicaciones/titulo/' + word)
                        data1 = json.loads(r.data)
                        r = http.request('GET', 'http://127.0.0.1:8000/publicaciones/descripcion/' + word)
                        data2 = json.loads(r.data)
                         
                        #data3 = data1 + list(set(data2) - set(data1)) #Elimino repetidos

                        for dato in data1:
                            publicaciones.append(dato)
                        for dato in data2:
                            if dato not in data1:
                                publicaciones.append(dato)

                    except:
                        pass
    else:
        r = http.request(
            'GET',
        'http://127.0.0.1:8000/publicaciones/'
        )
        publicaciones = json.loads(r.data)
    context={'publicaciones': publicaciones}
    return render(request, 'inicio.html', context=context)

def registro(request):
    print("Prueba")
    return render(request, 'registro.html')

def eventos_details(request, ID_ACTIVIDAD):
    r = http.request(
        'GET',
         'http://127.0.0.1:8000/eventosID/' + str(ID_ACTIVIDAD),
    )
    context={'evento':json.loads(r.data)}
    if 'NOMBRE' in context['evento']:
        context['evento']['NOMBRE'] = limpiar_nombre( context['evento']['NOMBRE']) 
    return render(request, 'eventos_details.html', context=context)

def eventos_list(request):
    r = http.request(
        'GET',
    'http://127.0.0.1:8000/eventos/'
    )
    context={'eventos':eliminar_eventos_repetidos(json.loads(r.data))}
    return render(request, 'eventos_list.html', context=context)

def base_view(request):
    return render(request, 'graffiti_list.html')

def list_publicaciones_views(request):
    r = http.request(
        'GET',
    'http://127.0.0.1:8000/publicaciones/'
    )
    context={'publicaciones':json.loads(r.data)}
    return render(request, 'publicaciones_list.html', context=context)

def publicaciones_detail_view(request, pk):
    r = http.request(
        'GET',
    'http://127.0.0.1:8000/publicaciones/'+str(pk)
    )
    publicacion=json.loads(r.data)
    b = http.request(
        'GET',
    'http://127.0.0.1:8000/usuarios/'+str(publicacion['creador'])
    )
    context = {
        "publicacion": publicacion,
        "creador":json.loads(b.data),
        "meGusta": len(publicacion['meGusta']),
        "lenComentarios": len(publicacion['listaComentarios'])
    }
    return render(request, 'publicacion_detail.html', context=context)

def publicaciones_formulario_view(request):
    return render(request, 'publicacion_crear.html')

def usuarios_list(request):
    r = http.request(
        'GET',
    'http://127.0.0.1:8000/usuarios/'
    )
    context = {
        "usuarios": json.loads(r.data)
    }
    return render(request, 'usuarios_list.html', context=context)

def usuarios_detail(request, pk):
    r = http.request(
        'GET',
    'http://127.0.0.1:8000/usuarios/'+str(pk)
    )
    usuario=json.loads(r.data)
    listaPublicaciones = []
    for id in usuario['listaPublicaciones']:
        r = http.request('GET','http://127.0.0.1:8000/publicaciones/'+str(id))
        listaPublicaciones.append(json.loads(r.data))
    listaActualizaciones = []
    for id in usuario['listaGraffitisPublicaciones']:
        r = http.request('GET','http://127.0.0.1:8000/publicaciones/'+str(id))
        listaActualizaciones.append(json.loads(r.data))


    context = {
        "usuario": usuario,
        "listaPublicaciones": listaPublicaciones,
        "listaActualizaciones": listaActualizaciones
    }
    return render(request, 'usuarios_detail.html', context=context)

def crear_publicacion(request):
    print(request.POST)
    
    return redirect(reverse('inicio'))