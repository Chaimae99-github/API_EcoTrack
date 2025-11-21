# app/api/routes/sources.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_admin
from app.schemas.source import SourceCreate, SourceRead, SourceUpdate
from app.models.source import Source

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.get("/", response_model=list[SourceRead])
def list_sources(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Lister toutes les sources (user connecté requis)."""
    sources = db.query(Source).all()
    return sources


@router.get("/{source_id}", response_model=SourceRead)
def get_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Récupérer une source par son id."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source non trouvée")
    return source


@router.post("/", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
def create_source(
    source_in: SourceCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin),
):
    """Créer une nouvelle source (admin uniquement)."""
    source = Source(
        name=source_in.name,
        description=source_in.description,
        url=str(source_in.url) if source_in.url else None,
        type=source_in.type,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.patch("/{source_id}", response_model=SourceRead)
def update_source(
    source_id: int,
    source_in: SourceUpdate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin),
):
    """Mettre à jour une source (admin uniquement)."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source non trouvée")

    if source_in.name is not None:
        source.name = source_in.name
    if source_in.description is not None:
        source.description = source_in.description
    if source_in.url is not None:
        source.url = str(source_in.url)
    if source_in.type is not None:
        source.type = source_in.type

    db.commit()
    db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    source_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_current_admin),
):
    """Supprimer une source (admin uniquement)."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source non trouvée")

    db.delete(source)
    db.commit()
    return

