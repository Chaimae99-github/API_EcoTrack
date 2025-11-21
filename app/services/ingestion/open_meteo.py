# app/services/ingestion/open_meteo.py

from datetime import datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from app.models.indicator import Indicator
from app.models.source import Source
from app.models.zone import Zone


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_or_create_source_open_meteo(db: Session) -> Source:
    source = db.query(Source).filter(Source.name == "Open-Meteo").first()
    if source:
        return source

    source = Source(
        name="Open-Meteo",
        description="Données météo depuis l'API Open-Meteo",
        url="https://open-meteo.com/",
        type="api",
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def get_or_create_zone(
    db: Session,
    name: str,
    postal_code: str | None = None,
) -> Zone:
    zone = (
        db.query(Zone)
        .filter(Zone.name == name, Zone.postal_code == postal_code)
        .first()
    )
    if zone:
        return zone

    zone = Zone(name=name, postal_code=postal_code)
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


def ingest_open_meteo_for_city(
    db: Session,
    city_name: str,
    postal_code: str | None,
    lat: float,
    lon: float,
):
    """
    Appelle Open-Meteo pour une ville, stocke température & vent
    en tant qu'Indicators.
    """

    source = get_or_create_source_open_meteo(db)
    zone = get_or_create_zone(db, name=city_name, postal_code=postal_code)

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,windspeed_10m",
        "past_days": 1,
        "forecast_days": 1,
        "timezone": "UTC",
    }

    resp = httpx.get(OPEN_METEO_URL, params=params, timeout=10.0)
    resp.raise_for_status()
    data = resp.json()

    times = data["hourly"]["time"]
    temps = data["hourly"]["temperature_2m"]
    winds = data["hourly"]["windspeed_10m"]

    indicators: list[Indicator] = []

    for t_str, temp, wind in zip(times, temps, winds):
        ts = datetime.fromisoformat(t_str)

        indicators.append(
            Indicator(
                type="temperature",
                value=float(temp),
                unit="°C",
                timestamp=ts,
                zone_id=zone.id,
                source_id=source.id,
                extra_data={"from": "open-meteo"},
            )
        )
        indicators.append(
            Indicator(
                type="windspeed",
                value=float(wind),
                unit="km/h",
                timestamp=ts,
                zone_id=zone.id,
                source_id=source.id,
                extra_data={"from": "open-meteo"},
            )
        )

    db.add_all(indicators)
    db.commit()

    return len(indicators)
