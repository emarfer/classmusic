# 09 - La Fase de Enriquecimiento y Carga

Con el componente `TransformScrobble` finalizado, ya tenemos una forma robusta de convertir el JSON de la API en una lista de objetos `Scrobble` limpios. El siguiente paso natural es preparar y ejecutar la carga de estos datos en nuestra base de datos MySQL.

Este documento resume las importantes decisiones de diseño que tomamos para definir cómo se realizaría este proceso.

## 1. El Siguiente Paso: ¿Orquestador o Cargador?

La primera idea fue crear directamente el script orquestador final en `src/etl/ingest_scrobbles/ingest_scrobble.py`. Sin embargo, nos dimos cuenta de que nos faltaba un paso intermedio crucial: nuestro `MysqlManager` sabía cómo conectarse a la base de datos, pero aún no sabía cómo **cargar** o guardar datos.

**Decisión**: Antes de crear el orquestador, debíamos ampliar la funcionalidad de `MysqlManager` para que pudiera realizar inserciones en la base de datos.

## 2. Decisión de Diseño 1: ¿Dónde Vive la Lógica de Carga?

Aquí surgió una pregunta de arquitectura fundamental: ¿la lógica para guardar los scrobbles debía vivir en un nuevo fichero dentro de la carpeta ETL, o dentro de la clase `MysqlManager`?

**Decisión**: La lógica de carga debía residir **exclusivamente en `MysqlManager`**.

*   **Razón**: El principio de **Separación de Responsabilidades**. `MysqlManager` debe ser el único "guardián" de la base de datos. Cualquier componente que necesite interactuar con MySQL debe hacerlo a través de los métodos que `MysqlManager` expone, sin conocer los detalles de SQL. Esto asegura que si en el futuro cambiamos de base de datos, teóricamente solo tendríamos que modificar `MysqlManager`.

## 3. Decisión de Diseño 2: ¿Método Específico o Genérico?

Una vez decidido que la lógica estaría en `MysqlManager`, exploramos cómo implementarla. Se planteó una idea avanzada: crear un método genérico que leyera plantillas de ficheros `.sql` y las ejecutara.

**Decisión**: Adoptar un **enfoque híbrido**.

1.  **Para ahora**: Implementar un método **específico y optimizado** como `save_scrobbles(scrobbles: list)` en `MysqlManager`. Para una tarea tan común y sensible como una inserción masiva, un método específico nos permite usar las funciones de "bulk insert" de SQLAlchemy, que son más seguras (protegen contra inyección SQL) y tienen mejor rendimiento que generar un `INSERT` gigante manualmente.
2.  **Para el futuro**: Mantener la idea de un ejecutor de plantillas genérico para tareas más complejas, como `SELECT`s para informes o análisis, donde tener el SQL en un fichero `.sql` es una gran ventaja.

## 4. Decisión de Diseño 3: El Nacimiento de la Fase de "Enriquecimiento"

Al analizar el código antiguo, vimos que antes de insertar se hacían dos cosas:
1.  Se transformaba el `uts` a `fechahora` (lógica de `utslocal`).
2.  Se escapaban caracteres especiales (lógica de `car_esp`).
3.  Se buscaba y actualizaba el `id_can` después de la inserción (lógica de `act_scro`).

Llegamos a las siguientes conclusiones:

*   **Escapado de caracteres (`car_esp`)**: Ya no es necesario. Al usar las consultas parametrizadas de SQLAlchemy en `save_scrobbles`, la librería se encarga de escapar los datos de forma segura y automática.
*   **Transformaciones y Búsquedas (`fechahora`, `id_can`)**: Estos no son datos que vengan directamente de la API, sino que se derivan o se obtienen de nuestra propia base de datos.

**Decisión Final**: Se definió una nueva fase en nuestro ETL, la fase de **Enriquecimiento (Enrich)**. El modelo `Scrobble` se mantiene puro, representando solo los datos limpios de la API.

