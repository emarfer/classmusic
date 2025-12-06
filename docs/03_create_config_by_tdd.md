# Creando la Configuración con TDD: Paso a Paso

En este documento, vamos a desglosar el proceso que seguimos para crear y probar nuestra clase `Config` usando la metodología de **Desarrollo Guiado por Tests (TDD)**. El objetivo era simple: tener una clase capaz de cargar secretos (como una API key) desde un fichero `.env`.

## 1. El Principio Clave de TDD: Rojo, Verde, Refactorizar

TDD se basa en un ciclo corto y repetitivo:
1.  **Rojo**: Escribir un test que falle porque la funcionalidad que se quiere implementar aún no existe.
2.  **Verde**: Escribir el código de producción **mínimo** posible para que ese test pase.
3.  **Refactorizar**: Limpiar y mejorar tanto el código de producción como el del test, sin cambiar su comportamiento.

## 2. El Primer Intento: Un Test que No Fallaba

Nuestro primer test usaba `MagicMock`, una herramienta de `unittest.mock`.

```python
# Primer intento de test (incorrecto para este caso)
def test_read_credentials(self, mock_config):
    Config(mock_config).read_credentials()
    assert mock_config.LASTFM_KEY == "fake_key"
```

**Problema**: Este test pasaba siempre (era "verde" desde el principio), incluso con el método `read_credentials` vacío. `MagicMock` es tan flexible que el `assert` simplemente comprobaba un valor que el propio test había definido en el mock. No estaba probando lo que queríamos: **que la clase leyera un fichero real**.

## 3. El Segundo Intento: Un Test Realista que Falla (¡Bien!)

Para probar de verdad la lectura de un fichero, necesitábamos crear un entorno de prueba controlado y aislado. Aquí es donde entraron en juego dos herramientas increíblemente útiles de `pytest`: `tmp_path` y `monkeypatch`.

### ¿Qué es `tmp_path` y por qué lo usamos?

`tmp_path` es un *fixture* de `pytest` que crea un **directorio temporal único** para cada ejecución de un test.

*   **Propósito**: Aislar el test. Nos aseguramos de que nuestro test no lee accidentalmente un fichero `.env` real de nuestro proyecto ni deja ficheros de prueba tirados por ahí. Nos da un "laboratorio" limpio y estéril para cada prueba.

```python
# Uso de tmp_path para crear un .env de prueba
fake_env_file = tmp_path / ".env"
fake_env_file.write_text("FAKE_LASTFMKEY=fake_key")
```

### ¿Qué es `monkeypatch` y por qué lo usamos?

`monkeypatch` es otro *fixture* de `pytest` que nos permite **modificar el entorno de ejecución de forma segura** solo durante un test.

*   **Propósito**: Controlar el contexto del test. Lo usamos para dos cosas:
    1.  `monkeypatch.delenv(...)`: Para borrar temporalmente una variable de entorno. Esto nos asegura que el valor que leemos viene de nuestro fichero `.env` de prueba y no de una variable que ya existía en el sistema.
    2.  `monkeypatch.chdir(...)`: Nuestro primer intento para que `dotenv` encontrara el fichero fue cambiar el directorio de trabajo actual al directorio temporal. Aunque no fue la solución final, es un buen ejemplo de cómo `monkeypatch` puede controlar el entorno.

Con estas herramientas, nuestro test quedó así:

```python
# Test Rojo: Falla porque read_credentials() está vacío
def test_read_credentials(self, tmp_path, monkeypatch):
    fake_env_file = tmp_path / ".env"
    fake_env_file.write_text("FAKE_LASTFMKEY=fake_key")
    monkeypatch.delenv("FAKE_LASTFMKEY", raising=False)
    monkeypatch.chdir(tmp_path) # Intento inicial

    Config().read_credentials()
    
    # Falla aquí con KeyError porque la variable no se carga
    assert os.environ["FAKE_LASTFMKEY"] == "fake_key"
```

Este test fallaba con un `KeyError`, lo cual era **perfecto**. Era nuestro "Rojo": una prueba clara de que la funcionalidad no existía.

## 4. El Código Mínimo para el "Verde"

Con el test fallando, escribimos el código más simple posible en `src/config/config.py` para hacerlo pasar:

```python
# En src/config/config.py
from dotenv import load_dotenv

class Config:
    def read_credentials(self):
        load_dotenv()
```

## 5. El Obstáculo y la Refactorización Final

A pesar del cambio, el test seguía fallando. Descubrimos que depender de `monkeypatch.chdir` era frágil. La librería `dotenv` no estaba encontrando nuestro fichero temporal.

Esto nos llevó a la fase de **Refactorizar** y a una lección muy importante sobre escribir código "testable" (fácil de probar): **hacer las dependencias explícitas**.

En lugar de que `read_credentials` "mágicamente" buscara un fichero, lo modificamos para que pudiera recibir la ruta como un argumento.

**Código de producción final:**
```python
# En src/config/config.py
from dotenv import load_dotenv

class Config:
    def read_credentials(self, dotenv_path=None):
        # Le pasamos la ruta explícitamente a load_dotenv
        load_dotenv(dotenv_path=dotenv_path)
```

**Test final (que pasa a "Verde"):**
```python
# En tests/config/test_config.py
def test_read_credentials(self, tmp_path, monkeypatch):
    # Arrange
    fake_env_file = tmp_path / ".env"
    fake_env_file.write_text("FAKE_LASTFMKEY=fake_key")
    monkeypatch.delenv("FAKE_LASTFMKEY", raising=False)

    # Act: Llamamos al método pasándole la ruta de nuestro fichero falso
    Config().read_credentials(dotenv_path=fake_env_file)
    
    # Assert
    assert os.environ["FAKE_LASTFMKEY"] == "fake_key"
```

Con este cambio, el test pasó a **verde**. No dejamos lugar a la ambigüedad: le dijimos a nuestro código exactamente dónde encontrar el fichero que debía leer, haciendo el sistema robusto y predecible.

## 6. Lecciones Aprendidas

1.  **TDD te guía**: El ciclo Rojo-Verde-Refactorizar nos llevó de no tener nada a una solución funcional y probada.
2.  **Los tests deben ser aislados**: `tmp_path` es fundamental para que los tests no interfieran entre sí ni con el entorno real.
3.  **Controla el entorno del test**: `monkeypatch` nos da el poder de asegurar que las condiciones de la prueba son exactamente las que necesitamos.
4.  **El código explícito es mejor que el implícito**: Pasar dependencias (como una ruta de fichero) directamente a una función la hace mucho más fácil de probar y entender que confiar en estados globales (como el directorio de trabajo actual).
