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
url_eventos = 'https://datosabiertos.malaga.eu/api/3/action/datastore_search?resource_id=7f96bcbb-020b-449d-9277-1d86bd11b827'
url_bicis =  'https://datosabiertos.malaga.eu/recursos/transporte/trafico/da_carrilesBici-25830.geojson'
def comprobar_distancia(latitud1, latitud2, longitud1, longitud2, rango):
    return latitud1-latitud2<abs(rango) and longitud1-longitud2<abs(rango) 

def cargar_url(url):
    http = urllib3.PoolManager()
    r = http.request('GET',
    url
    )
    return r.data
     
class CalidadDelAireTodo(APIView):
    @swagger_auto_schema(operation_description="EVITAR SU USO. Devuelve todos los datos respecto a la calidad del aire que ofrece el ayuntamiento de Málaga. Esta consulta es muy ineficiente debido a la inmensa cantidad de datos ofrecidos, por lo que desaconsejamos su uso. En su lugar hay disponible la consulta por paginación.",
                         responses={200: 'Todo correcto', 404: 'Recurso no encontrado'}, 
                         deprecated=True) 
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
    @swagger_auto_schema(operation_description="Devuelve los datos de calidad del aire de forma paginada, en una página de tamaño LIMIT y saltando SKIP datos. \n Ejemplo: limit = 2 \n skip = 1 \n http://127.0.0.1:8000/calidadDelAire/limit=2&skip=1",
                         responses={200: 'Todo correcto', 404: 'Recurso no encontrado'}, operation_id="calidadDelAire_paginacion")
    def get(self, request, limit, skip=0):
        limit = int(self.kwargs.get("limit"))
        skip = int(self.kwargs.get("skip"))
        return getPaginacion(request, limit, skip)

class CalidadDelAirePaginacion2(APIView):
    @swagger_auto_schema(operation_description="Devuelve los LIMIT primeros datos de calidad del aire. \n Ejemplo: limit = 2 \n http://127.0.0.1:8000/calidadDelAire/limit=2",
                          responses={200: 'Todo correcto', 404: 'Recurso no encontrado'}, operation_id="calidadDelAire_paginacion2") 
    def get(self, request, limit, skip=0):
        limit = int(self.kwargs.get("limit"))
        skip = 0
        return getPaginacion(request, limit, skip)

