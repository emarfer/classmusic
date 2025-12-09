# Añadiendo `get_recenttracks` a `LastfmClient` con TDD

Después de construir y probar de forma robusta el método privado `_make_request`, el siguiente paso es crear nuestro primer método público que lo utilice: `get_recenttracks`. El objetivo de este método es obtener la lista de canciones escuchadas recientemente por el usuario.

Este documento resume el proceso TDD seguido y establece los próximos pasos, teniendo en cuenta la complejidad real de la API de Last.fm.

## 1. TDD para la Creación de `get_recenttracks`

Seguimos un ciclo Rojo-Verde-Refactorizar estricto para asegurarnos de que el método se construía correctamente.

### Paso 1: Testear la Llamada al Método Correcto (Rojo -> Verde)

El primer objetivo era simple: asegurarnos de que `get_recenttracks` llamaba a `_make_request` con el nombre del método de la API correcto.

**Test Inicial (Rojo):**
Escribimos un test que fallaba porque `get_recenttracks` no existía en la clase `LastfmClient`.

```python
# En tests/clients/test_lastfm_client.py
@patch("src.clients.lastfm_client.LastfmClient._make_request")
def test_get_recenttracks_calls_make_request_with_valid_method(self, mock_make_request):
    method = "user.getrecenttracks"

    # Falla aquí con AttributeError porque get_recenttracks no existe
    self.client.get_recenttracks() 

    mock_make_request.assert_called_once_with(method)
```
*Lección aprendida sobre `@patch`*: El decorador necesita la ruta completa al objeto que se va a mockear. Un intento inicial con `@patch("src.clients.lastfm_client._make_request")` falló porque `_make_request` es un método de `LastfmClient`, no un atributo del módulo. La ruta correcta es `"src.clients.lastfm_client.LastfmClient._make_request"`.

**Código Mínimo (Verde parcial):**
Añadimos el método vacío a la clase.

```python
# En src/clients/lastfm_client.py
def get_recenttracks(self):
    pass
```
El test ahora fallaba con `AssertionError`, porque `_make_request` no era llamado.

**Implementación Final (Verde):**
Añadimos la llamada a `_make_request`.

```python
# En src/clients/lastfm_client.py
def get_recenttracks(self):
    recenttracks = self._make_request("user.getrecenttracks")
    return recenttracks
```
Con esto, el test pasó, confirmando que nuestro método público utiliza correctamente el método privado con los argumentos esperados.

## 2. Análisis de la Complejidad Real de la API

Antes de seguir, analizamos cómo es una respuesta real de la API de Last.fm para `user.getrecenttracks`, descubriendo varias complejidades:

1.  **Paginación**: La API no devuelve todos los resultados de una vez. Los divide en páginas, y por defecto devuelve 50 canciones por página.
2.  **Estructura Anidada**: La lista de canciones no es la respuesta principal. Está anidada dentro de la estructura del JSON, concretamente en la clave `["recenttracks"]["track"]`.
3.  **Metadatos de Paginación**: La información sobre el número total de páginas, la página actual, etc., se encuentra en una clave separada: `["recenttracks"]["@attr"]`.
4.  **Filtrado por Fecha**: La API acepta un parámetro opcional `from` (un timestamp UTS) para obtener solo los "scrobbles" desde una fecha determinada.

Un ejemplo de la estructura de la respuesta es:
```json
{
    "recenttracks": {
        "track": [
            {"name": "Song A", "artist": {"#text": "Artist 1"}, ...},
            {"name": "Song B", "artist": {"#text": "Artist 2"}, ...}
        ],
        "@attr": {
            "user": "sinatxester",
            "totalPages": "2582",
            "page": "1",
            "perPage": "50",
            "total": "129073"
        }
    }
}
```

## 3. Próximos Pasos (Hoja de Ruta)

Dado este nuevo entendimiento, la funcionalidad de `get_recenttracks` debe construirse de forma incremental.

### Paso 3.1: Extraer la lista de "tracks" de una sola página

El próximo test se centrará en verificar que `get_recenttracks` puede procesar una respuesta simulada de **una sola página** y devolver únicamente la lista de canciones.

- **Test:**
  - Mockear `_make_request` para que devuelva un JSON con la estructura anidada y `totalPages: "1"`.
  - Llamar a `get_recenttracks()`.
  - Hacer un `assert` de que el resultado es la **lista** que estaba dentro de `["recenttracks"]["track"]`, no el diccionario completo.
