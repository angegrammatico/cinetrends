"""Extract: descarga películas de la API de TMDB y las guarda en data/raw/.

Uso (desde la carpeta src/):
    python -m cinetrends.extract --start-year 2023 --end-year 2023 --pages 1
"""
import argparse
import json
import time
from datetime import date

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from cinetrends import config

# Pausa entre llamadas para no saturar la API.
PAUSE_SECONDS = 0.05


def create_session(api_key):
    """Crea una conexión a la API que reintenta sola si algo falla."""
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.params = {"api_key": api_key}
    return session


def get_movie_ids(session, year, pages):
    """Devuelve los ids de las películas más votadas de un año."""
    movie_ids = []
    for page in range(1, pages + 1):
        response = session.get(
            f"{config.TMDB_BASE_URL}/discover/movie",
            params={
                "primary_release_year": year,
                "sort_by": "vote_count.desc",
                "page": page,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        for movie in data["results"]:
            movie_ids.append(movie["id"])
        if page >= data["total_pages"]:
            break
        time.sleep(PAUSE_SECONDS)
    return movie_ids


def get_movie_details(session, movie_id):
    """Devuelve la ficha completa de una película (incluye budget y revenue)."""
    response = session.get(f"{config.TMDB_BASE_URL}/movie/{movie_id}", timeout=30)
    response.raise_for_status()
    return response.json()


def extract_movies(start_year, end_year, pages):
    """Descarga las películas de varios años y las guarda en un archivo JSON."""
    session = create_session(config.get_api_key())

    movie_ids = []
    for year in range(start_year, end_year + 1):
        year_ids = get_movie_ids(session, year, pages)
        print(f"Año {year}: {len(year_ids)} películas encontradas")
        movie_ids.extend(year_ids)

    movie_ids = list(dict.fromkeys(movie_ids))  # quita ids repetidos

    movies = []
    for number, movie_id in enumerate(movie_ids, start=1):
        movies.append(get_movie_details(session, movie_id))
        if number % 100 == 0:
            print(f"Fichas descargadas: {number} de {len(movie_ids)}")
        time.sleep(PAUSE_SECONDS)

    config.DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = config.DATA_RAW_DIR / f"movies_{date.today():%Y%m%d}.json"
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(movies, file, ensure_ascii=False, indent=2)

    print(f"Listo: {len(movies)} películas guardadas en {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Descarga películas de TMDB.")
    parser.add_argument("--start-year", type=int, default=2000)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--pages", type=int, default=5)
    args = parser.parse_args()
    extract_movies(args.start_year, args.end_year, args.pages)


if __name__ == "__main__":
    main()