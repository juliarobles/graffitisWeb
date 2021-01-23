from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from bson import ObjectId
from django.template.loader import get_template
from django.template import Context
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
from django.utils.http import urlencode
import urllib3, json, flickrapi
import requests, webbrowser
from datetime import date
from urllib.parse import urlencode
import time
from xml.etree import ElementTree


http = urllib3.PoolManager()
client_id = '6f71c692857b528'
client_secret = 'fdd4159d0389284b15e33c8c80018700b0a8f5c0'
FLICKR_API_KEY = '75b8452aae39dc0967a42c37c139e8a0'
FLICKR_API_SECRET = '15075131b9983f9b'
FLICKR_USER = '191270823@N05'


#####################FUNCIONES ÚTILES######################

def cargar_paleta_API(request):
    r = http.request(
            'GET',
            'http://palett.es/API/v1/palette',
        )
    paleta = {'paleta': json.loads(r.data)}
    print(paleta)
    return render(request, 'paleta_api.html', paleta)

def uploadImage(image):
    flickr = flickrapi.FlickrAPI(FLICKR_API_KEY, FLICKR_API_SECRET)

    filename = image.name
    rsp = flickr.upload(filename=filename, fileobj=image)
    time.sleep(3)

    if rsp.get('stat') != 'ok':
        return None

    image_id = rsp.find('photoid').text

    for photo in flickr.walk_user():
        if photo.get('id') == image_id:
            url = 'https://live.staticflickr.com/'+photo.get('server')+'/'+photo.get('id')+'_'+photo.get('secret')+'.jpg'
            return url

    return None

def comprobarUsuarioLogueado(request):
    #Lo he cambiado por esto: https://stackoverflow.com/questions/4963186/django-sessions-can-you-check-for-session-data-and-set-it-in-same-view 
    if 'usuario' not in request.session:
        print(str('usuario' not in request.session) + " tiene que ser true")
        return redirect('/principal/')

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
        'http://127.0.0.1:8000/publicaciones/'
        )
        publicaciones = json.loads(r.data)
    context={'publicaciones': publicaciones, "busqueda": busNav}
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

def privacidad(request):
    return render(request, 'politicaPrivacidad.html')

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
    ret = comprobarUsuarioLogueado(request)
    if ret:
        return ret
    #  ** Flickr
    token= '72157717157590777-acde95669be3f3f1&oauth_verifier=b7825e3b792089ef'  #**No sé que es esto. oauth_token
    api_key = '75b8452aae39dc0967a42c37c139e8a0'
    api_secret = '15075131b9983f9b'
    user_id= '191270823@N05'


    otro_token ='898-452-861' #** Este código creo que si funciona, será el token

    if request.method == 'POST':
        fecha = date.fromisoformat(request.POST['fecha_captura'])

        # Comprobamos la longitud de los campos


        flickr = flickrapi.FlickrAPI(api_key, api_secret)

        # Comprobar validez del token de cache
    
        actualizar_token(flickr)
        ################################################################################



        imagen = request.FILES['imagen']
        resp = flickr.upload(filename=str(imagen), fileobj=imagen.file, format='etree')

        # Sacamos la id de la respuesta del servidor REST
        for elem in resp:
            if(str(elem.tag)=='photoid'):
                photo_id = elem.text

        # Obtenemos la URL consultando el servidor REST 
        for photo in flickr.walk_user(user_id):
            # Estructura de la url por si alguien quiere utilizar algo 
            # https://live.staticflickr.com/{server-id}/{id}_{secret}_{size-suffix}.jpg
            if(photo.get('id') == photo_id):
                url = 'https://live.staticflickr.com/'+photo.get('server')+'/'+photo.get('id')+'_'+photo.get('secret')+'.jpg'
                break        
        tematicas = str(request.POST['tematica']).split('#')
        if tematicas[0] == "":
            del tematicas[0]
        for t in tematicas:
            t = t.strip()
        # return render(request, 'imagen.html', context={'imagen':url})
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

        requests.post('http://localhost:8000/publicaciones/', data=json.dumps(dic), headers= {'Content-type': 'application/json', 'Accept': 'application/json'})
        # r = http.request(
        #     'POST',
        #     'http://localhost:8000/publicaciones', 
        #     fields=json.dumps(dic), 
        #     headers=  {'Content-type': 'application/json', 'Accept': 'application/json'}
        # )
        
    
    return redirect(reverse('inicio'))

