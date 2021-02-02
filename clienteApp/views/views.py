from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from bson import ObjectId
from django.template.loader import get_template
from django.template import Context
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
from django.utils.http import urlencode
import urllib3, json
import requests, webbrowser
from datetime import date
from urllib.parse import urlencode
import time
from xml.etree import ElementTree

# ---------------------------------------------------------------------------- #
#                                    INDICE                                    #
# ---------------------------------------------------------------------------- #

# -VARIABLES
# -APIS
#     -PALETAS
#     -IMGUR
# -AYUNTAMIENTO
#     -EVENTOS
# -USUARIOS
# -PUBLICACIONES
#     -COMENTARIOS
#     -GRAFFITIS
# -FUNCIONES APP






# ---------------------------------------------------------------------------- #
#                                   VARIABLES                                  #
# ---------------------------------------------------------------------------- #

http = urllib3.PoolManager()
client_id = '6f71c692857b528'
client_secret = 'fdd4159d0389284b15e33c8c80018700b0a8f5c0'
# Por ahora usaremos esto para modificar rápido las urls del server REST
# pero estaría bien hacer una variable global de la app o algo
url_base = 'https://graffitisweb-c4.herokuapp.com'

# ---------------------------------------------------------------------------- #
#                                     APIS                                     #
# ---------------------------------------------------------------------------- #



# ---------------------------------- PALETAS --------------------------------- #

def cargar_paleta_API(request):
    r = http.request(
            'GET',
            'http://palett.es/API/v1/palette',
        )
    paleta = {'paleta': json.loads(r.data)}
    print(paleta)
    return render(request, 'paleta_api.html', paleta)

# ---------------------------------- IMGUR ---------------------------------- #

def subirImagen_imgur(archivo):
    dic = {
        'image': b64encode(archivo.file.read()),
        'type': 'base64'
    }
    j1 = requests.post(
        "https://api.imgur.com/3/image",
        data = dic,
        headers = {
            'Accept': 'application/json', 
            'Authorization': 'Client-ID a3a0174547253ee'
        }
    )
    return json.loads(j1.content)['data']['link']

# ---------------------------------------------------------------------------- #
#                                 AYUNTAMIENTO                                 #
# ---------------------------------------------------------------------------- #


# ---------------------------------- EVENTOS --------------------------------- #

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
        url_base + '/eventos/'
        )
        data = {'eventos':eliminar_eventos_repetidos(json.loads(r.data))}
        return render(request, 'eventos_panel.html', data)

def cargar_evento_id_ajax(request, ID_ACTIVIDAD):
    if request.is_ajax and request.method == "GET":
        r = http.request(
            'GET',
            url_base + '/eventosID/'+str(ID_ACTIVIDAD),
        )
        data={'evento_seleccionado':json.loads(r.data)}
        # data['evento_seleccionado']['DESCRIPCION']= limpiar_nombre(data['evento_seleccionado']['DESCRIPCION'])
        data['evento_seleccionado']['NOMBRE']= limpiar_nombre(data['evento_seleccionado']['NOMBRE'])
        return render(request, 'info-card.html', data )

def eventos_details(request, ID_ACTIVIDAD):
    r = http.request(
        'GET',
         url_base + '/eventosID/' + str(ID_ACTIVIDAD),
    )
    context={'evento':json.loads(r.data)}
    if 'NOMBRE' in context['evento']:
        context['evento']['NOMBRE'] = limpiar_nombre( context['evento']['NOMBRE']) 
    return render(request, 'eventos_details.html', context=context)

def eventos_list(request):
    r = http.request(
        'GET',
        url_base + '/eventos/'
    )
    context={'eventos':eliminar_eventos_repetidos(json.loads(r.data))}
    return render(request, 'eventos_list.html', context=context)

# ---------------------------------------------------------------------------- #
#                                   USUARIOS                                   #
# ---------------------------------------------------------------------------- #


def usuarios_list(request):
    r = http.request(
        'GET',
     url_base + '/api/usuarios/'
    )
    context = {
        "usuarios": json.loads(r.data)
    }
    return render(request, 'usuarios_list.html', context=context)

def usuarios_detail(request, pk):
    r = http.request(
        'GET',
    url_base + '/api/usuarios/'+str(pk)
    )
    usuario=json.loads(r.data)
    listaPublicaciones = []
    for id in usuario['listaPublicaciones']:
        r = http.request('GET', url_base + '/api/publicaciones/'+str(id))
        listaPublicaciones.append(json.loads(r.data))
    listaActualizaciones = []
    for id in usuario['listaGraffitisPublicaciones']:
        r = http.request('GET',  url_base + '/api/publicaciones/'+str(id))
        listaActualizaciones.append(json.loads(r.data))


    context = {
        "usuario": usuario,
        "listaPublicaciones": listaPublicaciones,
        "listaActualizaciones": listaActualizaciones
    }
    return render(request, 'usuarios_detail.html', context=context)

