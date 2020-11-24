from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
from math import radians, cos, sin, asin, sqrt
import urllib3, json, unidecode
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from threading import Thread

urlCalidadDelAire = 'https://datosabiertos.malaga.eu/recursos/ambiente/calidadaire/calidadaire.json'
url_eventos = 'https://datosabiertos.malaga.eu/api/3/action/datastore_search'
url_bicis =  'https://datosabiertos.malaga.eu/recursos/transporte/trafico/da_carrilesBici-25830.geojson'
def comprobar_distancia(latitud1, latitud2, longitud1, longitud2, rango):
    return latitud1-latitud2<abs(rango) and longitud1-longitud2<abs(rango) 

def cargar_url(url):
    http = urllib3.PoolManager()
    r = http.request('GET',
    url,
    fields={'resource_id':'7f96bcbb-020b-449d-9277-1d86bd11b827'}
    )

   
    return r.data
     
class CalidadDelAireTodo(APIView):
    @swagger_auto_schema(operation_description="Devuelve todos los datos respecto a la calidad del aire que ofrece el ayuntamiento de Málaga. Esta consulta es muy ineficiente debido a la inmensa cantidad de datos ofrecidos, por lo que desaconsejamos su uso. En su lugar hay disponible la consulta por paginación.",
                         responses={200: 'Todo correcto', 404: 'Recurso no encontrado'}) 
    def get(self, request, pk=None):
        try:
            http = urllib3.PoolManager()
            r = http.request('GET', urlCalidadDelAire)
            datos = json.loads(r.data)
            return Response(datos, status=status.HTTP_200_OK)
        except:
            return Response(status= status.HTTP_404_NOT_FOUND)

#skip va incluido y limit no
class CalidadDelAirePaginacion(APIView):

    @swagger_auto_schema(operation_description="Devuelve los datos de calidad del aire de forma paginada, en una página de tamaño LIMIT y saltando SKIP datos.",
                         responses={200: 'Todo correcto', 404: 'Recurso no encontrado'}, operation_id="calidadDelAire_paginacion")
    def get(self, request, limit, skip=0):
        limit = int(self.kwargs.get("limit"))
        try:
            skip = int(self.kwargs.get("skip"))
        except:
            skip = 0
            # @swagger_auto_schema(operation_description="Devuelve los LIMIT primeros datos de calidad del aire.",
            #              responses={200: 'Todo correcto', 404: 'Recurso no encontrado'}) 
        try:
            http = urllib3.PoolManager()
            r = http.request('GET', urlCalidadDelAire)
            datos = json.loads(r.data)
        except:
            return Response(status= status.HTTP_404_NOT_FOUND)
        numDatos = len(datos['features'])
        res = []
        if skip+limit > numDatos:
            limit = numDatos-skip
        if skip < numDatos:
            for i in range(skip, skip+limit):
                res.append(datos['features'][i])
        return Response(res, status=status.HTTP_200_OK)


#Esta función asume que cada coordenada esta contenida en una única zona
#IMPORTANTE que si se pega una coordenada de google maps quitar espacio
class CalidadDelAireCoordenadas(APIView):
    @swagger_auto_schema(operation_description="Devuelve los datos de calidad del aire de la zona en la que está contenida la coordenada dada (latitud,longitud). Si esa coordenada no se encuentra devuelve un objeto vacio.",
                         responses={200: 'Todo correcto', 404: 'Recurso no encontrado'}, operation_id="calidadDelAire_coordenadas") 
    def get(self, request, x, y):
        coordX = float(self.kwargs.get("x"))
        coordY = float(self.kwargs.get("y"))  
        try:
            http = urllib3.PoolManager()
            r = http.request('GET', urlCalidadDelAire)
            datos = json.loads(r.data)
        except:
            return Response(status= status.HTTP_404_NOT_FOUND)
        numDatos = len(datos['features'])
        zona = {}
        encontrado = False
        i = 0
        while i < numDatos and not encontrado:
            zona = datos['features'][i]
            coordenadas = zona['geometry']['coordinates']
            vertx = []
            verty = []
            for x in coordenadas[0]:
                vertx.append(float(x[1])) #No se porque han guardado las coordenadas (y, x)
            for y in coordenadas[0]:
                verty.append(float(y[0]))
            res = pnpoly(len(vertx), vertx, verty, coordX, coordY)
            if res:
                encontrado = True
            else:
                i += 1
        if not encontrado:
            zona = {}
        return Response(zona, status=status.HTTP_200_OK)

#Algoritmo: https://stackoverflow.com/questions/11716268/point-in-polygon-algorithm
#nvert = numero de vertices, vertx y verty = arrays que contienen x e y coordenadas del poligono, testx y testy = nuestras coordenadas
def pnpoly(nvert, vertx, verty, testx, testy):
    c = False
    i = 0
    j = nvert-1
    while i < nvert:
        if (((verty[i]>testy) != (verty[j]>testy)) and
        (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i])):
            c = not c
        j = i
        i += 1
    return c


