# 08 - La Fase de Transformación: Creando el `TransformScrobble`

Con la fase de **Extracción** completada (`LastfmClient`) y nuestro modelo de datos definido (`Scrobble`), nos adentramos en el corazón de nuestro ETL: la fase de **Transformación**. El objetivo es crear un componente que traduzca los datos brutos de la API a nuestros objetos de dominio limpios y validados.

## 1. Ubicación y Responsabilidad: `TransformScrobble`

La primera decisión fue dónde y cómo debía vivir este componente.

1.  **Ubicación**: Siguiendo tu propuesta, decidimos crear una estructura más específica para futuros ETLs. Creamos el directorio `src/etl/ingest_scrobbles/`, reconociendo que podríamos tener otros procesos (como `create_playlists`) en el futuro. El transformador viviría en `transformer.py` dentro de esta nueva carpeta.
2.  **Nombre**: Elegimos el nombre `TransformScrobble` para la clase, ya que es mucho más descriptivo que un genérico `Transformer`.
3.  **Responsabilidad**: Acordamos que, siguiendo el principio de **Separación de Responsabilidades**, esta clase tendría una única y clara misión: ser un "traductor" puro. No debe saber nada sobre la API, la base de datos o de dónde vienen los datos. Su única función es:
    *   **Input**: Recibir una lista de diccionarios con datos en bruto.
    *   **Output**: Devolver una lista de objetos `Scrobble`.

## 2. Desarrollo Guiado por Tests (TDD) "de Abajo Hacia Arriba"

En lugar de abordar toda la transformación de golpe, adoptamos una estrategia "de abajo hacia arriba", empezando por la unidad de trabajo más pequeña.

Creamos un método privado, `_extract_scrobble_data`, cuya única responsabilidad sería transformar **un solo** diccionario de scrobble en bruto.

Los tests iniciales se centraron exclusivamente en este método, verificando que era capaz de "aplanar" la estructura anidada del JSON de la API y que los datos resultantes eran compatibles con nuestro modelo `Scrobble`.

## 3. Refactorización Clave: Devolver `Scrobble` Directamente

Nuestra primera versión de `_extract_scrobble_data` devolvía un diccionario. Aunque funcionaba, nos dimos cuenta de que podíamos hacerlo más claro y robusto.

La refactorización clave, propuesta por ti, fue modificar `_extract_scrobble_data` para que construyera y devolviera directamente una **instancia del objeto `Scrobble`**, en lugar de un diccionario intermedio.

*   **Beneficios**:
    *   **Mejor encapsulación**: Toda la lógica de creación del objeto `Scrobble` queda contenida en el método privado.
    *   **Mayor claridad**: La firma del método (`-> Scrobble`) ahora describe perfectamente lo que hace.
    *   **Simplificación**: El método público que construyamos después se volverá más simple.

Este cambio también nos obligó a refactorizar nuestros tests, eliminando uno que se volvió redundante y adaptando el principal para que esperara un objeto `Scrobble` como resultado. Un ejemplo perfecto del ciclo "Rojo-Verde-**Refactorizar**" de TDD.

## 4. Creación del Método Público

Con la lógica para un solo elemento ya probada, creamos el método público `transform_tracks_list`. Su implementación es ahora muy sencilla:

1.  Recibe la lista de diccionarios en bruto.
2.  Itera sobre ella.
3.  Llama a `_extract_scrobble_data` para cada elemento.
4.  Recopila los objetos `Scrobble` resultantes en una nueva lista.
5.  Devuelve la lista de `Scrobble`.

Creamos tests específicos para este método que verifican su comportamiento con listas de uno y varios elementos.

## 5. Decisión de Diseño Final: Una Clase de Servicio "Sin Estado"

Finalmente, discutimos sobre el constructor `__init__(self): pass`. Esto nos llevó a una decisión de diseño importante: `TransformScrobble` es una **clase de servicio sin estado (stateless service class)**.

Su propósito es ofrecer una funcionalidad (transformar datos), pero no necesita "recordar" ninguna información entre llamadas. Por ello, el diseño actual, donde se crea una instancia y se usan sus métodos pasándole los datos, es más limpio, flexible y reutilizable que un diseño "con estado" donde los datos se pasarían en el constructor. El `__init__` vacío es, por tanto, una decisión de diseño intencionada y correcta.

## 6. Conclusión

Hemos finalizado la fase de **Transformación** de nuestro ETL. Ahora tenemos un componente, `TransformScrobble`, robusto, bien probado y diseñado siguiendo principios sólidos de software, listo para entregar una lista de objetos `Scrobble` limpios al siguiente y último paso del proceso: la **Carga**.
