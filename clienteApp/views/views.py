from django.shortcuts import render, redirect
from graffitiApp.models import Publicacion, Usuario, Graffiti #No deberiamos usar esto
from django.http import HttpResponse
from django.urls import reverse
from bson import ObjectId
from django.template.loader import get_template
from django.template import Context
from django.http import HttpRequest, JsonResponse
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
import urllib3, json, flickrapi
import requests, webbrowser


http = urllib3.PoolManager()
client_id = '6f71c692857b528'
client_secret = 'fdd4159d0389284b15e33c8c80018700b0a8f5c0'
def comprobarUsuarioLogueado(request):
     if not request.session.has_key('usuario'):
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
    if ret:
        return ret
    
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
        "lenComentarios": len(publicacion['listaComentarios']),
        "usuarioLogeado": request.session['usuario']
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
    # ** Pruebas Imgur
    # client = ImgurClient(client_id, client_secret)
    # client.upload_from_path(POST['imagen'])
    # **Pruebas imagen
    # r = request.POST['imagen']
    # r.raw.decode_content = True
    # im = Image.open(r.raw)
    # print(im.format, im.mode, im.size)
    # print(request.FILES)
    # return render(request, 'imagen.html', context={'imagen':request.FILES['imagen']})
    #  ** Flickr
    token= '72157717157590777-acde95669be3f3f1&oauth_verifier=b7825e3b792089ef'  #**No sé que es esto. oauth_token
    api_key = '75b8452aae39dc0967a42c37c139e8a0'
    api_secret = '15075131b9983f9b'
    user_id= '191270823@N05'

    
    otro_token ='898-452-861' #** Este código creo que si funciona, será el token


    # **No sé cómo funciona el tema del token y la verificación de Flickr 
    # ** pero solo tendréis que descomentar las líneas de abajo para autorizar la app
    # ** y obtener un token nuevo
    # # ! Más info: https://stuvel.eu/flickrapi-doc/3-auth.html

    # print('Step 1: authenticate')
    # # Only do this if we don't have a valid token already
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

    # print('Step 2: use Flickr')
    # resp = flickr.photos.getInfo(photo_id='7658567128')

    if request.method == 'POST':



        # **Por ahora está comentado para no subir muchas fotos con las pruebas 
        # **Cuando esté crear publicación completo habrá que descomentarlo
        flickr = flickrapi.FlickrAPI(api_key, api_secret)
        # imagen = request.FILES['imagen']
        # resp = flickr.upload(filename=str(imagen), fileobj=imagen.file)
        # print(resp)
        img = flickr.walk_user()
        for photo in flickr.walk_user('191270823@N05'):
            # https://live.staticflickr.com/{server-id}/{id}_{secret}_{size-suffix}.jpg
            if(photo.get('size-suffix')):
                url = 'https://live.staticflickr.com/'+photo.get('server')+'/'+photo.get('id')+'_'+photo.get('secret')+'_'+photo.get('size-suffix')+'.jpg'
            else:
                url = 'https://live.staticflickr.com/'+photo.get('server')+'/'+photo.get('id')+'_'+photo.get('secret')+'.jpg'
                
            print(url)
            if photo.get('title') == 'volley clandestino azul-rosa.png' :
                img = photo
        return render(request, 'imagen.html', context={'imagen':url})


        




        dic = {
            'titulo': request.POST['titulo'],
            'descripcion': request.POST['descripcion'],
            'localizacion': request.POST['localizacion'],
            'tematica': request.POST['tematica'],
            'autor': request.POST['autor'],
            'creador': request.POST['creador'],#**Añadir el creador (id usuario logeado)
            'listaGraffitis':
            [
                {
                    'imagen': request.POST['imagen'], #**Meter url de imgur (investigar)
                    'estado': request.POST['estado'], 
                    'fechaCaptura': request.POST['fechaCaptura'], 
                    'autor': request.POST['autor']
                }
            ],
        }
        r = http.request(
            'POST',
            'http://localhost:8000/publicaciones', 
            fields=dic
        )
        print(r.status)
    
    return redirect(reverse('inicio'))

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
    if creador['email'] == request.session.get('usuario'):
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
