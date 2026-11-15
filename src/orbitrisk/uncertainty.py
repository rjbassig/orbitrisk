"""Explicitly synthetic, reproducible encounter-plane uncertainty experiments."""
from __future__ import annotations

import numpy as np
from scipy.stats import ncx2


def synthetic_probability(sigma_m: float = 100.0, hard_body_radius_m: float = 10.0, samples: int = 20_000, seed: int = 7) -> dict:
    if not 1 <= sigma_m <= 10_000 or not 0.1 <= hard_body_radius_m <= 100 or not 1_000 <= samples <= 100_000:
        raise ValueError("Synthetic controls are outside safe bounds")
    # Controlled 2-D encounter-plane scenario with a 1-sigma mean offset of 2 sigma.
    mean = np.array([2 * sigma_m, 0.0])
    rng = np.random.default_rng(seed)
    draws = rng.normal(mean, sigma_m, size=(samples, 2))
    probability = float((np.linalg.norm(draws, axis=1) <= hard_body_radius_m).mean())
    analytical = float(ncx2.cdf((hard_body_radius_m / sigma_m) ** 2, df=2, nc=4.0))
    return {
        "mode": "synthetic uncertainty experiment",
        "illustrative_only": True,
        "assumptions": "Isotropic Gaussian 2-D encounter-plane uncertainty; controlled mean miss of 2σ; not derived from a real TLE conjunction.",
        "sigma_m": sigma_m,
        "hard_body_radius_m": hard_body_radius_m,
        "samples": samples,
        "seed": seed,
        "monte_carlo_probability": probability,
        "analytical_probability": analytical,
    }
