# Diseño de la Clase `LastfmClient`

Antes de empezar a escribir el código para el cliente de Last.fm, hemos definido su estructura basándonos en los siguientes pasos, que reflejan un diseño común y robusto para clientes de API. Esto nos permite seguir el ciclo TDD de forma efectiva, probando cada parte de la funcionalidad a medida que la construimos.

## 1. El Constructor (`__init__`)

*   **Responsabilidad:** Inicializar la instancia del cliente.
*   **Detalles:** Recibirá una instancia de nuestra clase `Config`. Su principal tarea será extraer y almacenar la clave de la API (`api_key`) de Last.fm de este objeto `Config` en un atributo interno (por ejemplo, `self.api_key`). También es el lugar ideal para definir la URL base de la API de Last.fm (`self.base_url`).
*   **Propósito en el TDD:** El primer test que escribamos verificará que el constructor funciona correctamente, es decir, que la `api_key` se guarda adecuadamente al instanciar el cliente.

## 2. Atributos para la URL Base

*   **Responsabilidad:** Mantener la URL raíz de la API de Last.fm.
*   **Detalles:** Un atributo como `self.base_url = 'http://ws.audioscrobbler.com/2.0/'` asegurará que todas las llamadas a la API usen la misma base, facilitando su mantenimiento.

## 3. Métodos Públicos para Endpoints Específicos

*   **Responsabilidad:** Exponer las funcionalidades específicas de la API de Last.fm que queremos utilizar.
*   **Detalles:** Por cada método de la API de Last.fm (ej. `user.getRecentTracks`, `artist.getInfo`), crearemos un método público correspondiente en nuestra clase (`def get_recent_tracks(self, user, limit=10):`). Estos métodos se encargarán de:
    *   Tomar los parámetros específicos que necesita ese endpoint (ej. nombre de usuario, límite de resultados).
    *   Delegar la llamada HTTP real a un método privado (ver siguiente punto).

## 4. Un Método Privado "Ayudante" (`_make_request`)

*   **Responsabilidad:** Centralizar la lógica de las llamadas HTTP a la API.
*   **Detalles:** Este será un método interno (convención: empieza con guion bajo, ej. `_make_request(self, method, params)`). Su función será manejar los detalles repetitivos de cualquier llamada a la API de Last.fm:
    *   Construir la URL completa del endpoint, combinando `self.base_url` con el método y los parámetros.
    *   Añadir automáticamente parámetros comunes como la `api_key` y el formato de respuesta (`json`).
    *   Utilizar una librería HTTP (como `requests`) para realizar la petición.
    *   Manejar posibles errores de red o de la API (códigos de estado HTTP).
    *   Parsear la respuesta (típicamente JSON) y devolver los datos.
*   **Beneficio:** Evita la duplicación de código en los métodos públicos y facilita la gestión de errores y el logging de todas las llamadas a la API desde un único lugar.

---

Esta estructura nos permite un desarrollo modular, fácil de probar y mantener, siguiendo los principios de la separación de responsabilidades. Cada parte de la clase `LastfmClient` tendrá un propósito claro y definido.

## Implementación y Testeo del Constructor de `LastfmClient` (TDD)

Una vez definido el diseño, nos enfocamos en implementar y testear el constructor de la clase `LastfmClient`, siguiendo el ciclo TDD.

### 1. El Constructor (`__init__`) en `src/clients/lastfm_client.py`

El constructor de `LastfmClient` tiene la responsabilidad de inicializarse con las credenciales de la API y la URL base del servicio.

```python
# En src/clients/lastfm_client.py
from src.config.config import Config

class LastfmClient:
    def __init__(self, config: Config):
        # Obtener las claves usando el objeto Config recibido
        self.LASTFM_KEY = config.get_credentials("LASTFM_KEY")
        self.LASTFM_SECRET = config.get_credentials("LASTFM_SECRET")
        # Establecer la URI base de la API
        self.uri = "http://ws.audioscrobbler.com/2.0/"
```

