"""Export a bounded, auditable public-TLE snapshot for free static hosting."""
from __future__ import annotations

import json
import hashlib
from datetime import UTC, datetime
from pathlib import Path

from orbitrisk.conjunction import screen
from orbitrisk.ingestion import load_tle
from orbitrisk.propagation import trajectory
from orbitrisk.uncertainty import synthetic_probability

ROOT = Path(__file__).parents[1]
TLE = ROOT / "data/raw/celestrak-stations.tle"
OUT = ROOT / "web/public/research/orbitrisk-snapshot.json"
SOURCE = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle"

now = datetime.now(UTC)
objects = load_tle(TLE)
catalog = [{"norad_id": obj.norad_id, "name": obj.name, "epoch": obj.epoch.isoformat(), "inclination_deg": round(obj.inclination_deg, 4), "eccentricity": obj.eccentricity, "mean_motion_rev_day": round(obj.mean_motion_rev_day, 6)} for obj in objects]
payload = {
    "mode": "precomputed public-TLE snapshot",
    "generated_at": now.isoformat(),
    "source": SOURCE,
    "frame": "TEME inertial",
    "units": "kilometers and km/s",
    "limitation": "This static release is a reproducible geometric screen, not an operational conjunction assessment. Public TLEs contain no covariance.",
    "sha256": hashlib.sha256(TLE.read_bytes()).hexdigest(),
    "retrieved_at": datetime.fromtimestamp(TLE.stat().st_mtime, tz=UTC).isoformat(),
    "catalog": catalog,
    "trajectories": [{"object": catalog[index], "points": trajectory(obj, now)} for index, obj in enumerate(objects[:4])],
    "screen": {"window_hours": 24, "threshold_km": 1000, "events": screen(objects, now, 24, 1000)},
    "synthetic": synthetic_probability(),
}
OUT.write_text(json.dumps(payload, separators=(",", ":")))
print(OUT)
