import urllib3, json
import requests

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, JsonResponse

from google.oauth2 import id_token
from google.auth.transport import requests as g_requests

http = urllib3.PoolManager()

CLIENT_ID = '495343275268-1b1ccmu06nc825uvhcnb6p83kbfo2nmf.apps.googleusercontent.com'
#url_base = 'https://graffitisweb-c4.herokuapp.com/'

# Devolvemos el usuario con el email pasado como parametro o None, si no hay ninguno
def isInApp(email, request):
     # Buscamos el usuario
    url = request.get_host()
    if "8000" in url:
        url = "http://" + url
    else:
        url = "https://" + url
    r = http.request(
        'GET',
        url + '/'+'api/usuarios/',
    )
    print(r)
    usuario_data = json.loads(r.data.decode('utf-8'))
    usuario_matched = [user for user in usuario_data if user['email'] == email]
    res = None
    if len(usuario_matched) > 0:
        res = usuario_matched[0]
    return res

def registerUser(name, email, img, request):
    host = request.get_host()
    if "8000" in host:
        host = "http://" + host
    else:
        host = "https://" + host
    userJSON = {
        "usuario": email.split('@')[0],
        "nombre": name,
        "email": email,
        "password": "12345678",
        "imagen": img,
        "descripcion": "Creado mediante autentificación OAuth 2.0. Amante de la pizza con piña."
    }
    url=host + '/'+'api/usuarios/'
    response = requests.post(url, json.dumps(userJSON), headers= {'Content-type': 'application/json', 'Accept': 'application/json'})
    responseJSON = json.loads(response.content)
    
    return responseJSON["id"]
    

def action_loginInToken(request):
    if request.method == 'POST' and 'idtoken' in request.POST:
        idToken = request.POST['idtoken']
        try:
            # Verificamos la validez del token
            idinfo = id_token.verify_oauth2_token(idToken, g_requests.Request(), CLIENT_ID)
        except ValueError: 
            context = {'message' : 'Error de validacion de credenciales.'}
            return render(request, 'log.html', context=context)
        # El usuario se ha verificado correctamente
        # Tenemos que comprobar si el usuario se encuentra ya registrado; lo haremos buscando su email
        gEmail = idinfo['email']
        matched_user = isInApp(gEmail, request)
        if matched_user == None: # Nuevo usuario -> Lo registramos en la aplicación
            newUser_Id = registerUser(idinfo['name'], gEmail, idinfo['picture'], request)
            request.session['usuario'] = newUser_Id
            request.session['admin'] = False
        else:
            request.session['usuario'] = matched_user['id']
            request.session['admin'] = matched_user['admin']
        
        request.session.save()
        return JsonResponse({'dummy': 'yei'})

# ACCION
# Origen: log.html
# Efecto: autentifica a un usuario
def action_login(request):
    context = None

    url = request.get_host()
    if "8000" in url:
        url = "http://" + url
    else:
        url = "https://" + url
    # Tomamos el usuario y contraseña del post
    email_form = request.POST.get('email', '')
    password_form = request.POST.get('password', '')
    
    # Buscamos el usuario
    r = http.request(
        'GET',
        url + '/' +'api/usuarios/',
        
    )
    
    usuario_data = json.loads(r.data.decode('utf-8'))
    usuario_matched = [user for user in usuario_data if user['email'] == email_form]
    
    password_correct = None
    if(usuario_matched):
        password_correct = usuario_matched[0]['password']
    
    if password_correct == password_form:
        request.session['usuario'] = usuario_matched[0]['id']
        request.session['admin'] = usuario_matched[0]['admin']
        
        response = HttpResponseRedirect('/url/to_your_home_page')
        return redirect(reverse('inicio'))
    else:
        context = {
            'email' : email_form,
            'message' : 'Error, usuario incorrecto.'
        }

    return render(request, 'log.html', context=context)

# ACCION
# Efecto: elimina al usuario de la sesión
# Ruta final: principal
def action_logout(request):
    del request.session['usuario']
    del request.session['admin']
    
    return redirect(reverse('principal'))