*   **Puntos Claves:**
    *   **Inyección de Dependencias:** El constructor recibe una instancia de `Config` (indicado con `config: Config`), lo que significa que el `LastfmClient` no se preocupa de cómo se obtiene la configuración, solo de usarla.
    *   **Obtención de Credenciales:** Utiliza el método `get_credentials()` del objeto `Config` para extraer `LASTFM_KEY` y `LASTFM_SECRET`.
    *   **URL Base:** Se define directamente la `uri` base de la API.

### 2. Testeo del Constructor en `tests/clients/test_lastfm_client.py`

Para testear este constructor, necesitamos un `mock_config` que simule el comportamiento de nuestra clase `Config`, especialmente su método `get_credentials()`.

```python
# En tests/clients/test_lastfm_client.py
from unittest.mock import MagicMock
import pytest

from src.clients.lastfm_client import LastfmClient
from src.config.config import Config # Importamos Config para la especificación del mock


class TestLastfmClient():
    @pytest.fixture
    def mock_config(self) -> MagicMock:
        mock_config = MagicMock(spec=Config)

        # Usamos una función side_effect para que get_credentials devuelva diferentes valores
        # según la clave que se le pida.
        def get_credentials_side_effect(key_name):            
            keys_dict = {
                "LASTFM_KEY":"fake_lastfam_key",
                "LASTFM_SECRET":"fake_lastfm_secret"
            }
            return keys_dict[key_name]
        
        mock_config.get_credentials.side_effect = get_credentials_side_effect
        return mock_config
    
    def test_lastfm_client_gets_credentials(self, mock_config):        
        client = LastfmClient(mock_config)
        
        # Asertamos que el cliente ha almacenado las claves correctas
        assert client.LASTFM_KEY == "fake_lastfam_key"
        assert client.LASTFM_SECRET == "fake_lastfm_secret"
        
    def test_lastfm_client_has_uri(self, mock_config): # Corregido el typo en el nombre
        client = LastfmClient(mock_config)
        
        # Asertamos que la URI existe y tiene el valor correcto
        assert client.uri == "http://ws.audioscrobbler.com/2.0/"
```

*   **Puntos Claves del Test:**
    *   **Fixture `mock_config`:**
        *   Se crea un `MagicMock(spec=Config)` para asegurar que el mock se comporta como una instancia de `Config`.
        *   Se utiliza una función `side_effect_credentials` para el método `get_credentials` del mock. Esta función devuelve valores diferentes (`"fake_lastfam_key"`, `"fake_lastfm_secret"`) basándose en el `key_name` que se le pasa, simulando de forma realista el comportamiento de `Config.get_credentials()`.
    *   **`test_lastfm_client_gets_credentials`:** Este test verifica que el `LastfmClient` extrae y almacena correctamente ambas claves (`LASTFM_KEY` y `LASTFM_SECRET`) del objeto `Config` simulado.
    *   **`test_lastfm_client_has_uri`:** Este test, además de verificar que el atributo `uri` existe, comprueba que tiene el valor exacto esperado (`"http://ws.audioscrobbler.com/2.0/"`), protegiéndonos de cambios accidentales. (Se corrigió el pequeño typo en el nombre de la función `test_lastgm_client_has_uri` a `test_lastfm_client_has_uri`).

### Lecciones Aprendidas

1.  **Mocking Avanzado (`side_effect`):** Aprendimos a usar `side_effect` con una función para simular comportamientos de mock más complejos, donde el valor de retorno depende de los argumentos de entrada. Esto es crucial para testear interacciones con dependencias que tienen lógica condicional.
2.  **Testeo Completo del Constructor:** Aseguramos que el constructor de `LastfmClient` no solo se inicializa, sino que lo hace con los datos correctos provenientes de su dependencia `Config`.
3.  **Claridad en las Asertos:** Preferir aserciones que comprueben valores exactos en lugar de solo su existencia (ej. `assert client.uri == "..."` vs `assert client.uri is not None`).

---
## Testeando el Método `_make_request`

Una vez probado el constructor, el siguiente paso es probar los métodos de la clase. Empezamos por el método privado `_make_request`, que será el corazón de todas las llamadas a la API.

### 1. Simplificaciones y Preparación (`setup_method`)

