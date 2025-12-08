# El Dilema de la Depuración: Cómo Configurar un Entorno de Debug Profesional

Este documento resume el diálogo y el proceso de aprendizaje que seguimos para resolver un problema aparentemente simple pero fundamental: cómo depurar un fichero de Python que es parte de un proyecto estructurado con una carpeta `src`.

## 1. El Problema Inicial: `ModuleNotFoundError`

Todo comenzó al intentar depurar el fichero `src/clients/lastfm_client.py` usando la configuración por defecto de "Python: Current File" en VS Code.

El intento fallaba inmediatamente con el siguiente error:
```
ModuleNotFoundError: No module named 'src'
```
La línea que causaba el error era una importación al principio del fichero: `from src.config.config import Config`.

### ¿Por qué ocurría esto?

La raíz del problema es cómo Python maneja las rutas de importación (`PYTHONPATH`):

*   Cuando ejecutas un script como `python src/clients/lastfm_client.py`, Python establece que el directorio de trabajo para las importaciones es la carpeta del script, es decir, `src/clients/`.
*   Desde dentro de esa carpeta, Python intenta resolver `from src.config...`. Busca una carpeta `src` **dentro** de `src/clients/`, no la encuentra, y lanza el `ModuleNotFoundError`.
*   La razón por la que los tests (`pytest`) funcionaban bien es porque `pytest` se ejecuta desde la raíz del proyecto, por lo que sí puede "ver" la carpeta `src` y resolver las importaciones correctamente.

## 2. La Búsqueda de una Solución: Un Viaje por Varias Propuestas

Nuestra conversación exploró varias soluciones, cada una con sus pros y sus contras, revelando poco a poco la solución más profesional.

### Propuesta 1: El Script "Runner" Externo

La primera idea fue crear un script `debug_runner.py` en la raíz del proyecto. Este script actuaría como el "arrancador" o punto de entrada.

*   **Ventaja**: Al estar en la raíz, podía importar módulos de `src` sin problemas de rutas.
*   **Duda planteada**: Parecía una solución poco elegante y engorrosa. La pregunta clave era: *"¿Realmente necesito un fichero extra solo para depurar?"*

### Propuesta 2: El Bloque `if __name__ == "__main__"`

La siguiente idea fue hacer que el propio módulo `lastfm_client.py` fuera ejecutable añadiendo el bloque `if __name__ == "__main__":` al final.

*   **Ventaja**: No requería ficheros extra. Es una práctica común en Python para ficheros que pueden ser tanto librerías como scripts.
*   **Duda planteada**: Esto no resolvía la necesidad de tener un punto de entrada central para el proyecto que pudiera orquestar la ejecución de varios módulos en secuencia, como en un proceso ETL.

### El "Momento Eureka" y la Duda Clave

La duda más importante surgió aquí: *"¿Cómo depuro OTROS módulos como `config.py`? ¿Necesito una configuración de `launch.json` para cada fichero?"*

Esta pregunta reveló el principio fundamental que no habíamos aclarado:

> **Principio Clave:** No depuramos "ficheros", depuramos un **"proceso"**. El objetivo es iniciar un único proceso principal. Una vez el depurador de VS Code se "engancha" a ese proceso, podemos poner breakpoints en **CUALQUIER** parte del código que ese proceso utilice.

## 3. La Solución Definitiva: Combinando Estructura y Herramientas

La solución final y más robusta combinó lo mejor de todas las ideas y utilizó herramientas estándar del ecosistema de Python.

### Paso 1: Hacer el Proyecto "Autoconsciente" con `pyproject.toml`

Para que nuestro entorno virtual supiera que nuestra carpeta `src` era un paquete instalable, creamos un fichero `pyproject.toml` en la raíz. Este fichero es el estándar moderno para definir proyectos de Python.

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "classmusic"
version = "0.1.0"

[tool.setuptools.packages.find]
where = ["src"]
```

### Paso 2: El "Modo Editable" con `pip`

Con `pyproject.toml` creado, ejecutamos el siguiente comando en la terminal (con el entorno virtual activado):

```bash
pip install -e .
```

*   `pip install`: El comando estándar para instalar paquetes.
*   `-e`: La opción para instalar en modo "editable". Esto no copia el código, sino que crea un enlace simbólico. Cualquier cambio en `src` se refleja instantáneamente en el entorno.
*   `.`: Significa "el proyecto que se encuentra en el directorio actual".

Este comando es el pegamento mágico que registra nuestro proyecto `classmusic` en el entorno virtual, solucionando los `ModuleNotFoundError` de forma permanente.

### Paso 3: El Punto de Entrada Oficial (`__main__.py`)

Acogiendo la idea de un orquestador central, creamos un fichero `__main__.py` en la raíz. Este fichero actúa como el punto de entrada principal y limpio para toda la aplicación.

### Paso 4: Una Única Configuración de Depuración

Finalmente, añadimos una única configuración a `.vscode/launch.json` que simplemente ejecuta nuestro `__main__.py`.

```json
{
    "name": "Python: Debug Main Process",
    "type": "python",
    "request": "launch",
    "program": "${workspaceFolder}/__main__.py",
    "console": "integratedTerminal",
    "justMyCode": true
}
```

## 4. Conclusión: El Flujo de Trabajo Final

Después de este proceso, el flujo de trabajo para depurar cualquier parte del código es ahora increíblemente simple y potente:

1.  Abres cualquier fichero del proyecto (`config.py`, `lastfm_client.py`, etc.).
2.  Pones un breakpoint donde necesites investigar.
3.  Lanzas la única configuración de depuración que necesitas: **"Python: Debug Main Process"**.

El depurador arrancará el proceso principal, que a su vez llamará al resto de tu código, y se detendrá en el breakpoint que hayas puesto, dándote control total. Este es el método estándar, robusto y escalable para la depuración en proyectos de Python bien estructurados.
