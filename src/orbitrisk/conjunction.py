"""Geometric TLE screening followed by a local scalar minimization refinement."""
from __future__ import annotations

from datetime import datetime, timedelta
from itertools import combinations
from typing import Iterable

import numpy as np
from scipy.optimize import minimize_scalar

from .ingestion import OrbitalObject
from .propagation import state_at


def _relative(primary: OrbitalObject, secondary: OrbitalObject, when: datetime) -> tuple[float, float]:
    first_pos, first_vel = state_at(primary, when)
    second_pos, second_vel = state_at(secondary, when)
    return float(np.linalg.norm(first_pos - second_pos)), float(np.linalg.norm(first_vel - second_vel))


def screen(objects: Iterable[OrbitalObject], start: datetime, hours: int = 24, threshold_km: float = 100.0, step_minutes: int = 10) -> list[dict]:
    """Return refined minima found from a coarse candidate grid.

    This is a research screen, not an operational conjunction assessment.
    """
    if not 1 <= hours <= 72 or not 1 <= threshold_km <= 2000:
        raise ValueError("hours must be 1–72 and threshold_km must be 1–2000")
    result: list[dict] = []
    objects = list(objects)
    steps = range(0, hours * 60 + 1, step_minutes)
    for first, second in combinations(objects, 2):
        # Stations catalogs include attached modules that intentionally share a TLE.
        # They are not independent conjunction candidates.
        if first.line1[18:-1] == second.line1[18:-1] and first.line2[8:-1] == second.line2[8:-1]:
            continue
        distances = []
        for minute in steps:
            timestamp = start + timedelta(minutes=minute)
            try:
                distances.append(_relative(first, second, timestamp)[0])
            except ValueError:
                distances.append(float("inf"))
        candidate = int(np.argmin(distances))
        if not np.isfinite(distances[candidate]) or distances[candidate] > threshold_km * 1.5:
            continue
        center = start + timedelta(minutes=candidate * step_minutes)
        bound = step_minutes * 60
        objective = lambda seconds: _relative(first, second, center + timedelta(seconds=float(seconds)))[0]
        optimum = minimize_scalar(objective, bounds=(-bound, bound), method="bounded", options={"xatol": 0.01})
        tca = center + timedelta(seconds=float(optimum.x))
        miss_km, velocity_km_s = _relative(first, second, tca)
        if miss_km <= threshold_km:
            result.append({
                "primary": {"norad_id": first.norad_id, "name": first.name},
                "secondary": {"norad_id": second.norad_id, "name": second.name},
                "tca": tca.isoformat(),
                "miss_distance_km": round(miss_km, 4),
                "relative_velocity_km_s": round(velocity_km_s, 5),
                "screening_threshold_km": threshold_km,
                "method": "10-minute geometric screen + bounded scalar minimum refinement",
                "uncertainty": "No covariance is available in public TLE records; collision probability is not estimated.",
            })
    return sorted(result, key=lambda event: event["miss_distance_km"])
