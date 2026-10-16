"""Configuración del proyecto: rutas de carpetas y API key."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Carpeta raíz del proyecto (cinetrends/).
# __file__ es este archivo; .parents[2] sube dos carpetas: cinetrends/ -> src/ -> raíz.
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"

TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Lee el archivo .env y carga sus valores como variables de entorno.
load_dotenv(ROOT_DIR / ".env")


def get_api_key():
    """Devuelve la API key de TMDB, o un error claro si no está configurada."""
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key or api_key == "tu_clave_aqui":
        raise RuntimeError("Falta TMDB_API_KEY. Copiá .env.example como .env y poné tu clave.")
    return api_key