from django.shortcuts import render, redirect
import urllib3, json
import requests

http = urllib3.PoolManager()

# ACCION
# Origen: log.html
# Efecto: loguea a un usuario
def action_login(request):
    context = None
    
    if request.method == 'POST':
        # Tomamos el usuario y contraseña del post
        email_form = request.POST.get('email', '')
        password_form = request.POST.get('password', '')
        
        # Buscamos el usuario
        r = http.request(
            'GET',
            'http://127.0.0.1:8000/usuarios/',
        )
        
        usuario_data = json.loads(r.data.decode('utf-8'))
        usuario_matched = [user for user in usuario_data if user['email'] == email_form]
        
        password_correct = None
        if(usuario_matched):
            password_correct = usuario_matched[0]['password']
        
        if password_correct == password_form:
            request.session['usuario'] = email_form
            
            return redirect('/inicio/')
        else:
            context = {
                'email' : email_form,
                'message' : 'Error, usuario incorrecto.'
            }
    
    return render(request, 'log.html', context=context)