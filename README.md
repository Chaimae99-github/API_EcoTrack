
# EcoTrack – API environnementale avec FastAPI - Chaimae HAJJI

*(Authentification JWT • CRUD complets • Statistiques • Ingestion API/CSV • Alembic • Tests • Front-end)*

EcoTrack est une API complète permettant de collecter, stocker, analyser et visualiser des **indicateurs environnementaux** : pollution, météo, énergie, déchets, etc.

Le projet met en œuvre :

* FastAPI
* JWT Auth + rôles
* SQLAlchemy ORM
* Alembic (migrations)
* Tests Pytest
* Ingestion API + CSV
* Front-end HTML/JS + Chart.js

---

## Table des matières

* [Fonctionnalités principales](#fonctionnalités-principales)
* [Architecture du projet](#architecture-du-projet)
* [Installation](#installation)
* [Base de données & migrations](#base-de-données--migrations)
* [Lancement du serveur](#lancement-du-serveur)
* [Authentification](#authentification)
* [Endpoints principaux](#endpoints-principaux)
* [Statistiques](#statistiques)
* [Ingestion de données externes](#ingestion-de-données-externes)
* [Tests](#tests)
* [Front-end](#front-end)
* [Améliorations possibles](#améliorations-possibles)
* [Résumé pour le professeur](#résumé-pour-le-professeur)

---

# Fonctionnalités principales

### Authentification & rôles

* Login via JWT (OAuth2 password flow)
* Route d’inscription
* Rôles gérés :

  * `user` → accès en lecture
  * `admin` → accès complet (CRUD)
* Protection via dépendances FastAPI

### CRUD complet

CRUD pour :

* Users
* Zones
* Sources
* Indicators

Avec :

* filtres
* pagination
* tri
* gestion erreurs

### Statistiques intégrées

* Moyenne (`/stats/average`)
* Séries temporelles (`/stats/timeseries`)
* Résultat formaté pour Chart.js

### Ingestion externe

* API Open-Meteo
* CSV pollution
* Création automatique zones / sources / indicators

### Front-end inclus

* HTML / JS
* Login JWT
* Affichage tableaux
* Création indicators
* Graphiques temps réel

### Tests

* Tests API (pytest + TestClient)
* Base SQLite dédiée aux tests
* Vérification stat, CRUD, auth

---

# Architecture du projet

```text
API_ecotrack/
  app/
    api/
      routes/
        auth.py
        users.py
        zones.py
        sources.py
        indicators.py
        stats.py
    core/
      config.py
      security.py
    db/
      base.py
      session.py
    models/
      user.py
      zone.py
      source.py
      indicator.py
      __init__.py
    schemas/
      user.py
      zone.py
      source.py
      indicator.py
    services/
      ingestion/
        open_meteo.py
        csv_pollution.py
    scripts/
      init_db.py
    frontend/
      index.html
      app.js
  alembic/
    env.py
    versions/
  alembic.ini
  requirements.txt
  README.md
  ecotrack.db
  tests/
```

---

# Installation

### 1. Cloner le projet

```bash
git clone <repo-url>
cd API_ecotrack
```

### 2. Environnement virtuel

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

# Base de données & migrations

### Configuration `alembic.ini`

```ini
sqlalchemy.url = sqlite:///./ecotrack.db
```

### Appliquer les migrations

```bash
alembic upgrade head
```

✔️ Crée automatiquement les tables `users`, `zones`, `sources`, `indicators`.

### (Optionnel) Initialiser la base avec des données

```bash
python -m app.scripts.init_db
```

---

# Lancement du serveur

```bash
uvicorn app.main:app --reload
```

* Swagger UI : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Front-end : [http://127.0.0.1:8000/frontend/index.html](http://127.0.0.1:8000/frontend/index.html)

---

# Authentification

### Inscription

```
POST /auth/register
```

### Connexion (JWT)

```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=<email>
password=<password>
```

### Dans Swagger

* Cliquer **Authorize**
* Entrer email + password
* Swagger récupère automatiquement le token Bearer

---

# Endpoints principaux

## Users

| Méthode | Endpoint       | Rôle   | Description |
| ------- | -------------- | ------ | ----------- |
| POST    | /auth/register | public | Inscription |
| POST    | /auth/login    | public | Connexion   |
| GET     | /users/me      | user   | Profil      |
| GET     | /users         | admin  | Liste       |
| PATCH   | /users/{id}    | admin  | Modifier    |
| DELETE  | /users/{id}    | admin  | Supprimer   |

---

## Zones (`/zones`)

* CRUD complet
* Accessible aux users pour lecture
* Admin pour écriture

---

## Sources (`/sources`)

* CRUD complet
* Métadonnées de source (API/CSV)

---

## Indicators (`/indicators`)

* Filtres :

  * `indicator_type`
  * `zone_id`
  * `source_id`
  * `from_date`, `to_date`
* Pagination : `skip`, `limit`
* Tri : timestamp DESC

---

# Statistiques

## Moyenne

```
GET /stats/average?indicator_type=temperature&zone_id=1
```

Réponse :

```json
{
  "indicator_type": "temperature",
  "zone_id": 1,
  "source_id": null,
  "from_date": null,
  "to_date": null,
  "average": 9,
  "count": 2
}
```

## Séries temporelles

```
GET /stats/timeseries?indicator_type=temperature&group_by=day
```

Formaté pour les graphes :

```json
{
  "indicator_type": "temperature",
  "group_by": "day",
  "from_date": null,
  "to_date": null,
  "zone_id": null,
  "labels": [
    "2025-11-19",
    "2025-11-20",
    "2025-11-21"
  ],
  "series": [
    {
      "name": "temperature average",
      "data": [
        9,
        3.8083333333333336,
        2.461224489795918
      ]
    }
  ],
  "raw_points": [
    {
      "period": "2025-11-19",
      "average": 9,
      "count": 2
    },
    {
      "period": "2025-11-20",
      "average": 3.8083333333333336,
      "count": 48
    },
    {
      "period": "2025-11-21",
      "average": 2.461224489795918,
      "count": 49
    }
  ]
}
```

---

# Ingestion de données externes

## 1. Open-Meteo

* récupération température / vent
* insertion dans `Indicator`
* création automatique de la source

## 2. CSV pollution

* format :

```csv
date,zone_name,postal_code,indicator_type,value,unit
```

* ingestion → `Zone`, `Source`, `Indicator`

---

# Tests

Lancer tous les tests :

```bash
pytest
```

Contient :

* `test_auth.py` → inscription + login + JWT
* `test_indicators_stats.py`
  → création indicators + stats (average + time series)

Utilise une base dédiée : `test_ecotrack.db`.

---

# Front-end

Accessible via :

--> [http://127.0.0.1:8000/frontend/index.html](http://127.0.0.1:8000/frontend/index.html)

Fonctionnalités :

* Login JWT (enregistrement token localStorage)
* Tableaux :

  * zones
  * sources
  * indicators
* Formulaire création indicator
* Stats avec Chart.js

---

# Améliorations possibles

* Déploiement cloud (Railway / Render)
* Ajout carte interactive (Leaflet)
* Statistiques min/max/trend
* Front React ou Vue.js
* Base PostgreSQL

---

