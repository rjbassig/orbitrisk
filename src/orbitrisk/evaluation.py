from .uncertainty import synthetic_probability


def convergence() -> list[dict]:
    return [{"samples": n, "probability": synthetic_probability(samples=n)["monte_carlo_probability"]} for n in (1000, 5000, 20_000, 100_000)]