def actualizar_token(flickr):
        flickr.authenticate_via_browser(perms='write')

        # DESCOMENTAR AQUI. Solo tendréis que DESCOMENTAR las líneas de abajo para autorizar la app
        # y obtener un token nuevo
        # Más info: https://stuvel.eu/flickrapi-doc/3-auth.html
        ##############################################################################
        # if not flickr.token_valid(perms='write'):

        #     # Get a request token
        #     flickr.get_request_token(oauth_callback='oob')

        #     # Open a browser at the authentication URL. Do this however
        #     # you want, as long as the user visits that URL.
        #     authorize_url = flickr.auth_url(perms='write')
        #     webbrowser.open_new_tab(authorize_url)

        #     # Get the verifier code from the user. Do this however you
        #     # want, as long as the user gives the application the code.
        #     verifier = str(input('Verifier code: '))

        #     # Trade the request token for an access token
        #     flickr.get_access_token(verifier)
def eliminar_publicacion(request, pk):
    r = http.request(
        'GET',
    'http://127.0.0.1:8000/publicaciones/'+str(pk)
    )
    publicacion=json.loads(r.data)
    
    b = http.request(
        'GET',
    'http://127.0.0.1:8000/usuarios/'+str(publicacion['creador'])
    )

    creador = json.loads(b.data)
    if creador['id'] == request.session.get('usuario') or request.session.get('admin'):
        r = requests.delete(f'http://127.0.0.1:8000/publicaciones/{pk}/')
    return redirect(reverse('inicio'))

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
            url = 'http://127.0.0.1:8000/publicaciones/'+str(pk)+'/comentarios/'
            headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

            requests.post(url, data=data, headers=headers)
    return redirect(reverse('publicacion-detail', args=(pk,)))

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

def private_post_like(request,pk):
    if request.session.has_key('usuario'):
        cadena = {
            "usuario": str(request.session['usuario'])
        }
        data = json.dumps(cadena)
        url = 'http://127.0.0.1:8000/publicaciones/'+str(pk)+'/like'
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

        requests.post(url, data=data, headers=headers)


def editar_graffiti(request, id_pub, id_graf):
    if request.session.has_key('usuario'):
        r = requests.get('http://localhost:8000/publicaciones/' + id_pub +'/graffitis/' + id_graf)
        graffiti = json.loads(r.text)
        r = requests.get('http://localhost:8000/usuarios/' + graffiti['autor']['id'])
        autor = json.loads(r.text)
    return render(request, 'editar_graffiti.html', context={'graffiti' : graffiti, 'autor':autor, 'publicacion_id': id_pub, })

def eliminar_graffiti(request, ppk, gpk):
    if request.session.has_key('usuario'):
        r = requests.get('http://localhost:8000/publicaciones/' + ppk +'/graffitis/' + gpk)
        graffiti = json.loads(r.text)
        r = requests.get('http://localhost:8000/usuarios/' + graffiti['autor']['id'])
        autor = json.loads(r.text)
    
        if request.session.get('usuario') == autor['id'] or request.session.get('admin'):
            requests.delete('http://localhost:8000/publicaciones/' + ppk +'/graffitis/' + gpk)
    
    return redirect(reverse('publicacion-detail', args={ppk}))

