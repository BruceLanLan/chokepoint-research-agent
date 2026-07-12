"""Professional research ops modules (v5.2–v5.51 maturity train)."""

from __future__ import annotations

PRO_MODULE_IDS = [
    "event_calendar",
    "consensus_notes",
    "filing_alerts",
    "sector_taxonomy",
    "factor_checklist",
    "valuation_scaffold",
    "risk_matrix",
    "scenario_tree",
    "supply_export",
    "peer_set",
    "catalyst_log",
    "channel_check",
    "capacity_tracker",
    "policy_watch",
    "geo_risk",
    "customer_map",
    "supplier_map",
    "tech_roadmap",
    "patent_notes",
    "pricing_power",
    "moat_score",
    "unit_econ",
    "cash_cycle",
    "capex_cycle",
    "inventory_signal",
    "channel_inventory",
    "asp_tracker",
    "gross_margin_bridge",
    "op_leverage",
    "dilution_watch",
    "insider_notes",
    "short_interest_notes",
    "options_flow_notes",
    "macro_link",
    "rates_fx_link",
    "commodity_link",
    "esg_process",
    "governance_flags",
    "related_party",
    "audit_quality",
    "litigation_log",
    "cyber_risk",
    "key_person",
    "culture_notes",
    "product_ladder",
    "attach_rate",
    "switching_cost",
    "network_effect",
    "data_moat",
    "platform_risk",
]

__all__ = ["PRO_MODULE_IDS", "list_pro_modules", "run_pro_module"]

def list_pro_modules():
    from src.ops.pro.registry import list_modules
    return list_modules()

def run_pro_module(module_id: str, **kwargs):
    from src.ops.pro.registry import invoke_module
    return invoke_module(module_id, **kwargs)
