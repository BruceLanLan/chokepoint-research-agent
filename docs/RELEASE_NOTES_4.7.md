# Release notes — v4.7.0

Local extension marketplace, live LLM queue safety gate, quotes capability docs, CI smoke.

中文 → [zh/RELEASE_NOTES_4.7.md](./zh/RELEASE_NOTES_4.7.md)

```bash
python main.py marketplace
python main.py marketplace --q optics
python main.py queue --estimate-live
# live still blocked without explicit accept:
# python main.py queue --run 1 --live --i-accept-live-costs
python main.py queue --run 1   # mock, default safe
```

API: `GET /marketplace`, `GET /queue/estimate-live`, `GET /quotes/capabilities`  
Live `POST /queue/run` with `live:true` requires `i_accept_live_costs:true` or env `CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1`.

**Research only — not investment advice.**
