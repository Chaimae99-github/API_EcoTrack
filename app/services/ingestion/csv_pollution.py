# app/services/ingestion/csv_pollution.py

import csv
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.indicator import Indicator
from app.models.source import Source
from app.models.zone import Zone


def get_or_create_source_csv(db: Session) -> Source:
    source = db.query(Source).filter(Source.name == "CSV Pollution").first()
    if source:
        return source

    source = Source(
        name="CSV Pollution",
        description="Données de pollution importées depuis un CSV open data",
        url="https://www.data.gouv.fr/",  # tu peux préciser la vraie URL si tu veux
        type="csv",
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def ingest_pollution_csv(db: Session, csv_path: str = "data/pollution.csv"):
    """
    Lit un fichier CSV et crée des Indicators.
    """
    source = get_or_create_source_csv(db)

    file_path = Path(csv_path)
    if not file_path.exists():
        print(f"[WARN] Fichier CSV {csv_path} introuvable, ingestion ignorée.")
        return 0

    indicators: list[Indicator] = []

    with file_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = datetime.fromisoformat(row["date"])

            # zone
            zone = (
                db.query(Zone)
                .filter(
                    Zone.name == row["zone_name"],
                    Zone.postal_code == row["postal_code"],
                )
                .first()
            )
            if not zone:
                zone = Zone(
                    name=row["zone_name"],
                    postal_code=row["postal_code"],
                )
                db.add(zone)
                db.commit()
                db.refresh(zone)

            indicator = Indicator(
                type=row["indicator_type"],
                value=float(row["value"]),
                unit=row["unit"],
                timestamp=ts,
                zone_id=zone.id,
                source_id=source.id,
                extra_data={"from": "csv"},
            )
            indicators.append(indicator)

    if indicators:
        db.add_all(indicators)
        db.commit()

    return len(indicators)
