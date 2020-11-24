# API Rest para GraffitiApp
Esta API es parte de un proyecto evaluable para la asignatura de **Ingeniería Web** en la **Universidad de Málaga**.

Actualmente, nuestra API alberga diversos métodos encargados de consultar, crear, modificar y eliminar información relativa a:
* Usuarios.
* Publicaciones.
* Graffitis.
* Comentarios.

Además, contamos con una conexión a la API *Datos abiertos del Ayuntamiento de Málaga* para la consulta de datos de interés de diversa índole, en concreto para la consulta de:
* Datos de la calidad del aire en la ciudad.
* Eventos próximos que se llevarán a cabo.

**¡Para que no te pierdas nada de lo pasa en nuestra ciudad!**

### Tecnologías usadas
Para llevar este proyecto acabo hemos usado las siguientes tecnologías:
* [Python 3](https://www.python.org/download/releases/3.0/)
* [DJango](https://www.djangoproject.com/)
* [MongoDB](mongodb.com)
* [DJango Rest Framework](https://www.django-rest-framework.org/)

## Instalación y puesta a punto
Para poder ejecutar nuestra API en su propia máquina, solo tiene que seguir estos pasos:
 1. Instalar MongoDB desde su [página oficial](https://www.mongodb.com/) o bien preparar una base de datos propia.
 2. Instalar Python (Que ya viene con [pip](https://pypi.org/project/pip/) instalado por defecto :tada:)
 ``` shell
 pip install python
 ```
 3. Descargar nuestro proyecto
 ``` shell
 git clone https://github.com/juliarobles/graffitisWeb.git
 ```
 O bien descargándolo directamente desde aquí.
 4. Instalar los requisitos especificados dentro del archivo requirements.txt,
 ``` shell
 pip install -r requirements.txt.
 ```
Y con eso, tenemos todo a punto para ejecutar la aplicación.

## Puesta en marcha del servicio
Para ello, solo hemos de realizar dos tareas:
 1. Poner en marcha la base de datos.
 2. Ejecutar la aplicación mediante el siguiente comnado:
  ``` shell
 python manage.py runserver.
 ```
 
 Y todo listo, ¡ahora podrá acceder a la API de forma local!
