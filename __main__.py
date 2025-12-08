# __main__.py
from src.config.config import Config
from src.clients.lastfm_client import LastfmClient
import os  # Necesario para construir la ruta al .env


def run():
    """
    Punto de entrada principal para ejecutar el proceso.
    """
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    config = Config(dotenv_path=dotenv_path)
    client = LastfmClient(config=config)
    tracks = client.get_recenttracks()

    print(f"Proceso finalizado. Se encontraron {len(tracks)} tracks.")


# --- Punto de arranque ---
if __name__ == "__main__":
    run()
