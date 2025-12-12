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
