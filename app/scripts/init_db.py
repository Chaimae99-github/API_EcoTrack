# app/scripts/init_db.py

from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.db.base import Base
import app.models  # important pour que les tables existent

from app.core.security import get_password_hash
from app.models.user import User
from app.services.ingestion.open_meteo import ingest_open_meteo_for_city
from app.services.ingestion.csv_pollution import ingest_pollution_csv


def create_admin_if_not_exists(db: Session):
    admin_email = "admin@ecotrack.com"
    admin = db.query(User).filter(User.email == admin_email).first()
    if admin:
        print("[INFO] Admin existe déjà.")
        return admin

    admin = User(
        email=admin_email,
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"[INFO] Admin créé : {admin_email} / admin123")
    return admin


def main():
    print("[INFO] Création des tables (si nécessaire)...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1) Admin
        create_admin_if_not_exists(db)

        # 2) Ingestion Open-Meteo (exemple pour Paris)
        print("[INFO] Ingestion Open-Meteo...")
        count_meteo = ingest_open_meteo_for_city(
            db,
            city_name="Paris",
            postal_code="75000",
            lat=48.8566,
            lon=2.3522,
        )
        print(f"[INFO] {count_meteo} indicateurs météo insérés.")

        # 3) Ingestion CSV pollution
        print("[INFO] Ingestion CSV pollution...")
        count_csv = ingest_pollution_csv(db)
        print(f"[INFO] {count_csv} indicateurs pollution insérés.")

    finally:
        db.close()
        print("[INFO] Script terminé.")


if __name__ == "__main__":
    main()
