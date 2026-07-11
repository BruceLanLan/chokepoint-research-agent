# Release notes — v4.5.0

Workspace digest, knowledge-map compare, hypotheses scratchpad, report frontmatter enrichment.

中文 → [zh/RELEASE_NOTES_4.5.md](./zh/RELEASE_NOTES_4.5.md)

```bash
python main.py digest
python main.py compare-maps cpo_ai_interconnect optical_pluggables
python main.py hypothesis --add "ELS remains sole-source for 2 years" --system CPO
python main.py hypothesis --list
python main.py hypothesis --promote <id>
python main.py enrich-report some_memo.md
```

API: `GET /digest`, `GET /maps/compare?a=&b=`, `GET|POST /hypotheses`, `POST /reports/{name}/enrich`

**Research only — not investment advice.**
