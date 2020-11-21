from django.shortcuts import render
from django.http import HttpResponse
import urllib3, json

# Consulta normal 
# https://datosabiertos.malaga.eu/api/3/action/datastore_search  

# Consulta SQL
# https://datosabiertos.malaga.eu/api/3/action/datastore_search_sql


def leer_objeto(request):
    # ?resource_id=7f96bcbb-020b-449d-9277-1d86bd11b827&limit=5&q=title:jones
    url = 'https://datosabiertos.malaga.eu/api/3/action/datastore_search'  
    http = urllib3.PoolManager()
    r = http.request('GET',
     url, 
     fields={'resource_id':'7f96bcbb-020b-449d-9277-1d86bd11b827', 'limit':'5', 'q': 'title:jones'}
     )
    return HttpResponse(r.data)





    
  