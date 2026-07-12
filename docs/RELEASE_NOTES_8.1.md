# Release notes — v8.1.0

**Deep verticals in the golden path** (no new industry sprawl)

## Why

Five vertical packs (CPO, HBM, power/cooling, robotics actuators, specialty materials) already cover the AI-hardware chokepoint spine. v8.1 makes them **usable by default** instead of adding more YAML clones.

## What you can do

```bash
# Scaffold + research with deep process constraints
python main.py research --vertical cpo_optics

# List / inspect / suggest
python main.py progrp verticals
python main.py progrp verticals --show hbm_packaging
python main.py progrp verticals --suggest "CPO ELS silicon photonics"

# Offline suite only on the pack's pro modules (not all 50)
python main.py pro-suite --vertical cpo_optics --text "…"

# Desk shows vertical catalog + next actions
python main.py desk
```

API: `GET /pro/verticals`, `GET /pro/verticals/{id}`, `POST /pro/verticals/{id}/scaffold`,  
`POST /pro/suite` with `{"vertical":"cpo_optics",…}`.

UI Research tab: vertical dropdown + **Fill from vertical**.

## Tests

133 offline tests green.

Research / education only — not investment advice.
