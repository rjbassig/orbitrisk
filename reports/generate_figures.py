"""Generate figures and tables from the verified static replay snapshot."""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
snapshot = json.loads((ROOT / "web/public/research/orbitrisk-snapshot.json").read_text())
events = snapshot["screen"]["nearest_approaches"][:10]
out = ROOT / "reports/figures"
out.mkdir(parents=True, exist_ok=True)
with (ROOT / "reports/nearest_approaches.csv").open("w", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["rank", "primary", "secondary", "tca", "miss_distance_km", "relative_velocity_km_s", "screening_threshold_km"])
    for index, event in enumerate(events, 1):
        writer.writerow([index, event["primary"]["name"], event["secondary"]["name"], event["tca"], event["miss_distance_km"], event["relative_velocity_km_s"], event["screening_threshold_km"]])

labels = [f'{e["primary"]["name"]} × {e["secondary"]["name"]}' for e in events][::-1]
values = [e["miss_distance_km"] for e in events][::-1]
width, row_height, left = 1000, 42, 260
max_value = max(values or [1])
rows = []
for index, (label, value) in enumerate(zip(labels, values)):
    y = 70 + index * row_height
    bar = 620 * value / max_value
    rows.append(f'<text x="16" y="{y + 18}" fill="#c4d0c8" font-size="13">{label}</text><rect x="{left}" y="{y}" width="{bar:.1f}" height="20" fill="#9fc7bb"/><text x="{left + bar + 8:.1f}" y="{y + 15}" fill="#f0f4ef" font-size="12">{value:.2f} km</text>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {max(130, 100 + len(rows) * row_height)}"><rect width="100%" height="100%" fill="#101412"/><text x="16" y="28" fill="#f0f4ef" font-size="18">OrbitRisk nearest geometric approaches · Resource catalog</text>{"".join(rows)}</svg>'
(out / "nearest_approaches.svg").write_text(svg)
print(out / "nearest_approaches.svg")