def usuario_follow(request, pk):
    if request.session.has_key('usuario'):
        id_user = request.session.get('usuario')
        headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
        data={'usuario':request.session.get('usuario')}
        body = json.dumps(data)
        url = url_base + '/api/usuarios/'+pk+'/follow'
        r = requests.post(url, data=body, headers=headers)
    return redirect(reverse('usuarios-detail', args={pk}))

def usuario_edit(request, pk):
    if request.session.has_key('usuario'):
        if request.method == 'POST':
            url = url_base + '/api/usuarios/' + pk + "/"
            data = {
                "descripcion": request.POST.get("descripcion") 
            }
            body = json.dumps(data)
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
            r = requests.put(url, data=body, headers=headers)
            b = r.reason
            c = r.status_code
            d = r.json
            
    return redirect(reverse('usuarios-detail', args=[pk]))


# ---------------------------------------------------------------------------- #
#                                 PUBLICACIONES                                #
# ---------------------------------------------------------------------------- #

def private_post_like(request,pk):
    if request.session.has_key('usuario'):
        cadena = {
            "usuario": str(request.session['usuario'])
        }
        data = json.dumps(cadena)
        url = url_base + '/api/publicaciones/'+str(pk)+'/like'
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

        requests.post(url, data=data, headers=headers)

def editar_publicacion(request, pk, gpk):
    if request.method == 'POST' :

        imagencheck = request.FILES.get('imagen') or None
        if imagencheck is not None  :
            imagen = request.FILES['imagen']
            url = subirImagen_imgur(archivo)
        else :
            r = http.request(
                'GET',
                url_base + '/api/publicaciones/'+pk+'/graffitis/'+gpk
            )
            graffiti = json.loads(r.data)
            url = graffiti.get('imagen')        

        tematica = request.POST['tematica']
        cadena = "["
        lista = []
        for tem in tematica.split("#")[1:]:
            lista.append(tem)

        dic = {
            'titulo': request.POST['titulo'],
            'descripcion': request.POST['descripcion'],
            'tematica': lista,
            'autor': request.POST['autor']
        }
        doc = {
            'imagen' : url,
            'estado': request.POST['estado'],
            'fechaCaptura':request.POST['fecha_captura'],
            'autor': request.POST['publicador']
        }
        data = json.dumps(dic)
        headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
        g = requests.put(url_base + '/api/publicaciones/'+pk+'/graffitis/'+gpk, data=json.dumps(doc), headers=headers)
        r = requests.put(url_base + '/api/publicaciones/'+pk+'/', data=data, headers=headers)
        
    else: 
        r = http.request(
            'GET',
            url_base + '/api/publicaciones/'+str(pk)
        )
        publicacion = json.loads(r.data)
        primerGraffiti = publicacion.get('listaGraffitis')[0]
        tematica = publicacion.get("tematica")
        cadena = ""
        for tem in tematica:
            cadena += '#'+tem
        context={
                'publicacion': publicacion,
                'graffiti' : primerGraffiti,
                'tematica': cadena
        }
        
        return render(request, 'publicacion_editar.html', context=context)
    
    return redirect(reverse('publicacion-detail', args=[pk]))

def crear_publicacion(request):
    print('He entrado a crear publicacion')
    ret = comprobarUsuarioLogueado(request)
    if ret:
        return ret
    
    if request.method == 'POST':
        fecha = date.fromisoformat(request.POST['fecha_captura'])
        imagen = request.FILES['imagen']
        url = subirImagen_imgur(imagen)

        tematicas = str(request.POST['tematica']).split('#')
        if tematicas[0] == "":
            del tematicas[0]
        for t in tematicas:
            t = t.strip()
        dic = {
            "titulo": request.POST["titulo"],
            "descripcion": request.POST["descripcion"],
            "localizacion": request.POST["localizacion"],
            "tematica": tematicas,#[request.POST["tematica"]],
            "autor": request.POST["autor"],
            "creador":  request.session['usuario'],#**Añadir el creador (id usuario logeado)
            "listaGraffitis":
            [
                {
                    "imagen":url, 
                    "estado": request.POST["estado"], 
                    "fechaCaptura": request.POST["fecha_captura"], 
                    "autor": request.session['usuario']
                }
            ],
        }

        requests.post(url_base + '/api/publicaciones/', data=json.dumps(dic), headers= {'Content-type': 'application/json', 'Accept': 'application/json'})
    return redirect(reverse('inicio'))