El flujo de nuestro orquestador `ingest_scrobble.py` queda así:
1.  **Extract**: `LastfmClient` obtiene los datos brutos.
2.  **Transform**: `TransformScrobble` los convierte en `list[Scrobble]`.
3.  **Enrich**: Un nuevo componente "Enricher" tomará la `list[Scrobble]`, calculará `fechahora` y buscará el `id_can` para cada uno.
4.  **Load**: `MysqlManager.save_scrobbles` recibirá los datos ya enriquecidos y completos para realizar la inserción masiva.

Este enfoque "Enriquecer y Luego Cargar" es más robusto, eficiente y asegura la integridad de los datos desde el primer momento, evitando las complejas operaciones de `UPDATE` y borrado a posteriori.

---
## 5. Implementación de la Clase `EnrichScrobble`

Con el plan claro, procedimos a crear el componente "Enricher".

### 5.1. Formato de Salida: ¿Lista de Diccionarios o DataFrame?

La primera decisión para el `Enricher` fue definir el formato de sus datos de salida. Dado que el `MysqlManager` usaría la carga masiva, ¿qué formato era mejor para él?

**Decisión**: El `Enricher` devolverá un **DataFrame de Pandas**.
*   **Razón**: SQLAlchemy tiene una integración excelente con Pandas a través del método `DataFrame.to_sql()`. Es una forma muy conveniente y legible de realizar inserciones masivas, y se alinea con las prácticas comunes en flujos de trabajo de datos.

### 5.2. Primeros Pasos con TDD: `fechahora` y Vectorización

Empezamos el desarrollo de `EnrichScrobble` con TDD, centrándonos primero en la tarea más sencilla: añadir la columna `fechahora`.

**Decisión**: Usar operaciones **vectorizadas** de Pandas.
*   **Razón**: En lugar de usar un bucle o el método `.apply()`, la función vectorizada `pd.to_datetime(df['uts'], unit='s')` es mucho más rápida y eficiente, ya que opera sobre toda la columna de una vez. Esto representa una mejora significativa de rendimiento.

### 5.3. Añadiendo Lógica de Negocio: Álbumes Desconocidos

Identificamos una regla de negocio del antiguo proyecto: si un álbum era un string vacío (`""`), debía transformarse en `"[Desconocido]"`.

**Decisión**: Esta lógica pertenece al `Enricher`.
*   **Razón**: Es una regla de transformación de datos, no una responsabilidad de la base de datos. Se implementó con `df.loc[...]`, una forma idiomática de pandas para realizar asignaciones condicionales. El `MysqlManager` recibirá los datos ya limpios.

### 5.4. Próximo Paso: Búsqueda de `id_can`

El paso más complejo es obtener el `id_can` para cada scrobble. La estrategia definida es:

1.  **En `EnrichScrobble`**:
    *   Crear una columna `completo` en el DataFrame, concatenando `artist`, `album` y `title`.
    *   Obtener una lista de todos los valores `completo` únicos.
2.  **En `MysqlManager`**:
    *   Crear un nuevo método, `get_id_can_map(completos: list)`, que recibirá la lista de strings `completo`.
    *   Este método ejecutará **una única consulta `SELECT`** a la base de datos (`SELECT completo, id_can FROM total WHERE completo IN (...)`) para obtener todos los IDs de una vez.
    *   Devolverá un diccionario que mapea cada string `completo` a su `id_can`.
3.  **De vuelta en `EnrichScrobble`**:
    *   Usar este diccionario para popular la columna `id_can` en el DataFrame, probablemente con el método `.map()` de pandas.

Este enfoque de "búsqueda masiva" es crucial para evitar el problema de rendimiento "N+1" (hacer una consulta a la base de datos por cada fila).

**Conclusión**: Con estos pasos, `EnrichScrobble` está casi listo. La tarea inmediata es ir a `MysqlManager` y crear el método `get_id_can_map` con sus correspondientes tests.
