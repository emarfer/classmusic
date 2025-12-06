# Recomeded steps

1. Create git repository.
2. Crate .gitignore
3. Crate virtual environment 
    - since this is a local project and i'm working in WSL and the first envs were created with conda, is best to create the env with pipenv than with uv.
4. Add Baseic Project Files (like README.md)
5. First Commit

# Packages neeeded
- pandas
- numpy
- requests
- pyarrow
- sqlalchemy
- mysqlclient
- pydantic
- python-dotenv
- pytest
- ruff
- black


# Steps taken
1. Created repository in github -> git clone
2. Copied GEMINI.md from another project and modify it a little bit for this one.
3. copied settings.json 
4. add basic folders.


# How to: crear entorno con pipenv.
- creará dos ficheros: Pipfile + Pipfile.lock
   1. `Pipfile`: Aquí se declaran las librerías que necesita tu proyecto (como las que has listado). Es como la "receta" de tu entorno.
   2. `Pipfile.lock`: Este fichero es como una "foto" exacta de las versiones de todas las librerías instaladas. Asegura que si alguien (o tú misma en otro ordenador) instala el entorno, tendrá exactamente las mismas versiones, evitando el clásico "en mi máquina funciona".
- instalar pipenv:
```
pip install pipenv
```
- verificar 3.12: 
```
python3.12 --version
```
```bash
pyenv: python3.12: command not found

The `python3.12' command exists in these Python versions:
  3.12.0

Note: See 'pyenv help global' for tips on allowing both
```
- esto nos dice que python 3.12 está instalado pero no activado. Para que pipenv lo utlice necesitamos indicarle a pyenv que lo utilice
- pyenv versions: nos indica qué versiones de python gestiona pyenv.
- decirle a pyenv que use la version 3.12.0 para este proyecto.
    - desde el directorio del proyecto: pyenv local 3.12.0
    - creará un fichero llamado `.python-version` idicando qué version de python debe usarse aquí.
- Instalar dependencias
    - producción:
    ```bash
    pipenv install pandas numpy requests pyarrow sqlalchemy mysqlclient pydantic python-dotenv
    ```
    - desarrollo (testing, formato):
    ```bash
    pipenv install pytest ruff black --dev
    ```
    (se han creado los archivso Pipefile + Pipefile.lock) 
- Activar entorno:


