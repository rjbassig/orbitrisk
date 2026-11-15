"""Validated, attributed ingestion of three-line TLE records."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from sgp4.api import Satrec


@dataclass(frozen=True)
class OrbitalObject:
    norad_id: int
    name: str
    line1: str
    line2: str
    satrec: Satrec
    epoch: datetime

    @property
    def inclination_deg(self) -> float:
        return self.satrec.inclo * 180.0 / 3.141592653589793

    @property
    def eccentricity(self) -> float:
        return self.satrec.ecco

    @property
    def mean_motion_rev_day(self) -> float:
        return self.satrec.no_kozai * 1440.0 / (2.0 * 3.141592653589793)


def _epoch(sat: Satrec) -> datetime:
    # SGP4 stores a Julian date; datetime conversion keeps the source epoch explicit.
    unix_days = sat.jdsatepoch + sat.jdsatepochF - 2440587.5
    return datetime.fromtimestamp(unix_days * 86400.0, tz=UTC)


def load_tle(path: Path) -> list[OrbitalObject]:
    lines = [line.rstrip() for line in path.read_text().splitlines() if line.strip()]
    if len(lines) % 3:
        raise ValueError("TLE source must contain complete name/line-1/line-2 records")
    objects: list[OrbitalObject] = []
    for index in range(0, len(lines), 3):
        name, line1, line2 = lines[index : index + 3]
        if not (line1.startswith("1 ") and line2.startswith("2 ")):
            raise ValueError(f"Invalid TLE record at line {index + 1}")
        sat = Satrec.twoline2rv(line1, line2)
        if sat.error:
            continue
        objects.append(OrbitalObject(int(sat.satnum), name.strip(), line1, line2, sat, _epoch(sat)))
    if len(objects) < 2:
        raise ValueError("At least two valid TLE records are required for screening")
    return objects