- **Implementación:**
  - Modificar `get_recenttracks` para que acceda a `response["recenttracks"]["track"]` antes de devolver el resultado.

### Paso 3.2: Implementar el parámetro `from`

Una vez que la extracción funcione, crearemos un test para el filtrado por fecha.

- **Test:**
  - Llamar a `get_recenttracks(from_date=MI_TIMESTAMP)`.
  - Hacer un `assert` de que `_make_request` es llamado no solo con el `method` correcto, sino también con el parámetro `from` y su valor.
- **Implementación:**
  - Modificar la firma de `get_recenttracks` para que acepte un argumento opcional `from_date`.
  - Si `from_date` se proporciona, pasarlo como un `kwarg` a `_make_request`.

### Paso 3.3: Gestionar la paginación

Este es el paso más complejo y el que dará la funcionalidad completa.

- **Test:**
  - Configurar el mock de `_make_request` para que se comporte de forma dinámica. Por ejemplo, usando `side_effect`.
  - La primera vez que se llame, devolverá la página 1 y `"totalPages": "2"`.
  - La segunda vez, devolverá la página 2 y `"totalPages": "2"`.
  - Hacer un `assert` de que `_make_request` fue llamado **dos veces**, la segunda vez con el parámetro `page=2`.
  - Hacer un `assert` de que la lista final devuelta por `get_recenttracks` contiene las canciones de **ambas páginas`.
- **Implementación:**
  - `get_recenttracks` llamará a `_make_request` una primera vez.
  - Extraerá el total de páginas de los metadatos `["@attr"]["totalPages"]`.
  - Hará un bucle desde la página 2 hasta la última página, llamando a `_make_request` en cada iteración con el parámetro `page` correspondiente.
  - Acumulará los resultados de la lista `["track"]` de cada página en una única lista final.
  - Devolverá la lista completa.

---

## 3. Implementación Incremental de Funcionalidades (Actualización)

Las funcionalidades originalmente descritas en la sección "3. Próximos Pasos (Hoja de Ruta)" han sido implementadas y probadas. A continuación, se detalla el trabajo realizado y los casos de borde manejados.

### Paso 3.1: Gestionar la Paginación (Hoja de Ruta: Pasos 3.1 y 3.3 Completados)

La primera gran funcionalidad implementada fue asegurar que el cliente pudiera obtener **todos** los scrobbles, no solo los de la primera página.

- **Tests**:
  - Se crearon tests para ambos escenarios: una respuesta con una sola página (`test_get_recenttracks_returns_list_of_tracks_when_totalpages_is_one`) y una con múltiples páginas (`test_get_recenttracks_returnslist_of_tracks_when_totalpages_is_more_than_one`).
  - Para simular las respuestas de la API, se crearon ficheros JSON de prueba (`test_rt_1page.json`, `test_rt_2_pages_1.json`, etc.), con la estructura adecuada para simular las respuestas de la API.
  - El mock de `_make_request` se configuró con `side_effect` para simular las llamadas secuenciales a las diferentes páginas.
- **Implementación**:
  - `get_recenttracks` se modificó para leer primero el metadato `totalPages` de la respuesta.
  - Se implementó un bucle que itera desde la página 1 hasta `totalPages`, llamando a `_make_request` con el parámetro `page` en cada iteración.
  - Los resultados (`["recenttracks"]["track"]`) de cada página se acumulan en una lista única que se devuelve al final.

### Paso 3.2: Manejo de Casos Borde (Nuevas Funcionalidades)

Durante el desarrollo, se identificaron y manejaron dos casos borde importantes que no estaban explícitamente detallados en el plan inicial.

#### Caso 1: No hay scrobbles nuevos

- **Test**: Se creó `test_total_pages_attribute_is_zero_raises_error` para el caso en que la API devuelve `totalPages: "0"`.
- **Implementación**: Se añadió una comprobación al inicio de `get_recenttracks` que lanza un `ValueError` si `totalPages` es "0", evitando trabajo innecesario y comunicando el estado claramente.

#### Caso 2: Canción en reproducción ("Now Playing")

Se descubrió que si una canción se está reproduciendo, aparece como el primer elemento en la lista de `track` con un metadato `{"@attr": {"nowplaying": "true"}}`. Este scrobble no está finalizado y, por lo tanto, no debe ser ingestado.

- **Proceso TDD**:
  1.  **Descomposición**: El problema se dividió en dos métodos privados: `_check_first_element_tracks_list` para identificar el track "now playing" y `_drop_first_element_if_attr_in_keys` para eliminarlo de la lista.
  2.  **Tests Unitarios y de Interacción**: Se crearon tests para verificar cada método por separado (`test_check_first_element_list`, `test_drops_first_element_if_attr_in_keys`) y para asegurar que se llamaban correctamente entre sí (`test_drops_first_element_if_attr_in_keys_calls_check_first_element_list`).
  3.  **Test de Integración**: Finalmente, se añadieron tests a nivel de `get_recenttracks` (`test_get_recenttracks_calls_drops_first_element...` y `test_get_recenttracks_drops_first_element_if_in_list_when_it_has_attr_in_keys`) para garantizar que la lógica completa funcionaba como un todo, incluyendo la correcta configuración de los mocks.

---

## 4. Siguiente Paso

Con la funcionalidad principal de paginación y el manejo de casos borde ya implementados y probados, el siguiente objetivo es añadir la capacidad de filtrar los resultados por fecha, tal como se describía originalmente en el "Paso 3.2" de la hoja de ruta.

### Implementar el parámetro `from`

- **Test:**
  - Llamar a `get_recenttracks(from_date=MI_TIMESTAMP)`.
  - Hacer un `assert` de que `_make_request` es llamado no solo con el `method` correcto, sino también con un `kwarg` que contenga el parámetro `from` y su valor en formato timestamp.
- **Implementación:**
  - Modificar la firma de `get_recenttracks` para que acepte un argumento opcional `from_date`.
  - Si `from_date` se proporciona, pasarlo como un `kwarg` a `_make_request`.

---

## 5. Implementación de Parámetros Adicionales: `limit`, `to` y `extended`

Después de finalizar la gestión de paginación y los casos borde básicos, se procedió a enriquecer la funcionalidad de `get_recenttracks` incorporando parámetros adicionales de la API de Last.fm, con el objetivo de hacer el cliente más flexible y eficiente.

### Parámetro `extended`

- **Objetivo**: Obtener información más detallada de cada "track" en la respuesta de la API.
- **Implementación**: Se añadió la clave `'extended': '1'` directamente al diccionario `self.params` en el método `__init__` de `LastfmClient`. Esto asegura que todas las llamadas a la API de "recent tracks" incluyan este parámetro por defecto.
- **Tests**: Los tests que validan los parámetros de la petición (`test_make_requests_api_gets_called_with_correct_params` y `test_make_request_acept_new_parameters`) fueron actualizados para esperar la presencia de este nuevo parámetro.

### Parámetros `limit` y `to` (o `to_uts`)

- **Objetivo**: Permitir controlar el número de tracks por página (`limit`) y especificar una fecha de fin (timestamp UTS) para la búsqueda de tracks (`to_uts`), complementando la funcionalidad de `from_uts`.
- **Implementación**:
    - Se modificó la firma del método `get_recenttracks` para aceptar `limit` (con un valor por defecto de 200) y `to_uts` (con valor por defecto `None`), además de `from_uts`.
    - En las llamadas internas a `_make_request`, el parámetro `limit` se pasó directamente.
    - Para los parámetros `from_uts` y `to_uts`, se utilizó el desempaquetado de diccionario (`**{"from": from_uts, "to": to_uts}`) para manejar las claves que son palabras reservadas en Python, asegurando que se transmitieran correctamente a la API. Esta lógica se aplicó tanto en la llamada inicial para obtener `totalPages` como en el bucle de paginación.
- **Tests**:
    - El test `test_get_recenttracks_calls_make_request_with_valid_params` fue actualizado para verificar que `get_recenttracks` llama a `_make_request` con los valores por defecto de `limit`, `from_uts` y `to_uts`.
    - Los tests `test_make_request_acept_new_parameters` y `test_make_requests_works_in_get_recenttracks_with_new_parameters` fueron actualizados (y renombrados para mayor claridad) para validar que todos los nuevos parámetros (`limit`, `from_uts`, `to_uts`) se pasan y manejan correctamente a lo largo de la cadena de llamadas (`get_recenttracks` -> `_make_request` -> `requests.get`).