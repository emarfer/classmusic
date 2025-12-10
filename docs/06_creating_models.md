# 06 - Creando el Modelo de Datos: Scrobble

Después de finalizar la implementación de un cliente de API robusto (`LastfmClient`), el siguiente paso lógico en nuestro proceso ETL (Extract, Transform, Load) es la fase de **Transformación**. El primer paso de esta fase es definir un "molde" o "plantilla" para nuestros datos limpios.

## 1. Definiendo la Responsabilidad del Modelo

Nuestra primera gran decisión de diseño fue determinar la responsabilidad de nuestras clases de modelo. Se planteó la pregunta: ¿la clase debe saber cómo extraerse a sí misma del JSON de la API, o debe ser simplemente una definición de datos limpia y agnóstica de su origen?

Siguiendo el principio de **Separación de Responsabilidades**, decidimos que la segunda opción era la correcta.

*   **`LastfmClient`**: Se encarga de la **Extracción**. Su única misión es hablar con la API y traer los datos en bruto.
*   **Clases de Modelo (p. ej., `Scrobble`)**: Definen la **estructura de los datos limpios** dentro de nuestra aplicación. No saben nada sobre la API de lastfm ni sobre la base de datos.
*   **Transformador (un paso futuro)**: Será una pieza de código (probablemente en `src/etl/`) que se encargará de "traducir" el JSON en bruto del cliente a nuestros objetos de modelo limpios.

## 2. De `Track` a `Scrobble`: La Importancia del Lenguaje del Dominio

Inicialmente, pensamos en nombrar nuestro modelo principal `Track`. Sin embargo, gracias a una observación clave, nos dimos cuenta de que lo que obtenemos de la API `user.getrecenttracks` no es simplemente una lista de temas, sino una lista de **registros de escucha**, que en el lenguaje de lastfm se denominan **"scrobbles"**.

Decidimos cambiar el nombre del modelo a `Scrobble` por varias razones de peso:
1.  **Precisión Semántica**: Es el término correcto para un evento de escucha único.
2.  **Alineación con la Base de Datos**: El nombre se alinea con la tabla de destino en MySQL, `scrobbling`.
3.  **Refleja la Clave Primaria**: El identificador único de cada registro es el timestamp (`uts`), no el ID del tema. Un mismo tema puede tener muchos scrobbles, pero cada scrobble es único.

Este cambio hace que el código sea más expresivo y fácil de entender para cualquiera que conozca el dominio del problema.

## 3. El Diseño Final del Modelo `Scrobble`

Con el nombre y las responsabilidades claras, diseñamos el modelo `Scrobble` basándonos directamente en las columnas de la tabla `scrobbling`. Utilizamos la librería `pydantic` para obtener validación de datos automática.

Se tomó una decisión de diseño importante con respecto a los campos `mbid`: tras confirmar que la API de lastfm siempre devuelve una cadena de texto (aunque sea vacía, `""`) para estos campos, se definieron como `str` y no como opcionales.

El modelo final en `src/models/scrobble.py` quedó así:

```python
from pydantic import BaseModel

class Scrobble(BaseModel):
    uts: int
    artist: str
    artist_mbid: str
    album: str
    album_mbid: str
    title: str
    track_mbid: str
```

## 4. Probando el Modelo con TDD

Para asegurar que nuestro modelo `Scrobble` se comportaba como esperábamos, creamos una suite de tests en `tests/models/test_scrobble.py`. Los tests se centraron en verificar las capacidades de validación de Pydantic, cubriendo los siguientes escenarios:
1.  **Creación exitosa**: Se probó que el modelo se instancia correctamente con un diccionario de datos válidos.
2.  **Aceptación de `mbid` vacíos**: Se verificó que los campos `mbid` aceptan una cadena de texto vacía sin problemas.
3.  **Fallo por campos ausentes**: Se comprobó que Pydantic lanza una `ValidationError` si falta un campo obligatorio. Se utilizó un bucle para probar la ausencia de cada campo de forma individual.
4.  **Fallo por tipos incorrectos**: Se probó que se lanza una `ValidationError` si un campo recibe un tipo de dato que no se puede convertir (p. ej., un texto no numérico para `uts`). Para esto, se usó el decorador `@pytest.mark.parametrize` para probar varios valores inválidos de forma idiomática.
5.  **Coerción de tipos**: Se verificó que Pydantic convierte automáticamente un `uts` en formato de string numérico a `int`.

Tras una ronda de refactorización para limpiar los `imports` y hacer los tests más concisos (usando `model_dump()` y `@pytest.mark.parametrize`), obtuvimos una suite de tests robusta que nos da confianza en nuestro modelo de datos.

## 5. Conclusión y Próximos Pasos

Hemos definido y validado con éxito nuestro primer modelo de dominio, `Scrobble`. Esto completa el primer y más importante paso de la fase de **Transformación** de nuestro ETL.

El siguiente paso lógico será crear el **Transformador**: una función o clase que tome la lista de diccionarios JSON en bruto de `LastfmClient` y la convierta en una lista de objetos `Scrobble` limpios y validados.