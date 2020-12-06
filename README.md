# API Rest y cliente para GraffitiApp (Grupo C4)
Este es un proyecto evaluable para la asignatura de **Ingeniería Web** en la **Universidad de Málaga**.
Consta de dos partes: una **API Rest** y un **cliente** de la misma.

Actualmente, nuestra API alberga diversos métodos encargados de consultar, crear, modificar y eliminar información relativa a:
* Usuarios.
* Publicaciones.
* Graffitis.
* Comentarios.

Además, contamos con una conexión a la API *Datos abiertos del Ayuntamiento de Málaga* para la consulta de datos de interés de diversa índole, en concreto para la consulta de:
* Datos de la calidad del aire en la ciudad.
* Eventos próximos que se llevarán a cabo.
* Carriles bici de la ciudad.

**¡Para que no te pierdas nada de lo pasa en nuestra ciudad!**

Nuestro cliente, llamado *Underground* y cuyo código completo se encuentra dentro de la carpeta *ClienteApp*, hace uso de la anterior permite:
* Iniciar sesión provisionalmente. Este sistema será sustituido proximamente por OAuth de Google.
* Ver todas las publicaciones en el inicio.
* Buscar entre todas las publicaciones por uno o varios hashtags, uno o varios usuarios o una o varias palabras contenidas en el título o la descripción.
* Ver una publicación detallada junto a todos los *graffitis* que la forman.
* Ver el perfil de cualquier usuario, incluido sí mismo, junto con todas las publicaciones que este ha creado o en las que ha contribuido.
* Seguir y dejar de seguir a otro usuario.
* Crear una nueva publicación.
* Eliminar una publicación creada por tí.
* Contribuir a una publicación ya existente con una actualización (*graffiti*) del mismo.
* Eliminar una contribución (*graffiti*) creada por tí.
* Realizar comentarios en las publicaciones.
* Eliminar los comentarios realizados el usuario de la sesión.
* Dar *me gusta* a las publicaciones (con la posibilidad de quitarlo), tanto en el inicio como en los detalles de la misma.
* Compartir un usuario o una publicación por redes sociales.
* Cerrar sesión provisionalmente.



### Tecnologías usadas
Para llevar este proyecto a cabo hemos usado las siguientes tecnologías:
* [Python 3](https://www.python.org/download/releases/3.0/)
* [DJango](https://www.djangoproject.com/)
* [MongoDB](mongodb.com)
* [DJango Rest Framework](https://www.django-rest-framework.org/)

## Instalación y puesta a punto
Para poder ejecutar nuestra API en su propia máquina, solo tiene que seguir estos pasos:
 1. Instalar MongoDB desde su [página oficial](https://www.mongodb.com/) o bien preparar una base de datos propia con el nombre de _iweb_. OPCIONAL: puede también usar los datos de muestra proporcionados en la carpeta _Ejemplos bd_.
 2. Instalar Python (Que ya viene con [pip](https://pypi.org/project/pip/) instalado por defecto :tada:)
 ``` shell
 pip install python
 ```
 3. Descargar nuestro proyecto:
 
  Si únicamente quieres hacer uso del API Rest usar:
 ``` shell
 git clone https://github.com/juliarobles/graffitisWeb.git
 ```
  Si quieres hacer uso tanto de la API Rest como del cliente usar:
 ``` shell
 git clone --branch html https://github.com/juliarobles/graffitisWeb.git
 ```
  O bien puedes descargar la opción que prefieras directamente desde aquí.
 
 4. Instalar los requisitos especificados dentro del archivo requirements.txt,
 ``` shell
 pip install -r requirements.txt
 ```
Y con eso, tenemos todo a punto para ejecutar la aplicación.

Nota: Es probable que antes de poder ejecutar la aplicación sea necesario migrar las colecciones que trae Django por defecto para terminar de inicializar la base de datos. 
En este caso usar:
``` shell
python manage.py makemigrations
python manage.py migrate
 ```


## Puesta en marcha del servicio
Para ello, solo hemos de realizar dos tareas:
 1. Poner en marcha la base de datos.
 2. Ejecutar la aplicación mediante el siguiente comnado:
 ``` shell
 python manage.py runserver.
 ```
 La OpenAPI de la API Rest se encuentra en la raíz del proyecto, si quieres acceder al cliente deberas entrar en http://127.0.0.1:8000/principal/.
 
 Y todo listo, ¡Disfruta! :stuck_out_tongue_winking_eye:
