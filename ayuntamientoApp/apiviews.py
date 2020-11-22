from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
import urllib3, json, unidecode

urlCalidadDelAire = 'https://datosabiertos.malaga.eu/recursos/ambiente/calidadaire/calidadaire.json'

def comprobar_distancia(latitud1, latitud2, longitud1, longitud2, rango):
    return latitud1-latitud2<abs(rango) and longitud1-longitud2<abs(rango) 
     
class CalidadDelAireTodo(APIView):
    def get(self, request, pk=None):
        http = urllib3.PoolManager()
        r = http.request('GET', urlCalidadDelAire)
        datos = json.loads(r.data)
        return Response(datos, status=status.HTTP_200_OK)

class CalidadDelAireCoordenadas(APIView):
    def get(self, request, x, y):
        coordX = float(self.kwargs.get("x"))
        coordY = float(self.kwargs.get("y"))
        http = urllib3.PoolManager()
        r = http.request('GET', urlCalidadDelAire)
        datos = json.loads(r.data)
        zonas = {}#Quizas haga falta que sea un diccionario
        i = 0
        for zona in datos['features']:
            coordenadas = zona['geometry']['coordinates']
            vertx = []
            verty = []
            for x in coordenadas[0]:
                vertx.append(float(x[1])) #No se porque han guardado las coordenadas (y, x)
            for y in coordenadas[0]:
                verty.append(float(y[0]))
            res = pnpoly(len(vertx), vertx, verty, coordX, coordY)

            if res:
                zonas["zona " + str(i)] = zona 
                i += 1
        return Response(zonas, status=status.HTTP_200_OK)

#Algoritmo: https://stackoverflow.com/questions/11716268/point-in-polygon-algorithm
#nvert = numero de vertices, vertx y verty = arrays que contienen x e y coordenadas del poligono, testx y testy = nuestras coordenadas
def pnpoly(nvert, vertx, verty, testx, testy):
    c = False
    i = 0
    j = nvert-1
    # print(nvert)
    # print(vertx)
    # print(verty)
    # print(testx)
    # print(testy)
    while i < nvert:
        #a = (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i]
        #print(a) poniendo esto sale división por 0
        #El problema tiene pinta de estar aqui
        if (((verty[i]>testy) != (verty[j]>testy)) and
        (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i])):
            c = not c
        j = i
        i += 1
    return c

class eventos(APIView):

    def get(self, request, contenido,campo=''):
        http = urllib3.PoolManager()
        r = http.request('GET',
        'https://datosabiertos.malaga.eu/api/3/action/datastore_search',
        fields={'resource_id':'7f96bcbb-020b-449d-9277-1d86bd11b827'}
        )

        lista = json.loads(r.data)['result']['records']
        # lista = y['result']['records']
        resultado = []
        c= str(contenido)
        if(campo != ''):
            for elem in lista:
                if (unidecode.unidecode(c.casefold()) in unidecode.unidecode(str(elem[campo]).casefold())):
                    resultado.append(elem)
        else:
            for elem in lista:
                for v in elem.items():
                    if(unidecode.unidecode(c.casefold()) in unidecode.unidecode(str(v).casefold())):
                        resultado.append(elem)
                        break
        return Response(resultado,status=status.HTTP_200_OK)

class bicis(APIView):
    
    def get(self, request, latitud, longitud, rango):
        http = urllib3.PoolManager()
        r = http.request(
            'GET', 
            'https://datosabiertos.malaga.eu/recursos/transporte/trafico/da_carrilesBici-25830.geojson'
        )
        
        lista = json.loads(r.data)['features']
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