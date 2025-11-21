# tests/test_indicators_stats.py

from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.zone import Zone
from app.models.source import Source

TEST_DATABASE_URL = "sqlite:///./test_ecotrack.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def create_admin_direct_in_db():
    """
    Crée un utilisateur admin directement dans la base de test,
    sans passer par /auth/register (pour éviter les problèmes de schéma).
    """
    db = TestingSessionLocal()
    try:
        Base.metadata.create_all(bind=engine)

        admin_email = "admin@test.local"
        admin = db.query(User).filter(User.email == admin_email).first()
        if admin:
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
        return admin
    finally:
        db.close()


def get_token_for(client, email: str, password: str) -> str:
    resp = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_create_indicator_and_stats(client):
    # 1) Créer un admin directement en base de test
    admin = create_admin_direct_in_db()

    # 2) Récupérer un token pour cet admin via /auth/login
    token = get_token_for(client, admin.email, "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    # 3) Créer une zone via l'API
    resp = client.post(
        "/zones/",
        headers=headers,
        json={"name": "TestCity", "postal_code": "12345"},
    )
    assert resp.status_code == 201
    zone = resp.json()
    zone_id = zone["id"]

    # 4) Créer une source via l'API
    resp = client.post(
        "/sources/",
        headers=headers,
        json={
            "name": "TestSource",
            "description": "Source de test",
            "url": None,
            "type": "test",
        },
    )
    assert resp.status_code == 201
    source = resp.json()
    source_id = source["id"]

    # 5) Créer quelques indicators via l'API
    now = datetime.utcnow()
    for i in range(3):
        ts = (now - timedelta(hours=i)).isoformat()

        resp = client.post(
            "/indicators/",
            headers=headers,
            json={
                "type": "temperature",
                "value": 20 + i,
                "unit": "°C",
                "timestamp": ts,
                "zone_id": zone_id,
                "source_id": source_id,
                "extra_data": {"i": i},
            },
        )
        assert resp.status_code == 201

    # 6) Vérifier la récupération filtrée
    resp = client.get(
        "/indicators/?indicator_type=temperature&limit=10",
        headers=headers,
    )
    assert resp.status_code == 200
    indicators = resp.json()
    assert len(indicators) == 3

    # 7) Vérifier la moyenne
    resp = client.get(
        f"/stats/average?indicator_type=temperature&zone_id={zone_id}",
        headers=headers,
    )
    assert resp.status_code == 200
    avg_data = resp.json()
    assert avg_data["count"] == 3
    assert avg_data["indicator_type"] == "temperature"

    # 8) Vérifier la série temporelle
    resp = client.get(
        f"/stats/timeseries?indicator_type=temperature&zone_id={zone_id}",
        headers=headers,
    )
    assert resp.status_code == 200
    ts_data = resp.json()
    assert "labels" in ts_data
    assert "series" in ts_data
    assert len(ts_data["labels"]) >= 1
    assert len(ts_data["series"][0]["data"]) == len(ts_data["labels"])