def eliminar_publicacion(request, pk):
    r = http.request(
        'GET',
    url_base + '/api/publicaciones/'+str(pk)
    )
    publicacion=json.loads(r.data)
    
    b = http.request(
        'GET',
    url_base + '/api/usuarios/'+str(publicacion['creador'])
    )

    creador = json.loads(b.data)
    if creador['id'] == request.session.get('usuario') or request.session.get('admin'):
        r = requests.delete(url_base + '/api/publicaciones/{pk}/')
    return redirect(reverse('inicio'))


def list_publicaciones_views(request):
    r = http.request(
        'GET',
    url_base + '/api/publicaciones/'
    )
    context={'publicaciones':json.loads(r.data)}
    return render(request, 'publicaciones_list.html', context=context)

def publicaciones_detail_view(request, pk):
    r = http.request(
        'GET',
    url_base + '/api/publicaciones/'+str(pk)
    )
    publicacion=json.loads(r.data)
    b = http.request(
        'GET',
    url_base + '/api/usuarios/'+str(publicacion['creador'])
    )

    for graffiti in publicacion['listaGraffitis']:
        graffiti['id'] = str(graffiti['_id'])

    context = {
        "publicacion": publicacion,
        "creador":json.loads(b.data),
        "meGusta": len(publicacion['meGusta']),
        "lenComentarios": len(publicacion['listaComentarios']),
        "usuarioLogeado": request.session['usuario'],
        "primerGraffiti": publicacion.get("listaGraffitis")[0]
    }
    return render(request, 'publicacion_detail.html', context=context)

def publicaciones_formulario_view(request):
    ret = comprobarUsuarioLogueado(request)
    if ret:
        return ret
    return render(request, 'publicacion_crear.html')

# -------------------------------- COMENTARIO -------------------------------- #

def crear_comentario(request, pk):
    if request.method == 'POST':
        if request.session.has_key('usuario'):
            texto_comentario = request.POST.get('texto')
            id_user = request.session['usuario']
            
            cadena = {
                "texto": str(texto_comentario),
                "autor": str(id_user)
            }
            data = json.dumps(cadena)
            url = url_base + '/api/publicaciones/'+str(pk)+'/comentarios/'
            headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

            requests.post(url, data=data, headers=headers)
    return redirect(reverse('publicacion-detail', args=(pk,)))

def delete_comentario(request, pk, cpk):
    
    if request.session.has_key('usuario'):
        id_user = request.session['usuario']
        r = http.request(
            'GET',
            url_base + '/api/publicaciones/'+pk+'/comentarios/'+cpk
        )
        comentario = json.loads(r.data)
        
        headers = {'Accept': 'application/json'}
        
        if id_user == comentario.get('autor').get('id') or request.session.get('admin'):
            a=requests.delete(url_base + '/api/publicaciones/'+pk+'/comentarios/'+cpk, headers=headers)
            

            
    return redirect(reverse('publicacion-detail', args=(pk,)))

# --------------------------------- GRAFFITIS -------------------------------- #


def editar_graffiti(request, id_pub, id_graf):
    if request.session.has_key('usuario'):
        r = requests.get(url_base + '/api/publicaciones/' + id_pub +'/graffitis/' + id_graf)
        graffiti = json.loads(r.text)
        r = requests.get(url_base + '/api/usuarios/' + graffiti['autor']['id'])
        autor = json.loads(r.text)
    return render(request, 'editar_graffiti.html', context={'graffiti' : graffiti, 'autor':autor, 'publicacion_id': id_pub, })

def eliminar_graffiti(request, ppk, gpk):
    if request.session.has_key('usuario'):
        r = requests.get(url_base + '/api/publicaciones/' + ppk +'/graffitis/' + gpk)
        graffiti = json.loads(r.text)
        r = requests.get(url_base + '/api/usuarios/' + graffiti['autor']['id'])
        autor = json.loads(r.text)
    
        if request.session.get('usuario') == autor['id'] or request.session.get('admin'):
            requests.delete(url_base + '/api/publicaciones/' + ppk +'/graffitis/' + gpk)
    
    return redirect(reverse('publicacion-detail', args={ppk}))

