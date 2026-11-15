# OrbitRisk

**OrbitRisk** is a reproducible research application for public-TLE orbit propagation, geometric conjunction screening, and clearly separated synthetic uncertainty experiments.

Live application: `https://orbitrisk.rjbassig.dev`  
Portfolio: `https://rjbassig.dev/work/orbitrisk`  
Research report: `https://rjbassig.dev/work/orbitrisk/report`

## What it does

The real-data mode loads CelesTrak's credential-free Stations TLE catalog, keeps the original TLE snapshot in `data/raw`, parses NORAD identifiers and orbital metadata, propagates TEME states with SGP4, and screens pairs over a configurable window. A 10-minute coarse scan supplies candidates; each candidate is refined with a bounded scalar minimization of relative distance. The API reports TCA, miss distance, and relative velocity.

The synthetic mode is deliberately separate. It estimates collision probability for a controlled two-dimensional encounter-plane experiment with explicit Gaussian covariance and hard-body-radius assumptions. It is not a probability estimate for a public-TLE event.

## Data provenance and limits

- **Source:** [CelesTrak GP data](https://celestrak.org/NORAD/documentation/gp-data-formats.php), Stations group. The original downloaded snapshot and a SHA-256 exposed by `/api/provenance` make the release auditable.
- **Frame and units:** SGP4 returns TEME inertial position/velocity, in km and km/s. The app does not present these raw states as Earth-fixed coordinates.
- **Freshness:** every catalog response exposes each TLE epoch; the API exposes the snapshot retrieval time. Refresh `data/raw/celestrak-stations.tle` with `curl` when reproducing a later screen.
- **Limitations:** public TLEs do not provide covariance or the state quality required for operational conjunction assessment. The project is not a warning service and never assigns a real collision probability.

## Architecture

```text
data/raw/celestrak-stations.tle -> ingestion -> SGP4/TEME propagation
                                            -> coarse screen + refined TCA -> FastAPI
                                                                           -> Next.js + React Three Fiber
```

`api/main.py` provides a read-only, bounded API. `web/` is a Vercel-ready Next.js viewer. The browser visualizes only propagated API trajectories; marker size is explicitly exaggerated for visibility.

## Local development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m uvicorn api.main:app --reload

cd web
cp .env.example .env.local
npm install
npm run dev
```

Set `ORBITRISK_API_BASE_URL` to the API URL for a deployed frontend. The frontend proxies API requests through `/api/research`.

## Tests and reproducibility

```bash
PYTHONPATH=src python -m pytest
curl http://localhost:8000/health
curl 'http://localhost:8000/api/conjunctions?hours=24&threshold_km=1000'
```

The tests validate parsing/SGP4 state generation and deterministic synthetic Monte Carlo with an explicit seed. Controlled scenarios and user-facing results should be regenerated from the source snapshot; do not compare outputs across snapshots without recording source epochs.

## Deployment

- **API:** Railway from repository root. `railway.toml` starts `python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT`. Set `ORBITRISK_CORS_ORIGINS=https://orbitrisk.rjbassig.dev,https://rjbassig.dev`.
- **Frontend:** Vercel with `web` as the root directory. Set `ORBITRISK_API_BASE_URL` to the Railway public HTTPS URL.
- **DNS:** add `orbitrisk.rjbassig.dev` to the Vercel frontend project, then apply the exact DNS record Vercel supplies at the domain registrar.

No credentials, raw bulk catalogs, model checkpoints, or private data are required or committed.
