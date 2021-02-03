# API Rest y cliente para GraffitiApp (Grupo C4)
Este es un proyecto evaluable para la asignatura de **Ingeniería Web** en la **Universidad de Málaga**.
Consta de dos partes: una **API Rest** y un **cliente** de la misma. Además, está subido a la nube con **MongoDB Atlas** y **Heroku**.

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
* Iniciar sesión con OAuth de Google.
* Ver todas las publicaciones en el inicio.
* Buscar entre todas las publicaciones por uno o varios hashtags, uno o varios usuarios o una o varias palabras contenidas en el título o la descripción.
* Consultar los eventos del Ayuntamiento de Málaga.
* Ver el perfil de cualquier usuario, incluido sí mismo, junto con todas las publicaciones que este ha creado o en las que ha contribuido.
* Seguir y dejar de seguir a otro usuario.
* Ver una publicación detallada junto a todos los *graffitis* que la forman.
* Crear una nueva publicación.
* Editar una publicación creada por tí.
* Eliminar una publicación creada por tí.
* Contribuir a una publicación ya existente con una actualización (*graffiti*) del mismo.
* Eliminar una contribución (*graffiti*) creada por tí.
* Realizar comentarios en las publicaciones.
* Eliminar los comentarios realizados el usuario de la sesión.
* Dar *me gusta* a las publicaciones (con la posibilidad de quitarlo), tanto en el inicio como en los detalles de la misma.
* Compartir un usuario o una publicación por redes sociales.
* Cerrar sesión de Google.
* Consulta global de todos los usuarios de la aplicación.
* Ver el mapa de publicaciones.
* Consultar la calidad del aire.
* Editar la descripción del usuario.
* Recibir información del tiempo actual.
* Recibir una paleta aleatoria de colores.



### Tecnologías usadas
Para llevar este proyecto a cabo hemos usado las siguientes tecnologías:
* [Python 3](https://www.python.org/download/releases/3.0/)
* [DJango](https://www.djangoproject.com/)
* [MongoDB](mongodb.com)
* [DJango Rest Framework](https://www.django-rest-framework.org/)

## Instalación y puesta a punto
¡Esta aplicación está en la nube! Para acceder a ella entra en: https://graffitisweb-c4.herokuapp.com/

Aún así si se quisiera ejecutar localmente solo tiene que seguir estos pasos:
 1. En el caso de no querer utilizar MongoDB Atlas, instalar MongoDB desde su [página oficial](https://www.mongodb.com/) o bien preparar una base de datos propia con el nombre de _iweb_. OPCIONAL: puede también usar los datos de muestra proporcionados en la carpeta _Ejemplos bd_.
 2. Instalar Python (Que ya viene con [pip](https://pypi.org/project/pip/) instalado por defecto :tada:)
 ``` shell
 pip install python
 ```
 
 :warning:Nota importante: A partir de Python 3.9 se ha eliminado una función que utiliza la librería Flickrapi, por lo que se debe usar Python 3.8 para ejecutar esta aplicación.

 3. Descargar nuestro proyecto:
 
  Si únicamente quieres hacer uso del API Rest usar:
 ``` shell
 git clone https://github.com/juliarobles/graffitisWeb.git
 ```
  Si quieres hacer uso tanto de la API Rest como del cliente usar:
 ``` shell
 git clone --branch html https://github.com/juliarobles/graffitisWeb.git
 ```
  Si quieres hacer uso de la aplicación completa adaptada a la nube:
 ``` shell
 git clone --branch nube-heroku https://github.com/juliarobles/graffitisWeb.git
 ```
  O bien puedes descargar la opción que prefieras directamente desde aquí.
 
 4. (Solo en el caso de la rama nube-heroku) Antes de la primera ejecución ejecutar:
 ``` shell
 python manage.py collectstatic
 ```
 
 5. Instalar los requisitos especificados dentro del archivo requirements.txt,
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


## Puesta en marcha del servicio en local
Para ello, solo hemos de ejecutar la aplicación mediante el siguiente comnado:
 ``` shell
 python manage.py runserver
 ```
 La OpenAPI de la API Rest se encuentra en /api mientras que al cliente se accede desde la raiz de la aplicación.
 
 Y todo listo, ¡Disfruta! :stuck_out_tongue_winking_eye:
