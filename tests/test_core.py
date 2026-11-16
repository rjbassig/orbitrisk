from pathlib import Path
from datetime import UTC, datetime

from orbitrisk.ingestion import load_tle
from orbitrisk.conjunction import screen
from orbitrisk.propagation import state_at
from orbitrisk.uncertainty import synthetic_probability

ROOT = Path(__file__).parents[1]

def test_public_snapshot_parses_and_propagates():
    objects = load_tle(ROOT / "data/raw/celestrak-resource.tle")
    position, velocity = state_at(objects[0], datetime.now(UTC))
    assert len(objects) >= 2 and position.shape == (3,) and velocity.shape == (3,)

def test_resource_screen_has_finite_ranked_results():
    objects = load_tle(ROOT / "data/raw/celestrak-resource.tle")
    events = screen(objects, datetime.now(UTC), hours=1, threshold_km=2000)
    assert events == sorted(events, key=lambda event: event["miss_distance_km"])
    assert all(event["miss_distance_km"] >= 0 and event["relative_velocity_km_s"] >= 0 for event in events)

def test_synthetic_probability_is_reproducible():
    assert synthetic_probability(samples=1000, seed=3) == synthetic_probability(samples=1000, seed=3)
