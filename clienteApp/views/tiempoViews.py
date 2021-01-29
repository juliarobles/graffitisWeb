import urllib3, json
import requests

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, JsonResponse

http = urllib3.PoolManager()
url = "http://api.weatherapi.com/v1/forecast.json?key=355fa1dbfd2c4b7a996215007212801&q=Malaga&days=3"

def parseCondicion(cond):
    switcher = {
        'Sunny': 'Despejado',
        'Clear': 'Despejado',
        'Cloudy': 'Nublado',
        'Partly cloudy': 'Parc. Nublado'
    }
    
    tiempo = switcher.get(cond, 'Lluvia')
    ok = 'Buen día'
    if tiempo == 'Lluvia':
        ok = 'Mal día'
    
    return (tiempo, ok)

def cargar_tiempo(request):
    r = http.request(
        'GET',
        url
    )
    
    datos=json.loads(r.data)
    
    vered_hoy = None
    fecha_hoy = datos['location']['localtime'].split(' ')[0].split('-')
    condicion_hoy = datos['current']['condition']['text']
    temp_hoy = str(round(datos['current']['temp_c']))
    viento_hoy = datos['current']['wind_kph']
    (cond_hoy, vered_hoy) = parseCondicion(condicion_hoy)
    f_hoy = fecha_hoy[2]+"-"+fecha_hoy[1]+"-"+fecha_hoy[0]
    
    n_hoy = 0
    if vered_hoy.contains('Nublado'):
        n_hoy = 1
    elif vered_hoy == 'Lluvia':
        n_hoy = 2
    
    vered_mañana = None
    fecha_mañana = datos['forecast']['forecastday'][1]['date'].split('-')
    condicion_mañana = datos['forecast']['forecastday'][1]['day']['condition']['text']
    temp_mañana_max = datos['forecast']['forecastday'][1]['day']['maxtemp_c']
    temp_mañana_min = datos['forecast']['forecastday'][1]['day']['mintemp_c']
    viento_mañana = datos['forecast']['forecastday'][1]['day']['maxwind_kph']
    temp_mañana = str(round(temp_mañana_max)) + '-' + str(round(temp_mañana_min))
    (cond_mañana, vered_mañana) = parseCondicion(condicion_mañana)
    f_mañana = fecha_mañana[2]+"-"+fecha_mañana[1]+"-"+fecha_mañana[0]
    
    n_mañana = 0
    if vered_mañana.contains('Nublado'):
        n_mañana = 1
    elif vered_mañana == 'Lluvia':
        n_mañana = 2
    
    vered_pasado = None
    fecha_pasado = datos['forecast']['forecastday'][2]['date'].split('-')
    condicion_pasado = datos['forecast']['forecastday'][2]['day']['condition']['text']
    temp_pasado_max = datos['forecast']['forecastday'][2]['day']['maxtemp_c']
    temp_pasado_min = datos['forecast']['forecastday'][2]['day']['mintemp_c']
    viento_pasado = datos['forecast']['forecastday'][2]['day']['maxwind_kph']
    temp_pasado = str(round(temp_pasado_min)) + '-' + str(round(temp_pasado_max))
    (cond_pasado, vered_pasado) = parseCondicion(condicion_pasado)
    f_pasado = fecha_pasado[2]+"-"+fecha_pasado[1]+"-"+fecha_pasado[0]
    
    n_pasado = 0
    if vered_pasado.contains('Nublado'):
        n_pasado = 1
    elif vered_pasado == 'Lluvia':
        n_pasado = 2
    
    # Datos
    data = {
        'fecha_hoy': f_hoy,
        'temp_hoy': temp_hoy,
        'viento_hoy': viento_hoy,
        'cond_hoy': cond_hoy,
        'vered_hoy': vered_hoy,
        'n_hoy': n_hoy,
        
        'fecha_tom': f_mañana,
        'temp_tom': temp_mañana,
        'viento_tom': viento_mañana,
        'cond_tom': cond_mañana,
        'vered_tom': vered_mañana,
        'n_tom': n_mañana,
        
        'fecha_pasado': f_pasado,
        'temp_pasado': temp_pasado,
        'viento_pasado': viento_pasado,
        'cond_pasado': cond_pasado,
        'vered_pasado': vered_pasado,
        'n_pasado': n_pasado
    }
    
    return render(request, 'tiempo.html', data)