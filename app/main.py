
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.session import engine
from app.db.base import Base
import app.models

from app.api.routes import auth, users, zones, sources, indicators, stats
from app.api.deps import oauth2_scheme

app = FastAPI(title="EcoTrack API")

# Création des tables
Base.metadata.create_all(bind=engine)

# CORS : pour autoriser le front à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # en dev on autorise tout, en prod tu peux restreindre
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers statiques du front
# -> http://127.0.0.1:8000/frontend/index.html
app.mount("/frontend", StaticFiles(directory="app/frontend", html=True), name="frontend")


# Inclusion des routes API
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(zones.router)
app.include_router(sources.router)
app.include_router(indicators.router)
app.include_router(stats.router)


# Route de test sécurité (optionnelle)
@app.get("/secure-example")
def secure_example(token: str = Depends(oauth2_scheme)):
    return {"message": "token ok"}


@app.get("/")
def root():
    return {"message": "EcoTrack API running"}




# # app/main.py
# from fastapi import FastAPI, Depends
# from app.api.routes import auth, users, zones, sources, indicators, stats
# from app.db.session import engine
# from app.db.base import Base
# import app.models  # important pour que les modèles soient enregistrés
# from app.api.deps import oauth2_scheme

# from fastapi.security import OAuth2PasswordBearer

# # app = FastAPI(title="EcoTrack API")


# app = FastAPI(
#     title="EcoTrack API",
#     description="API du projet EcoTrack",
# )

# Base.metadata.create_all(bind=engine)

# app.include_router(auth.router)
# app.include_router(users.router)
# app.include_router(zones.router)
# app.include_router(sources.router)
# app.include_router(indicators.router)
# app.include_router(stats.router)



# # Création des tables au démarrage (simple, sans Alembic)


# # @app.get("/")
# # def read_root():
# #     return {"message": "EcoTrack API is running"}


# @app.get("/secure-example")
# def secure_example(token: str = Depends(oauth2_scheme)):
#     return {"message": "token ok"}

# @app.get("/")
# def root():
#     return {"message": "EcoTrack API running with auth!"}