def delete_comentario(request, pk, cpk):
    
    if request.session.has_key('usuario'):
        id_user = request.session['usuario']
        r = http.request(
            'GET',
            'http://127.0.0.1:8000/publicaciones/'+pk+'/comentarios/'+cpk
        )
        comentario = json.loads(r.data)
        
        headers = {'Accept': 'application/json'}
        
        if id_user == comentario.get('autor').get('id'):
            a=requests.delete('http://127.0.0.1:8000/publicaciones/'+pk+'/comentarios/'+cpk, headers=headers)
            

            
    return redirect(reverse('publicacion-detail', args=(pk,)))

def usuario_follow(request, pk):
    if request.session.has_key('usuario'):
        id_user = request.session.get('usuario')
        headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
        data={'usuario':request.session.get('usuario')}
        body = json.dumps(data)
        r = requests.post(f'http://localhost:8000/usuarios/{pk}/follow', data=body, headers=headers)
    return redirect(reverse('usuarios-detail', args={pk}))

def usuario_edit(request, pk):
    if request.session.has_key('usuario'):
        if request.method == 'POST':
            url = 'http://localhost:8000/usuarios/' + pk + "/"
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
            # Subir imagen a flickr
            url = uploadImage(imagen)
            print(imagen.name)
            form = request.POST
            data = {
                'estado': form['estado'],
                'fechaCaptura': form['fecha_captura'],
                'autor': request.session.get('usuario'),
                'imagen': url
            }
            body = json.dumps(data)
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
            r = requests.post(f'http://localhost:8000/publicaciones/{pk}/graffitis/', data=body, headers=headers)
            return redirect(reverse('publicacion-detail', args=[pk]))

def guardar_editar_graffiti(request, id_pub, id_graf):
    ret = comprobarUsuarioLogueado(request)
    if ret:
        return ret
    graffiti = requests.get('http://localhost:8000/publicaciones/'+id_pub+'/graffitis/' +id_graf)
    graf = json.loads(graffiti.text)

    if request.method == 'POST':
        dic={
            'imagen': graf['imagen'],
            'estado': request.POST['estado'],
            'fechaCaptura': request.POST['fecha_captura'],
            'autor': graf['autor']['id']
        }
        resp = requests.put('http://localhost:8000/publicaciones/' + id_pub + '/graffitis/' + id_graf, data=json.dumps(dic), headers= {'Content-type': 'application/json', 'Accept': 'application/json'})
    return redirect(reverse('publicacion-detail', args=[id_pub]))

def editar_publicacion(request, pk, gpk):
    if request.method == 'POST' :

        api_key = '75b8452aae39dc0967a42c37c139e8a0'
        api_secret = '15075131b9983f9b'
        user_id= '191270823@N05'

        flickr = flickrapi.FlickrAPI(api_key, api_secret)
        imagencheck = request.FILES.get('imagen') or None
        if imagencheck is not None  :
            imagen = request.FILES['imagen']
            resp = flickr.upload(filename=str(imagen), fileobj=imagen.file, format='etree')

            # Sacamos la id de la respuesta del servidor REST
            for elem in resp:
                if(str(elem.tag)=='photoid'):
                    photo_id = elem.text

            # Obtenemos la URL consultando el servidor REST 
            for photo in flickr.walk_user(user_id):
                # Estructura de la url por si alguien quiere utilizar algo 
                # https://live.staticflickr.com/{server-id}/{id}_{secret}_{size-suffix}.jpg
                if(photo.get('id') == photo_id):
                    url = 'https://live.staticflickr.com/'+photo.get('server')+'/'+photo.get('id')+'_'+photo.get('secret')+'.jpg'
                    break
        else :
            r = http.request(
                'GET',
                'http://127.0.0.1:8000/publicaciones/'+pk+'/graffitis/'+gpk
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
        g = requests.put(f'http://127.0.0.1:8000/publicaciones/{pk}/graffitis/{gpk}', data=json.dumps(doc), headers=headers)
        r = requests.put(f'http://127.0.0.1:8000/publicaciones/{pk}/', data=data, headers=headers)
        
    else: 
        r = http.request(
            'GET',
            'http://127.0.0.1:8000/publicaciones/'+str(pk)
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