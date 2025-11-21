# app/api/routes/zones.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_admin
from app.schemas.zone import ZoneCreate, ZoneRead, ZoneUpdate
from app.models.zone import Zone

router = APIRouter(prefix="/zones", tags=["Zones"])


@router.get("/", response_model=list[ZoneRead])
def list_zones(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # juste pour exiger d'être connecté
):
    zones = db.query(Zone).all()
    return zones


@router.get("/{zone_id}", response_model=ZoneRead)
def get_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone non trouvée")
    return zone


@router.post("/", response_model=ZoneRead, status_code=status.HTTP_201_CREATED)
def create_zone(
    zone_in: ZoneCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin),
):
    zone = Zone(
        name=zone_in.name,
        postal_code=zone_in.postal_code,
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone

@router.patch("/{zone_id}", response_model=ZoneRead)
def update_zone(
    zone_id: int,
    zone_in: ZoneUpdate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin),
):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone non trouvée")

    if zone_in.name is not None:
        zone.name = zone_in.name
    if zone_in.postal_code is not None:
        zone.postal_code = zone_in.postal_code

    db.commit()
    db.refresh(zone)
    return zone


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin),
):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone non trouvée")

    db.delete(zone)
    db.commit()
    return
