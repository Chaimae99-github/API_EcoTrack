# app/api/routes/stats.py

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.indicator import Indicator

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/average")
def average_indicator(
    indicator_type: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    zone_id: int | None = None,
    source_id: int | None = None,
):
    """
    Renvoie la moyenne d'un indicateur, avec des filtres optionnels.
    """

    query = db.query(
        func.avg(Indicator.value).label("avg_value"),
        func.count(Indicator.id).label("count"),
    ).filter(Indicator.type == indicator_type)

    if from_date is not None:
        query = query.filter(Indicator.timestamp >= from_date)
    if to_date is not None:
        query = query.filter(Indicator.timestamp <= to_date)
    if zone_id is not None:
        query = query.filter(Indicator.zone_id == zone_id)
    if source_id is not None:
        query = query.filter(Indicator.source_id == source_id)

    result = query.one()

    if result.count == 0:
        raise HTTPException(status_code=404, detail="Aucune donnée pour ces critères.")

    return {
        "indicator_type": indicator_type,
        "zone_id": zone_id,
        "source_id": source_id,
        "from_date": from_date,
        "to_date": to_date,
        "average": float(result.avg_value),
        "count": result.count,
    }


@router.get("/timeseries")
def indicator_timeseries(
    indicator_type: str,
    group_by: Literal["day", "month"] = "day",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    zone_id: int | None = None,
):
    """
    Renvoie une série temporelle des moyennes d'un indicateur,
    groupée par jour ou par mois.
    """

    # Choix de la fonction de groupement SQLite
    if group_by == "day":
        # 2025-11-21
        period_expr = func.date(Indicator.timestamp)
    else:  # "month"
        # 2025-11
        period_expr = func.strftime("%Y-%m", Indicator.timestamp)

    query = db.query(
        period_expr.label("period"),
        func.avg(Indicator.value).label("avg_value"),
        func.count(Indicator.id).label("count"),
    ).filter(Indicator.type == indicator_type)

    if from_date is not None:
        query = query.filter(Indicator.timestamp >= from_date)
    if to_date is not None:
        query = query.filter(Indicator.timestamp <= to_date)
    if zone_id is not None:
        query = query.filter(Indicator.zone_id == zone_id)

    query = query.group_by("period").order_by("period")

    rows = query.all()

    if not rows:
        raise HTTPException(status_code=404, detail="Aucune donnée pour ces critères.")

    points = [
        {
            "period": row.period,
            "average": float(row.avg_value),
            "count": row.count,
        }
        for row in rows
    ]

    # Format pratique pour un front (labels + series)
    return {
        "indicator_type": indicator_type,
        "group_by": group_by,
        "from_date": from_date,
        "to_date": to_date,
        "zone_id": zone_id,
        "labels": [p["period"] for p in points],
        "series": [
            {
                "name": f"{indicator_type} average",
                "data": [p["average"] for p in points],
            }
        ],
        "raw_points": points,  # utile pour debug
    }