def graffiti_form(request, pk):
    """
    Esta funcion se encargara de generar la pagina html con el formulario
    para los graffitis. Tiene doble funcionalidad:
    - GET: crea el formulario y muestra el html
    - POST: crea el graffiti y se guarda, redirige a la publicacion
    """
    comprobarUsuarioLogueado(request)
    if request.method == 'GET':
        context={
            'publicacion': pk
        }
        return render(request, 'graffiti_form.html', context=context)
    elif request.method == 'POST':
        if request.session.has_key('usuario'):
            imagen = request.FILES['imagen']
            # Subir imagen a imgur
            url = subirImagen_imgur(imagen)
            form = request.POST
            data = {
                'estado': form['estado'],
                'fechaCaptura': form['fecha_captura'],
                'autor': request.session.get('usuario'),
                'imagen': url
            }
            body = json.dumps(data)
            # print('Dictionary:' + body)
            # print('URL:' + url)
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
            url = url_base + '/api/publicaciones/'+pk+'/graffitis/'
            r = requests.post(url, data=body, headers=headers)
            return redirect(reverse('publicacion-detail', args=[pk]))

def guardar_editar_graffiti(request, id_pub, id_graf):
    ret = comprobarUsuarioLogueado(request)
    if ret:
        return ret
    graffiti = requests.get(url_base + '/api/publicaciones/'+id_pub+'/graffitis/' +id_graf)
    graf = json.loads(graffiti.text)

    if request.method == 'POST':
        dic={
            'imagen': graf['imagen'],
            'estado': request.POST['estado'],
            'fechaCaptura': request.POST['fecha_captura'],
            'autor': graf['autor']['id']
        }
        url = url_base +'/api/publicaciones/' + id_pub + '/graffitis/' + id_graf
        resp = requests.put(url, data=json.dumps(dic), headers= {'Content-type': 'application/json', 'Accept': 'application/json'})
    return redirect(reverse('publicacion-detail', args=[id_pub]))

# ---------------------------------------------------------------------------- #
#                                 FUNCIONES APP                                #
# ---------------------------------------------------------------------------- #



def comprobarUsuarioLogueado(request):
    #Lo he cambiado por esto: https://stackoverflow.com/questions/4963186/django-sessions-can-you-check-for-session-data-and-set-it-in-same-view 
    if 'usuario' not in request.session:
        print(str('usuario' not in request.session) + " tiene que ser true")
        return redirect(reverse('principal'))

def principal(request):
    if 'usuario' in request.session:
        return redirect(reverse('inicio'))
        
    else:
        return render(request, 'log.html')

def inicio(request):
    ret = comprobarUsuarioLogueado(request)
    busNav = ""
    if ret:
        return ret
    publicaciones = []
    if "busqueda" in request.GET and request.GET.get("busqueda") != "":
        busqueda = request.GET.get("busqueda")
        request.session['ultBusqueda'] = busqueda
        busNav = busqueda
        if "#" in busqueda: #Busco por temática
            listaHT = busqueda.split("#")
            for ht in listaHT:
                if ht != '':
                    url = url_base + '/api/publicaciones/tematica/' + str(ht).strip()
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
                        r = http.request('GET', url_base + '/api/usuarios/username/' + str(user).strip())
                        usuario = json.loads(r.data)
                        id = usuario[0]['id']
                        r = http.request('GET', url_base + '/api/publicaciones/creador/' + str(id))
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
                        r = http.request('GET', url_base + '/api/publicaciones/titulo/' + word)
                        data1 = json.loads(r.data)
                        r = http.request('GET', url_base + '/api/publicaciones/descripcion/' + word)
                        data2 = json.loads(r.data)

                        for dato in data1:
                            publicaciones.append(dato)
                        for dato in data2:
                            if dato not in data1:
                                publicaciones.append(dato)
                    except:
                        pass
    else:
        if 'ultBusqueda' in request.session:
            request.session['ultBusqueda'] = ""
        r = http.request(
            'GET',
         url_base + '/api/publicaciones/'
        )
        publicaciones = json.loads(r.data)
    context={'publicaciones': publicaciones, "busqueda": busNav}
    return render(request, 'inicio.html', context=context)

def registro(request):
    print("Prueba")
    return render(request, 'registro.html')

def base_view(request):
    return render(request, 'graffiti_list.html')

def privacidad(request):
    return render(request, 'politicaPrivacidad.html')


def like_inicio(request, pk):
    private_post_like(request, pk)
    if 'ultBusqueda' in request.session and request.session['ultBusqueda'] != "":
        url = reverse('inicio')
        params = urlencode({'busqueda' : request.session['ultBusqueda']})
        return HttpResponseRedirect(url + "?%s" % params)
    else:
        return redirect(reverse('inicio'))

def like_publicacion(request, pk):
    private_post_like(request, pk)
    return redirect(reverse('publicacion-detail', args=(pk,)))

