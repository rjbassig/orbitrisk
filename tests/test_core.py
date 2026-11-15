from pathlib import Path
from datetime import UTC, datetime

from orbitrisk.ingestion import load_tle
from orbitrisk.propagation import state_at
from orbitrisk.uncertainty import synthetic_probability

ROOT = Path(__file__).parents[1]

def test_public_snapshot_parses_and_propagates():
    objects = load_tle(ROOT / "data/raw/celestrak-stations.tle")
    position, velocity = state_at(objects[0], datetime.now(UTC))
    assert len(objects) >= 2 and position.shape == (3,) and velocity.shape == (3,)

def test_synthetic_probability_is_reproducible():
    assert synthetic_probability(samples=1000, seed=3) == synthetic_probability(samples=1000, seed=3)
