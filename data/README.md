# Municipality skeleton data

This directory stores the canonical municipality master as JSONL.

- `municipalities.jsonl`: one record per target municipality, keyed by the six-digit local-government code.
- `municipality_sites_candidates.jsonl`: unverified official-site candidates collected from J-LIS.
- Do not place enrichment fields from unrelated domains directly into the master; keep them in domain-specific JSONL files and JOIN by `municipality_code`.
- A missing value means unknown/not yet researched, not “does not exist”.

Generate the 1,741-row skeleton from an official e-Stat municipality CSV export:

```bash
python scripts/build_skeleton.py /path/to/estat_municipalities.csv
```

The generator checks the unique code count and refuses to write output unless it equals 1,741. If the official export includes a different scope or date, inspect it rather than lowering the check silently.
