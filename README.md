# Lab04 — UrbanBike Threat Model - HexNation

**Course:** SSD
**Group members:**  
Sultan Sikandar - UW-24-CY-BS-052 — Group Lead  
Eman Zafar - UW-24-CY-BS-022  DFD Modeler  
Uzair Hussian - UW-24-CY-BS-042 Threat Analyst  
Uzair Hussain - UW-24-CY-BS-042  Control Architect / Scan Engineer

## Scenario
UrbanBike smart bike-sharing backend. Riders unlock bikes; operators issue refunds.
The first backend version was built quickly and never reviewed.

## Results
- **Threats modelled:** 8 (S, T, R, I, D, E all covered; T1, T3, T4, T7 on crossing flows F3/F4/F6)
- **Semgrep findings:** 12 before → 0 after
- **Top 3 threats:**
  1. T1 — Unlock without login (Spoofing, 20 Critical) → `@require_auth()` — Complete mediation
  2. T3 — Cross-rider data read (Tampering, 16 High) → ownership check + parameterised SQL — Complete mediation + Defence in depth
  3. T5 — Lock API key exposure (Info disclosure, 16 High) → key from environment — Minimise attack surface

## Files
- `model/` — Threat Dragon JSON (Architecture v1 and v2)
- `app/app.py` — fixed application
- `rules/stride_rules.yml` — STRIDE Semgrep rules
- `map_threats.py` — maps findings to STRIDE letters
- `reports/` — baseline.json, after.json
- `screenshots/` — figures for the report

## Run the scan
```bash
python3 -m venv venv && source venv/bin/activate
pip install semgrep flask requests
semgrep --config rules/stride_rules.yml --metrics=off app/
semgrep --config rules/stride_rules.yml --metrics=off --json -o reports/baseline.json app/
python3 map_threats.py reports/baseline.json
