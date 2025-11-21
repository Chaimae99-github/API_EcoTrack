from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_admin
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user


# ------- CRUD ADMIN --------

@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 50,
):
    """
    Liste paginée des utilisateurs (admin seulement).
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_admin(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    """
    Créer un utilisateur (admin). Similaire à /auth/register mais réservé admin.
    """
    from app.core.security import get_password_hash

    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé.")

    hashed = get_password_hash(user_in.password)

    user = User(
        email=user_in.email,
        hashed_password=hashed,
        role=user_in.role,
        is_active=user_in.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user_admin(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    """
    Modifier email, rôle, is_active (admin).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if user_in.email is not None:
        # Vérifier que l'email n'est pas déjà pris par quelqu'un d'autre
        existing = (
            db.query(User)
            .filter(User.email == user_in.email, User.id != user_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Email déjà utilisé.")
        user.email = user_in.email

    if user_in.role is not None:
        user.role = user_in.role

    if user_in.is_active is not None:
        user.is_active = user_in.is_active

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    """
    Suppression d'un utilisateur (admin). Pour un vrai projet on ferait un soft delete,
    mais ici on peut supprimer.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    db.delete(user)
    db.commit()
    return
