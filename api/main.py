"""Read-only OrbitRisk research API; no operational warning capability."""
from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
import hashlib
import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from orbitrisk.conjunction import screen
from orbitrisk.evaluation import convergence
from orbitrisk.ingestion import load_tle
from orbitrisk.propagation import trajectory
from orbitrisk.uncertainty import synthetic_probability

ROOT = Path(__file__).resolve().parents[1]
TLE = ROOT / "data/raw/celestrak-stations.tle"
SOURCE = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle"
app = FastAPI(title="OrbitRisk", version="0.1.0", description="Public-TLE geometric screening and explicit synthetic uncertainty experiments.")
origins = [item.strip().rstrip("/") for item in os.getenv("ORBITRISK_CORS_ORIGINS", "https://orbitrisk.rjbassig.dev,https://rjbassig.dev,http://localhost:3000").split(",") if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET"], allow_headers=["Content-Type"])

@lru_cache(maxsize=1)
def catalog(): return load_tle(TLE)

def provenance():
    payload = TLE.read_bytes()
    objects = catalog()
    return {"source": SOURCE, "snapshot_file": TLE.name, "sha256": hashlib.sha256(payload).hexdigest(), "retrieved_at": datetime.fromtimestamp(TLE.stat().st_mtime, tz=UTC).isoformat(), "objects": len(objects), "frame": "TEME inertial", "units": "kilometers and km/s", "limitation": "Public TLEs have no covariance; this API never reports operational collision probability."}

@app.get("/health")
def health():
    try: return {"status": "ready", "catalog": provenance()}
    except Exception as error: raise HTTPException(503, f"Catalog unavailable: {error}")

@app.get("/api/provenance")
def get_provenance(): return provenance()

@app.get("/api/catalog")
def get_catalog():
    return [{"norad_id": item.norad_id, "name": item.name, "epoch": item.epoch.isoformat(), "inclination_deg": round(item.inclination_deg, 4), "eccentricity": item.eccentricity, "mean_motion_rev_day": round(item.mean_motion_rev_day, 6), "source": "CelesTrak Stations snapshot"} for item in catalog()]

@app.get("/api/trajectory/{norad_id}")
def get_trajectory(norad_id: int):
    obj = next((item for item in catalog() if item.norad_id == norad_id), None)
    if obj is None: raise HTTPException(404, "NORAD object not in the loaded catalog")
    return {"object": {"norad_id": obj.norad_id, "name": obj.name, "epoch": obj.epoch.isoformat()}, "frame": "TEME inertial", "points": trajectory(obj, datetime.now(UTC))}

@app.get("/api/conjunctions")
def get_conjunctions(hours: int = Query(24, ge=1, le=72), threshold_km: float = Query(1000, ge=1, le=2000)):
    return {"mode": "real public-TLE geometric screen", "generated_at": datetime.now(UTC).isoformat(), "events": screen(catalog(), datetime.now(UTC), hours, threshold_km), "limitations": "A screen is not an operational conjunction assessment. No covariance-derived collision probability is available from this public source."}

@app.get("/api/synthetic/probability")
def get_synthetic_probability(sigma_m: float = Query(100, ge=1, le=10000), hard_body_radius_m: float = Query(10, ge=.1, le=100), samples: int = Query(20000, ge=1000, le=100000), seed: int = Query(7, ge=0, le=999999)):
    return synthetic_probability(sigma_m, hard_body_radius_m, samples, seed)

@app.get("/api/synthetic/convergence")
def get_convergence(): return convergence()
