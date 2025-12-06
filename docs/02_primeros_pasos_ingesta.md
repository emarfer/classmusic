# Pasos para la Ingesta de Datos en `classmusic`

1.  **Diseñar la Estructura de Carpetas:**
    Crear una estructura lógica dentro de `src/` que separe las responsabilidades. Por ejemplo: `src/config/` para la configuración, `src/clients/` para los clientes de API, `src/database/` para la lógica de la base de datos, `src/models/` para nuestras clases de datos y `src/ETL/` para los procesos de ingesta.

### El Principio Clave: Separación de Responsabilidades

La idea principal detrás de esta estructura es un principio de diseño de software llamado **"Separación de Responsabilidades"** (Separation of Concerns).

Imagina que estás cocinando. Tienes un área para cortar los ingredientes, otra para cocinarlos (los fuegos) y otra para emplatar. No lo haces todo en el mismo sitio y con las mismas herramientas, ¿verdad? Cada área tiene una responsabilidad clara.

En el código, es igual. En lugar de tener un único fichero "gigante" que hable con la API, procese los datos y los guarde en la base de datos (como a veces pasaba en `musicapp`, donde ficheros como `sqltools.py` hacían muchas cosas distintas), vamos a crear "cajones" especializados. Esto nos da un código mucho más limpio, fácil de entender, de probar y de modificar en el futuro sin miedo a romperlo todo.

---

### La Estructura de Carpetas Explicada

Nuestra carpeta principal de código será `src/` (de *source*, "fuente" u "origen" en inglés). Todo nuestro código Python vivirá aquí dentro, separado del resto de archivos del proyecto como los `docs/`, `tests/`, etc.

```
classmusic/
├── src/
│   ├── __init__.py
│   ├── models/
│   ├── clients/
│   ├── database/
│   ├── config/
│   └── etl/
└── ... (otros archivos como docs/, tests/, etc.)
```
*Nota: El archivo `__init__.py` es un fichero (normalmente vacío) que le dice a Python: "oye, esta carpeta no es una carpeta cualquiera, es un 'paquete' de código", lo que nos permite importar módulos de unas carpetas a otras fácilmente.*

Ahora, veamos cada "cajón":

#### `src/models/`
*   **¿Qué va aquí?** Aquí definiremos las "plantillas" o "moldes" de nuestros datos. Serán clases de Python que representan los conceptos clave de nuestro proyecto. Por ejemplo, tendríamos un archivo `track.py` con una clase `Track`, un `artist.py` con una clase `Artist`, etc.
*   **¿Por qué?** Esta es la médula de tu idea de "classmusic". En lugar de que un "track" sea una simple fila en un DataFrame de Pandas o un diccionario genérico, será un objeto `Track` con atributos claros (ej: `track.title`, `track.duration_ms`). Esto hace que tu código sea mucho más legible y robusto, y si el día de mañana quieres añadir un nuevo dato a un track (por ejemplo, `track.lyrics_url`), sabes exactamente dónde tienes que ir a modificarlo: a la clase `Track` en esta carpeta.

#### `src/clients/`
*   **¿Qué va aquí?** La palabra "cliente" aquí se refiere a un programa que consume un servicio. Esta carpeta contendrá todo el código que se comunica con servicios externos, es decir, las APIs. Tendríamos, por ejemplo, un fichero `lastfm_client.py`.
*   **¿Por qué?** Aislamos completamente la lógica de comunicación con el exterior. La clase `LastfmAPIClient` que vivirá aquí será la única en todo el proyecto que sepa cómo se hace una petición a Last.fm (la URL, los parámetros, las claves de API...). El resto de tu aplicación no necesitará saber esos detalles. Simplemente le dirá al cliente: `dame_las_ultimas_canciones()` y el cliente se encargará del resto. Si Last.fm cambia su API, ¡solo tienes que modificar este fichero!

#### `src/database/`
*   **¿Qué va aquí?** Todo el código que interactúa directamente con tu base de datos MySQL. Aquí vivirá nuestra futura clase `DatabaseManager`.
*   **¿Por qué?** Igual que con los clientes de API, aislamos la responsabilidad de la persistencia de datos. Esta clase será la única que sepa cómo construir las sentencias `INSERT`, `UPDATE` o `SELECT` en SQL. El resto de la aplicación le dará órdenes sencillas como `guarda_este_track(track_object)` o `dame_el_artista_por_nombre('U2')`. Si algún día decidieras cambiar de MySQL a otra base de datos como PostgreSQL, teóricamente solo tendrías que "traducir" el código dentro de esta carpeta, y el resto de la aplicación seguiría funcionando igual.

#### `src/config/`
*   **¿Qué va aquí?** Un módulo o clase responsable de cargar y proveer todas las configuraciones de la aplicación: la clave de la API, la contraseña de la base de datos, el nombre de usuario, etc.
*   **¿Por qué?** Para tener un único punto de verdad para toda la configuración. Evitamos tener `os.getenv("MI_CLAVE")` repartido por todo el código. En su lugar, el código le preguntará al módulo de configuración los valores que necesita. Esto facilita la gestión de configuraciones diferentes para desarrollo y producción.

#### `src/etl/`
*   **¿Qué va aquí?** "ETL" son las siglas de **E**xtract, **T**ransform, **L**oad (Extraer, Transformar y Cargar). Esta carpeta contendrá los scripts de alto nivel que orquestan todo el proceso.
*   **¿Por qué?** Este es el "director de orquesta". Un script aquí dentro (`ingest_scrobbles.py`, por ejemplo) no contendrá lógica de API ni de SQL. En su lugar, usará las otras piezas que hemos construido:
    1.  Usará el **cliente** (`LastfmAPIClient`) para **Extraer** los datos.
    2.  Usará los **modelos** (`Track`, `Artist`) para **Transformar** esos datos crudos en objetos limpios y validados.
    3.  Usará el gestor de la **base de datos** (`DatabaseManager`) para **Cargar** (guardar) esos objetos en MySQL.

Separar la lógica de esta manera hace que cada parte sea más simple, reutilizable y, muy importante, **fácil de probar de forma aislada**.

---
2.  **Crear un Módulo de Configuración Centralizado:**
    En lugar de cargar variables de entorno en varios sitios, crearemos un único módulo que se encargue de leer las credenciales de la API de Last.fm y de la base de datos MySQL.

3.  **Definir el "Modelo de Dominio" con Clases:**
    Esta es la parte "class" de `classmusic`. Crearemos clases de Python para representar nuestras entidades principales: `Artist`, `Album` y `Track`. Esto nos ayudará a tener un código más limpio y organizado. Podríamos usar `pydantic` (que ya instalamos) para la validación automática de los datos.

4.  **Construir un Cliente de API Reutilizable:**
    Crearemos una clase `LastfmAPIClient`. Su única responsabilidad será comunicarse con la API de Last.fm. Tendrá métodos como `get_recent_tracks(user, from_date)` que devolverán los datos (idealmente, como una lista de nuestras clases `Track`).

5.  **Crear un Gestor de Base de Datos:**
    Una clase `DatabaseManager` que se encargue de toda la interacción con MySQL. Tendrá la lógica de conexión y métodos como `save_track(track)`, `get_artist_by_name(name)`, etc. Esto evitará tener código SQL disperso por todo el proyecto.

6.  **Desarrollar el Orquestador del Proceso ETL:**
    Crearemos un script principal (p. ej. `main_ingestion.py`) que use las clases anteriores para orquestar el proceso completo:
    *   Inicializa el `LastfmAPIClient` y el `DatabaseManager`.
    *   Pide los últimos tracks a la API.
    *   Para cada track, usa el `DatabaseManager` para guardarlo en la base de datos, gestionando la lógica de si el artista o el álbum ya existen.

7.  **Implementar un Sistema de "Logging":**
    En lugar de usar `print()`, configuraremos un sistema de logging para registrar lo que está sucediendo. Esto nos permitirá tener un registro claro de la ingesta, los éxitos y los errores de una manera mucho más profesional.