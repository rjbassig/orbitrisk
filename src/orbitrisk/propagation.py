"""SGP4 propagation in the TEME inertial frame, with kilometers and km/s."""
from __future__ import annotations

from datetime import datetime
import numpy as np

from .ingestion import OrbitalObject


def state_at(obj: OrbitalObject, when: datetime) -> tuple[np.ndarray, np.ndarray]:
    stamp = when.timestamp() / 86400.0 + 2440587.5
    whole = int(stamp)
    error, position, velocity = obj.satrec.sgp4(whole, stamp - whole)
    if error:
        raise ValueError(f"SGP4 propagation failed for {obj.norad_id}: code {error}")
    return np.asarray(position, dtype=float), np.asarray(velocity, dtype=float)


def trajectory(obj: OrbitalObject, when: datetime, minutes: int = 95, step_seconds: int = 120) -> list[dict]:
    from datetime import timedelta
    return [
        {"timestamp": (when + timedelta(seconds=offset)).isoformat(), "position_km": state_at(obj, when + timedelta(seconds=offset))[0].round(3).tolist()}
        for offset in range(-minutes * 30, minutes * 30 + 1, step_seconds)
    ]
