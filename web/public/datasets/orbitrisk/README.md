# OrbitRisk verified replay artifacts

These files are the exact public-TLE research release used by OrbitRisk. The source snapshot was retrieved from CelesTrak's credential-free Resource group and is provided with attribution; it is not a live feed.

- `resource-snapshot.tle`: original three-line element snapshot.
- `catalog-objects.csv`: 167 parser-valid catalog records.
- `screening-results.csv`: geometric 24-hour screen results (1,000 km threshold).
- `nearest-approaches.csv`: ranked geometric approaches under the separate 2,000 km ceiling.
- `metadata.json`: retrieval, filtering, counts, hashes, frame, units, and provenance.

All positions are SGP4 TEME states. These are geometric screening outputs, not collision probabilities or operational conjunction alerts. Preserve the source URL, retrieval timestamp, and SHA-256 when reproducing the release.
