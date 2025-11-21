# app/api/routes/indicators.py

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_admin
from app.schemas.indicator import IndicatorCreate, IndicatorRead, IndicatorUpdate
from app.models.indicator import Indicator
from app.models.zone import Zone
from app.models.source import Source

router = APIRouter(prefix="/indicators", tags=["Indicators"])


@router.get("/", response_model=list[IndicatorRead])
def list_indicators(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),

    # pagination
    skip: int = 0,
    limit: int = 100,

    # filtres
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    zone_id: int | None = None,
    source_id: int | None = None,
    indicator_type: str | None = None,
):
    """
    Lister les indicateurs avec filtres et pagination.
    - from_date / to_date : filtre sur la date
    - zone_id, source_id : filtre sur la zone / source
    - indicator_type : filtre sur le type (PM10, CO2, etc.)
    """

    query = db.query(Indicator)

    if from_date is not None:
        query = query.filter(Indicator.timestamp >= from_date)
    if to_date is not None:
        query = query.filter(Indicator.timestamp <= to_date)
    if zone_id is not None:
        query = query.filter(Indicator.zone_id == zone_id)
    if source_id is not None:
        query = query.filter(Indicator.source_id == source_id)
    if indicator_type is not None:
        query = query.filter(Indicator.type == indicator_type)

    indicators = (
        query.order_by(Indicator.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return indicators


@router.get("/{indicator_id}", response_model=IndicatorRead)
def get_indicator(
    indicator_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicateur non trouvé")
    return indicator


@router.post("/", response_model=IndicatorRead, status_code=status.HTTP_201_CREATED)
def create_indicator(
    indicator_in: IndicatorCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin),
):
    # (optionnel) vérifier que la zone et la source existent
    zone = db.query(Zone).filter(Zone.id == indicator_in.zone_id).first()
    if not zone:
        raise HTTPException(status_code=400, detail="Zone invalide")

    source = db.query(Source).filter(Source.id == indicator_in.source_id).first()
    if not source:
        raise HTTPException(status_code=400, detail="Source invalide")

    indicator = Indicator(
        type=indicator_in.type,
        value=indicator_in.value,
        unit=indicator_in.unit,
        timestamp=indicator_in.timestamp,
        zone_id=indicator_in.zone_id,
        source_id=indicator_in.source_id,
        extra_data=indicator_in.extra_data,
    )

    db.add(indicator)
    db.commit()
    db.refresh(indicator)
    return indicator


@router.patch("/{indicator_id}", response_model=IndicatorRead)
def update_indicator(
    indicator_id: int,
    indicator_in: IndicatorUpdate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin),
):
    indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicateur non trouvé")

    if indicator_in.type is not None:
        indicator.type = indicator_in.type
    if indicator_in.value is not None:
        indicator.value = indicator_in.value
    if indicator_in.unit is not None:
        indicator.unit = indicator_in.unit
    if indicator_in.timestamp is not None:
        indicator.timestamp = indicator_in.timestamp
    if indicator_in.zone_id is not None:
        indicator.zone_id = indicator_in.zone_id
    if indicator_in.source_id is not None:
        indicator.source_id = indicator_in.source_id
    if indicator_in.extra_data is not None:
        indicator.extra_data = indicator_in.extra_data

    db.commit()
    db.refresh(indicator)
    return indicator


@router.delete("/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_indicator(
    indicator_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin),
):
    indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicateur non trouvé")

    db.delete(indicator)
    db.commit()
    return
   
   
