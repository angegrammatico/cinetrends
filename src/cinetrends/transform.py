"""Transform: limpia los datos crudos de TMDB y calcula métricas financieras.

Lee el archivo JSON más reciente de data/raw/ y guarda dos tablas en data/processed/:
- movies.csv: una fila por película, con presupuesto, ingresos, ganancia y ROI.
- movie_genres.csv: una fila por cada combinación película-género.

Uso (desde la carpeta src/):
    python -m cinetrends.transform
"""
import json

import numpy as np
import pandas as pd

from cinetrends import config

# Montos menores a esto (en dólares) los tratamos como errores de carga.
# En TMDB a veces alguien escribe "5" queriendo decir 5 millones.
MIN_VALID_AMOUNT = 1000

# Columnas que nos quedamos de cada ficha de TMDB.
COLUMNS = [
    "id",
    "title",
    "release_date",
    "budget",
    "revenue",
    "runtime",
    "vote_average",
    "vote_count",
    "popularity",
    "original_language",
]


def load_latest_raw_file():
    """Devuelve la lista de películas del archivo JSON más reciente de data/raw/."""
    raw_files = sorted(config.DATA_RAW_DIR.glob("movies_*.json"))
    if not raw_files:
        raise FileNotFoundError("No hay datos en data/raw/. Ejecutá primero cinetrends.extract.")
    latest_file = raw_files[-1]
    print(f"Leyendo {latest_file.name}")
    with open(latest_file, encoding="utf-8") as file:
        return json.load(file)


def build_movies_table(raw_movies):
    """Arma la tabla de películas limpia y con las métricas calculadas."""
    movies = pd.DataFrame(raw_movies)[COLUMNS]
    movies = movies.rename(columns={"id": "movie_id"})

    # Quitar películas repetidas.
    movies = movies.drop_duplicates(subset="movie_id")

    # Convertir la fecha de texto a fecha real y sacar el año.
    movies["release_date"] = pd.to_datetime(movies["release_date"], errors="coerce")
    movies["release_year"] = movies["release_date"].dt.year.astype("Int64")

    # TMDB usa 0 cuando no conoce el presupuesto o los ingresos.
    # Un 0 no es "costó cero", es "no sabemos", así que lo cambiamos por vacío (NaN).
    for column in ["budget", "revenue"]:
        movies[column] = movies[column].where(movies[column] >= MIN_VALID_AMOUNT, np.nan)

    # Solo podemos calcular rentabilidad si tenemos los dos montos.
    movies["has_financials"] = movies["budget"].notna() & movies["revenue"].notna()

    movies["profit"] = movies["revenue"] - movies["budget"]
    movies["roi"] = movies["profit"] / movies["budget"]

    return movies


def build_genres_table(raw_movies):
    """Arma una tabla con una fila por cada par película-género."""
    rows = []
    for movie in raw_movies:
        for genre in movie["genres"]:
            rows.append({"movie_id": movie["id"], "genre": genre["name"]})
    return pd.DataFrame(rows, columns=["movie_id", "genre"]).drop_duplicates()


def transform():
    """Ejecuta la transformación completa y guarda los CSV."""
    raw_movies = load_latest_raw_file()

    movies = build_movies_table(raw_movies)
    genres = build_genres_table(raw_movies)

    config.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    movies.to_csv(config.DATA_PROCESSED_DIR / "movies.csv", index=False)
    genres.to_csv(config.DATA_PROCESSED_DIR / "movie_genres.csv", index=False)

    with_financials = movies["has_financials"].sum()
    print(f"Películas: {len(movies)}")
    print(f"Con presupuesto e ingresos: {with_financials} ({with_financials / len(movies):.0%})")
    print(f"ROI mediano: {movies['roi'].median():.2f}")
    print(f"Guardado en {config.DATA_PROCESSED_DIR}")


if __name__ == "__main__":
    transform()