def getPaginacion(request, limit, skip): 
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
    @swagger_auto_schema(operation_description="Devuelve los datos de calidad del aire de la zona en la que está contenida la coordenada dada (latitud,longitud). Si esa coordenada no se encuentra devuelve un objeto vacio. Ejemplo: http://127.0.0.1:8000/calidadDelAire/36.698981,-4.439564 \n Nota: el ayuntamiento devuelve las coordenadas de la forma (y,x)" ,
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
    @swagger_auto_schema(operation_description="Devuelve los datos de calidad del aire de las zonas cuyo centro estén a igual o menor distancia en kilometros (KM) de las coordenadas dadas (latitud,longitud). Si no se encuentran zonas devuelve un objeto vacio. Ejemplo: http://127.0.0.1:8000/calidadDelAire/36.698981,-4.439564&km=0.5 \n Nota: el ayuntamiento devuelve las coordenadas de la forma (y,x)",
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
        pk = int(pk)
        for elem in lista:
            if(elem['ID_ACTIVIDAD'] == pk):
                return Response(elem, status=200)
        return Response(status=404)

    @swagger_auto_schema(operation_description="Devuelve el evento de ID_ACTIVIDAD PK. Si no hay devuelve error. \n Ejemplo: id = 100195 \n http://127.0.0.1:8000/eventosID/100195",
                         responses={200: 'Todo correcto', 404:'Elemento no existente'}, operation_id="eventos_id") 
    def get(self, request, pk):
        return self.get_object(request, pk)

# URL: 'https://datosabiertos.malaga.eu/api/3/action/datastore_search'
class EventosTodo(APIView):
    @swagger_auto_schema(operation_description="Devuelve todos los eventos existentes en los datos del Ayuntamiento de Málaga \n Ejemplo: http://127.0.0.1:8000/eventos/",
                         responses={200: 'Todo correcto', 404: 'Campo o contenido no existente'}, operation_id="eventos_list") 
    def get(self, request, contenido='',campo=''):
        return getEvento(request, contenido, campo)

class EventosPropiedades(APIView):
    @swagger_auto_schema(operation_description="Devuelve los eventos que contengan la subcadena CONTENIDO en la propiedad CAMPO. No utilizar tildes. \n Ejemplo : \n campo = NOMBRE \n contenido = rom \n http://127.0.0.1:8000/eventos/NOMBRE/rom",
                         responses={200: 'Todo correcto', 404: 'Campo o contenido no existente'}, operation_id="eventos_propiedades") 
    def get(self, request, contenido='',campo=''):
        return getEvento(request, contenido, campo)

class EventosContenido(APIView):
    @swagger_auto_schema(operation_description="Devuelve los eventos que contengan la subcadena CONTENIDO en cualquiera de los campos del objeto. No utilizar tildes. \n Ejemplo: \n contenido = rom \n http://127.0.0.1:8000/eventos/rom ",
                         responses={200: 'Todo correcto', 404: 'Campo o contenido no existente'}, operation_id="eventos_contenido") 
    def get(self, request, contenido='',campo=''):
        return getEvento(request, contenido, campo)

def getEvento(request, contenido, campo):
    lista = json.loads(cargar_url(url_eventos))['result']['records']
    resultado = []
    c= str(contenido)

    if(campo=='' and contenido==''):
        return Response(lista, status=status.HTTP_200_OK)
    if(campo != ''):
        for elem in lista:
            if (campo in elem.keys()):
                if (unidecode.unidecode(c.upper()) in unidecode.unidecode(str(elem[campo]).upper())):
                    resultado.append(elem)
            else:
                return Response(status=404)
    else:
        for elem in lista:
            for v in elem.items():
                if(unidecode.unidecode(c.upper()) in unidecode.unidecode(str(v).upper())):
                    resultado.append(elem)
                    break
    if(not resultado):
        return Response(status= status.HTTP_404_NOT_FOUND)
    else:
        return Response(resultado,status=status.HTTP_200_OK)

class EventosPaginacion(APIView):
    @swagger_auto_schema(operation_description="Devuelve los eventos de forma paginada, en una página de tamaño LIMIT y saltando SKIP datos. \n Ejemplo: \n limit = 2 \n skip = 1 \n http://127.0.0.1:8000/eventos/limit=2&skip=1",
                         responses={200: 'Todo correcto'}, operation_id="eventos_paginacion") 
    def get(self, request, limit, skip=0):
        limit = int(self.kwargs.get("limit"))
        skip = int(self.kwargs.get("skip"))
        return getPaginacionEventos(request, limit, skip)

class EventosPaginacion2(APIView):
    @swagger_auto_schema(operation_description="Devuelve los LIMIT primeros datos de los eventos. \n Ejemplo: limit = 2 \n http://127.0.0.1:8000/eventos/limit=2",
                         responses={200: 'Todo correcto'}, operation_id="eventos_paginacion2") 
    def get(self, request, limit, skip=0):
        limit = int(self.kwargs.get("limit"))
        skip = 0
        return getPaginacionEventos(request, limit, skip)

def getPaginacionEventos(request, limit, skip):
    datos = json.loads(cargar_url(url_eventos))
    numDatos = len(datos['result']['records'])
    res = []
    if skip+limit > numDatos:
        limit = numDatos-skip
    if skip < numDatos:
        for i in range(skip, skip+limit):
            res.append(datos['result']['records'][i])
    return Response(res, status=status.HTTP_200_OK)

class BicisTodo(APIView):
    @swagger_auto_schema(operation_description="Devuelve toda la información sobre los carriles bici de Málaga. \n Ejemplo: http://127.0.0.1:8000/bicis/",
                         responses={200: 'Todo correcto', 404:'Not found'}, operation_id="bicis_lista")
    def get(self, request, pk=None):
        try:
            datos = cargar_url(url_bicis)
            lista = json.loads(datos)['features']
            return Response(lista, status=200)
        except:
            return Response(status=404)

class BicisID(APIView):
    @swagger_auto_schema(operation_description="Devuelvo el carril bici según el id. \n Ejemplo: id = da_carrilesBici.fid--6a251225_176106c6f0c_-3878 \n http://127.0.0.1:8000/bicis/da_carrilesBici.fid--6a251225_1761094a9bf_7266 \n (Nota: las ids cambian constantemente por lo que este ejemplo puede no funcionar, lo recomendable es coger el primer id de la consulta /bicis para probar esta consulta)",
                         responses={200: 'Todo correcto', 404:'Not found'}, operation_id="bicis_id")
    def get(self, request, id):
        lista = json.loads(cargar_url(url_bicis))['features']
        print("que")
        for elem in lista:
            if (id == elem['id']):
                return Response(elem, status=200)
        return Response(status=404)

class BicisRango(APIView):

    @swagger_auto_schema(operation_description="Consulta sobre los objetos que esten a una distancia menor de RANGO desde un punto de latitud LATITUD y longitud LONGITUD.\n Rango es la distancia a la que busca los puntos, si la diferencia (en valor absoluto) entre el punto que pones en la url y los puntos de los carriles bici es menor que el rango entonces está dentro de este. \nEjemplo: \nhttp://localhost:8000/bicis/371516.17325603,4065461.06099268&rango=1",
                         responses={200: 'Todo correcto', 404:'Not found'}, operation_id="bicis_rango")
    def get(self, request, latitud=None, longitud=None, rango=None):
        try:
            lista = json.loads(cargar_url(url_bicis))['features']
        except:
            return Response(status=404)
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

