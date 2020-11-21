from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
import urllib3, json

urlCalidadDelAire = 'https://datosabiertos.malaga.eu/recursos/ambiente/calidadaire/calidadaire.json'

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
    print(nvert)
    print(vertx)
    print(verty)
    print(testx)
    print(testy)
    while i < nvert:
        #a = (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i]
        #print(a) poniendo esto sale división por 0
        #El problema tiene pinta de estar aqui
        if (((verty[i]>testy) != (verty[j]>testy)) and
        (testx < (vertx[j]-vertx[i]) * (testy-verty[i]) / (verty[j]-verty[i]) + vertx[i])):
            print("hey")
            c = not c
        i += 1
        j = i
    return c