Primero, decidimos simplificar el alcance: como solo vamos a ingestar datos de un usuario, el nombre de usuario puede estar fijo en el cliente, y la `LASTFM_SECRET` no es necesaria para las llamadas de solo lectura.

Para evitar repetir la creación del `LastfmClient` en cada test, usamos `setup_method`, una función de `pytest` que se ejecuta antes de cada test dentro de una clase:

```python
# En tests/clients/test_lastfm_client.py
class TestLastfmClient():    
    def setup_method(self, method):
        # Creamos un mock simple para Config, ya que solo necesitamos una clave
        mock_config = MagicMock(spec=Config)
        mock_config.get_credentials.return_value = "fake_lastfam_key"
        # Creamos la instancia del cliente y la guardamos en self para que esté disponible en los tests
        self.client = LastfmClient(mock_config)
```

### 2. Test 1: Verificar que se Llama a `requests.get`

Nuestro primer objetivo fue asegurar que `_make_request` efectivamente intentaba hacer una llamada de red, pero sin hacerla de verdad.

*   **Herramienta:** Usamos `@patch` de `unittest.mock` como un decorador para reemplazar `requests.get` por un `MagicMock`.
*   **Test (Rojo -> Verde):**
    1.  **Test**: Creamos `test_make_requests_api_gets_called` y usamos `mock_requests_get.assert_called_once()` para verificar que el mock fue llamado.
    2.  **Fallo Inicial (Rojo)**: El test fallaba porque `_make_request` estaba vacío.
    3.  **Implementación (Verde)**: Añadimos la implementación mínima en `_make_request` para que llamara a `requests.get`.

### 3. Test 2: Refactorizar para Aceptar Argumentos Dinámicos

El siguiente paso fue hacer `_make_request` más útil, capaz de construir la URL con parámetros.

*   **Test (Rojo -> Verde):**
    1.  **Test**: Creamos `test_make_requests_api_gets_called_with_correct_params`. Este test llama a `_make_request` con un método y parámetros opcionales (`_make_request("test_method", limit=0)`). La aserción clave es `mock_requests_get.assert_called_once_with(url, expected_params)`, que comprueba no solo *si* se llamó, sino *con qué argumentos exactos*.
    2.  **Fallo Inicial (Rojo)**: El test fallaba porque `_make_request` no aceptaba los nuevos argumentos (`method`, `**kwargs`).
    3.  **Implementación (Verde)**: Refactorizamos `_make_request` para que aceptara `method` y `**kwargs`, construyera el diccionario de parámetros y llamara a `requests.get`.

### 4. El Bug Sutil: Referencia vs. Copia

Durante la refactorización, nos encontramos con un bug común pero importante. El código `params = self.params` creaba una **referencia**, no una copia, por lo que cada llamada a `_make_request` modificaba el diccionario base de la clase.

*   **La Solución:** Cambiamos la línea a `params = self.params.copy()` para asegurar que cada llamada trabaje con su propio diccionario de parámetros, aislando las llamadas entre sí.

**Código Final del Método `_make_request`:**
```python
# En src/clients/lastfm_client.py
def _make_request(self, method:str, **kwargs):
    # Creamos una copia para no modificar el diccionario base de la instancia
    params = self.params.copy()
    # Añadimos el método de la API
    params.update({"method":method})
    # Añadimos cualquier parámetro opcional
    params.update(kwargs)
    # Hacemos la llamada
    return requests.get(self.uri, params)
```

### Más Lecciones Aprendidas

4.  **Mocking de Librerías Externas (`@patch`)**: Aprendimos a usar `@patch` para aislar nuestro código de dependencias externas como `requests`, haciendo los tests rápidos y fiables.
5.  **Aserciones Específicas**: `assert_called_once_with()` es mucho más potente que `assert_called_once()` porque nos permite verificar que la interacción con el mock se hizo con los datos exactos que esperábamos.
6.  **Peligros de los Objetos Mutables**: Descubrimos la importancia de usar `.copy()` con diccionarios o listas que son atributos de una clase para evitar que el estado de una llamada "se filtre" a la siguiente.
7.  **Preparación de Tests Limpios (`setup_method`)**: Vimos cómo usar `setup_method` para reducir código repetido y hacer nuestros tests más legibles.