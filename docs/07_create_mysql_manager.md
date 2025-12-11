# 07 - Creando el Gestor de Base de Datos: MysqlManager

Una vez completada la fase de **Extracción** (con `LastfmClient`) y la primera parte de la **Transformación** (con el modelo `Scrobble`), el siguiente paso en nuestro plan de ETL es preparar la fase de **Carga (Load)**. Para ello, necesitamos un componente que gestione la comunicación con nuestra base de datos MySQL.

## 1. Diseño y Ubicación: `MysqlManager` en `src/database`

Siguiendo nuestro principio de **Separación de Responsabilidades**, tomamos varias decisiones de diseño clave:

1.  **Ubicación**: Decidimos crear el gestor en la carpeta `src/database/` en lugar de `src/clients/`. Reservamos `clients` para APIs externas (HTTP) y `database` para toda la lógica de persistencia, manteniendo una distinción clara.
2.  **Nombre**: Se eligió el nombre `mysql_manager.py` en lugar de un genérico `database_manager.py`. Esta decisión, sugerida por ti, nos da la flexibilidad de añadir otros gestores para diferentes tipos de bases de datos en el futuro (ej. `sqlite_manager.py`) sin crear conflictos.
3.  **Responsabilidad**: El `MysqlManager` será el único componente en toda la aplicación que sabrá "hablar" con MySQL. Cualquier otro proceso (como nuestras futuras ETLs) simplemente le dará órdenes, sin necesidad de conocer los detalles de la conexión.

## 2. TDD Paso a Paso: Construyendo el `MysqlManager`

Construimos la clase `MysqlManager` de forma incremental, siguiendo un estricto ciclo de TDD (Rojo-Verde-Refactorizar).

### Paso 2.1: Obtención de Credenciales (`__init__`)

El primer paso fue asegurarnos de que el `MysqlManager` pudiera obtener todas las credenciales necesarias del objeto `Config`.

1.  **Test Inicial**: Creamos un test que verificaba la obtención de una sola credencial (`MYSQL_PASSWORD`).
2.  **Mocking con `side_effect`**: Para probar la obtención de múltiples credenciales, modificamos el mock de `Config` en nuestro `setup_method` para usar `side_effect`. Esto nos permitió simular el comportamiento de `get_credentials` para diferentes claves.
3.  **Implementación**: Escribimos el código en el `__init__` de `MysqlManager` para que leyera todas las credenciales (`HOST`, `PORT`, `USER`, `PASSWORD`, `DATABASE`) y las almacenara como atributos de la instancia.

### Paso 2.2: Creación de la URI de Conexión (`_create_mysql_uri`)

Decidimos separar la lógica de construir la URI de conexión en su propio método privado para mejorar la testabilidad y la claridad.

1.  **Decisión de Diseño**: Discutimos si el nombre de la base de datos (`DATABASE`) debía ser parte de la configuración o un parámetro. Decidimos mantenerlo en la configuración para simplificar, ya que nuestro proyecto solo apunta a una base de datos.
2.  **Test**: Creamos `test_create_mysql_uri_creates_valid_uri`, donde definimos una URI "hardcodeada" que esperábamos como resultado. Esto asegura que el test verifica el resultado final exacto, no la lógica de construcción.
3.  **Implementación**: Implementamos el método `_create_mysql_uri` usando una f-string para construir la URI de conexión de SQLAlchemy con el dialecto `pymysql`.

### Paso 2.3: Creación del Motor de SQLAlchemy (`create_mysql_engine`)

El objetivo final de esta fase era que el gestor pudiera crear un "engine" de SQLAlchemy, que es el punto de entrada para toda la comunicación con la base de datos.

1.  **Lección de Mocking (El "Gotcha")**: Durante el testeo, nos encontramos con un problema común. Un test inicial que solo mockeaba `_create_mysql_uri` fallaba porque la llamada a `sqlalchemy.create_engine` se hacía de verdad, pero recibía un objeto `MagicMock` en lugar de una string, causando un error.
2.  **La Solución**: La lección fue que **un test unitario debe mockear todas las dependencias externas** de la función que se está probando. Arreglamos el test y creamos el definitivo mockeando tanto `_create_mysql_uri` como `sqlalchemy.create_engine`.
3.  **Test Final**: El test final (`test_create_mysql_engine_creates_sqlalchemy_engine`) verificó tres cosas:
    *   Que `_create_mysql_uri` es llamado.
    *   Que `sqlalchemy.create_engine` es llamado con la URI correcta.
    *   Que el método `create_mysql_engine` devuelve correctamente el objeto "engine" que el mock de `sqlalchemy.create_engine` le proporciona.

## 3. Conclusión

Con estos pasos, ahora tenemos una clase `MysqlManager` completamente probada. Es capaz de inicializarse con las credenciales correctas, construir la URI de conexión y preparar el motor de SQLAlchemy. Esto nos proporciona una base sólida y reutilizable sobre la cual construiremos los métodos para insertar y consultar datos en la fase de **Carga (Load)** de nuestro ETL.