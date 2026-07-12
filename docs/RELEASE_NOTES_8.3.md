# Release notes — v8.3.0

**Frontmatter lineage + dual doctor scores**

## Highlights

1. **`vertical_id` in report frontmatter** when research/save/export uses a deep vertical pack (also `skill`).
2. **Catalog** lists `skill`, `vertical_id`, `thesis_id` — search and UI can filter by pack.
3. **Doctor** splits health into:
   - `config` score/grade (packages, keys, agent build)
   - `ops` score/grade (kill-monitor, skills, verticals, pro specs, queue)
   - `live_ready` vs `ops_ok` flags
4. Missing **Tavily** is a **warning** (search soft-fails); product `ok` can stay true for offline ops.

```bash
python main.py doctor          # see config A/ops A scores
python main.py research --mock -V cpo_optics
# reports/*.md frontmatter includes vertical_id: cpo_optics
```

147 offline tests. Research only — not investment advice.