class CalidadDelAireDistancia(APIView):
    @swagger_auto_schema(operation_description="Devuelve los datos de calidad del aire de las zonas cuyo centro estén a igual o menor distancia en kilometros (KM) de las coordenadas dadas (latitud,longitud). Si no se encuentran zonas devuelve un objeto vacio.",
                         responses={200: 'Todo correcto', 404: 'Recurso no encontrado'}, operation_id="calidadDelAire_distancia") 
    def get(self, request, x, y, km):
        coordX = float(self.kwargs.get("x"))
        coordY = float(self.kwargs.get("y"))
        distancia = float(self.kwargs.get("km"))
        http = urllib3.PoolManager()
        r = http.request('GET', urlCalidadDelAire)
        datos = json.loads(r.data)
        zonas = []
        for zona in datos['features']:
            coordenadas = zona['geometry']['coordinates']
            vertx = []
            verty = []
            for x in coordenadas[0]:
                vertx.append(float(x[1])) #No se porque han guardado las coordenadas (y, x)
            for y in coordenadas[0]:
                verty.append(float(y[0])) 
            if comprobar_distancia_poligono(vertx, verty, coordX, coordY, distancia):
                zonas.append(zona)
        return Response(zonas, status=status.HTTP_200_OK)

#Si el centro del poligono esta a x o menos metros de nuestra coordenada es true 
def comprobar_distancia_poligono(vertx,verty,coordX,coordY,distancia):
    encontrado = False
    i = 0
    num = len(vertx)
    sX = sum(vertx)/num
    sY = sum(verty)/num
    if calcularDistancia(sX, sY, coordX, coordY) <= distancia: 
        encontrado = True
    return encontrado

#Código extraido de: https://stackoverrun.com/es/q/4271930
def calcularDistancia(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km

class EventosID(APIView):
    def get_object(self, request, pk):
        lista = json.loads(cargar_url(url_eventos))['result']['records']

        for elem in lista:
            if(elem['ID_ACTIVIDAD'] == pk):
                return Response(elem, status=200)
        return Response(status=404)
    @swagger_auto_schema(operation_description="Devuelve el evento de id PK. Si no hay devuelve error.",
                         responses={200: 'Todo correcto', 404:'Elemento no existente'}, operation_id="eventos_id") 
    def get(self, request, pk):
        return self.get_object(request, pk)

# URL: 'https://datosabiertos.malaga.eu/api/3/action/datastore_search'
class Eventos(APIView):
    @swagger_auto_schema(operation_description="Devuelve los eventos que contengan la subcadena CONTENIDO en la propiedad CAMPO. En el caso de que no se pase ningún campo buscará la cadena en todos los campos del objeto. Si no se le pasa ningún parámetro devolverá todos los eventos. ",
                         responses={200: 'Todo correcto', 404: 'Campo o contenido no existente'}, operation_id="eventos_propiedades") 
    def get(self, request, contenido='',campo=''):

        lista = json.loads(cargar_url(url_eventos))['result']['records']
        resultado = []
        c= str(contenido)
  
        
        if(campo=='' and contenido==''):
            return Response(lista, status=status.HTTP_200_OK)
        if(campo != ''):
            for elem in lista:
                if (campo in elem.keys()):
                    if (unidecode.unidecode(c.casefold()) in unidecode.unidecode(str(elem[campo]).casefold())):
                        resultado.append(elem)
                else:
                    return Response(status=404)
        else:
            for elem in lista:
                for v in elem.items():
                    if(unidecode.unidecode(c.casefold()) in unidecode.unidecode(str(v).casefold())):
                        resultado.append(elem)
                        break
        if(not resultado):
            return Response(status= status.HTTP_404_NOT_FOUND)
        else:
            return Response(resultado,status=status.HTTP_200_OK)

class EventosPaginacion(APIView):
    @swagger_auto_schema(operation_description="Devuelve los eventos de forma paginada, en una página de tamaño LIMIT y saltando SKIP datos.",
                         responses={200: 'Todo correcto'}, operation_id="eventos_paginacion") 
    def get(self, request, limit, skip=0):
        limit = int(self.kwargs.get("limit"))
        try:
            skip = int(self.kwargs.get("skip"))
        except:
            skip = 0

        datos = json.loads(cargar_url(url_eventos))
        numDatos = len(datos['result']['records'])
        res = []
        if skip+limit > numDatos:
            limit = numDatos-skip
        if skip < numDatos:
            for i in range(skip, skip+limit):
                res.append(datos['result']['records'][i])
        return Response(res, status=status.HTTP_200_OK)


class Bicis(APIView):
    
    
    def get_object(self, request, pk):
        lista = json.loads(cargar_url(url_bicis))['features']
        for elem in lista:
            if (pk == elem['id']):
                return Response(elem, status=200)
        return Response(status=404)
    
    @swagger_auto_schema(operation_description="Consulta sobre los objetos que esten a una distancia menor de RANGO desde un punto de latitud LATITUD y longitud LONGITUD",
                         responses={200: 'Todo correcto', 404:'Not found'}, operation_id="bicis_propiedades")
    def get(self, request, latitud=None, longitud=None, rango=None, pk=None):
        if pk:
             return self.get_object(request, pk)
        else:
         
            lista = json.loads(cargar_url(url_bicis))['features']
            latitud = float(latitud)
            longitud = float(longitud)
            rango = float(rango)

            resultado = []
            for elem in lista:
                if(elem['geometry']['type']=="Point"):
                    if(comprobar_distancia(elem['geometry']['coordinates'][0], latitud, elem['geometry']['coordinates'][1], longitud, rango)):
                        resultado.append(elem)
                else:
                    for punto in elem['geometry']['coordinates']:
                        if(comprobar_distancia(punto[0], latitud, punto[1], longitud, rango)):
                            resultado.append(elem)
                            break
            return Response(resultado,status=status.HTTP_200_OK)