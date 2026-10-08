# 🎬 CineTrends: rentabilidad y tendencias de la industria del cine

¿Qué películas son realmente rentables? CineTrends descarga datos de miles de películas desde la API de [TMDB](https://www.themoviedb.org/), los limpia con Python, los guarda en una base de datos SQL y los analiza en un dashboard de Power BI.

**Estado:** en construcción

## Preguntas de negocio

- ¿Qué géneros tienen el mejor retorno de la inversión (ROI)?
- ¿Un presupuesto más alto garantiza más ingresos?
- ¿Cómo cambiaron los presupuestos y las ganancias a lo largo de los años?

## Arquitectura

API de TMDB → Extract (Python) → Transform (Pandas) → Load (SQLite + CSV) → Dashboard (Power BI)

## Tecnologías

Python · Pandas · NumPy · SQL (SQLite) · Power BI · pytest · Git

## Estructura del repositorio

    cinetrends/
    ├── data/raw/         datos crudos de la API (no se suben)
    ├── data/processed/   datos limpios (no se suben)
    ├── notebooks/        exploración de datos
    ├── sql/              consultas SQL
    ├── src/cinetrends/   código del pipeline
    ├── tests/            pruebas automáticas
    ├── powerbi/          dashboard de Power BI
    └── docs/img/         capturas del dashboard

## Resultados

_Próximamente._

## Fuente de datos

Este producto usa la API de TMDB, pero no está respaldado ni certificado por TMDB.