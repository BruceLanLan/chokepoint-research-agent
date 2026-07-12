# Release notes — v8.6.0

**Same-vertical research memo compare**

## Why

After filtering the catalog by `vertical_id`, analysts need a one-command way to see what changed between two coverage passes: scorecard nodes, quality delta, and text similarity.

## Usage

```bash
# List memos in a pack
python main.py compare-vertical cpo_optics --list

# Latest two for a vertical
python main.py compare-vertical cpo_optics

# Explicit pair
python main.py compare-vertical --a older.md --b newer.md --no-udiff
```

API:

```bash
curl -s 'localhost:8000/reports/by-vertical/cpo_optics'
curl -s 'localhost:8000/reports/compare?vertical_id=cpo_optics'
curl -s -X POST localhost:8000/reports/compare \
  -H 'Content-Type: application/json' \
  -d '{"a":"older.md","b":"newer.md"}'
```

UI **Reports**: filter vertical → set A/B (or row buttons) → **Compare pair** / **Latest in vertical**.

Output highlights: `similarity_ratio`, `quality_delta_b_minus_a`, shared/only-A/only-B scorecard nodes, next_actions, optional udiff.

162 offline tests. Research only — not investment advice.
