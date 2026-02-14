from __future__ import annotations

from typing import Dict, List

from app.models.project import Project
from app.services.evaluation import network_rollup


def _range(min_price: float, typical_price: float, max_price: float) -> dict:
    return {"min": min_price, "typical": typical_price, "max": max_price}


def _mul(price: dict, quantity: int) -> dict:
    return {
        "min": round(price["min"] * quantity, 2),
        "typical": round(price["typical"] * quantity, 2),
        "max": round(price["max"] * quantity, 2),
    }


CAT7_PRICE_PER_METER = _range(0.8, 1.2, 1.8)
CAT7_DEFAULT_METERS_PER_RUN = 20
LAN_TERMINATION_PER_RUN = _range(12, 18, 30)

INDOOR_AP_PRICE = _range(85, 140, 240)
OUTDOOR_AP_PRICE = _range(120, 190, 320)
OUTDOOR_CAMERA_PRICE = _range(90, 170, 320)
OUTDOOR_DOORBELL_PRICE = _range(140, 240, 420)

SERVER_BY_SELECTION = {
    "Raspberry Pi": _range(110, 170, 280),
    "Intel NUC / Mini-PC": _range(260, 480, 900),
    "Unraid Server": _range(500, 900, 1800),
    "Proxmox Host": _range(500, 900, 1800),
    "NAS (Synology/QNAP)": _range(300, 650, 1400),
    "Home Assistant Green/Yellow": _range(110, 180, 320),
    "VM auf bestehendem Server": _range(0, 0, 0),
}

ROUTER_BY_SELECTION = {
    "Vorhanden und ausreichend": _range(0, 0, 0),
    "Vorhanden, Upgrade empfohlen": _range(130, 220, 420),
    "Neuanschaffung geplant": _range(130, 260, 520),
    "Provider-Router + eigener Router": _range(190, 320, 650),
}

SWITCH_BY_SIZE = {
    "Kein zusätzlicher Switch": _range(0, 0, 0),
    "8 Ports": _range(60, 110, 220),
    "16 Ports": _range(140, 250, 480),
    "24 Ports": _range(220, 390, 780),
    "48 Ports": _range(450, 780, 1500),
    "Mehrere Switches": _range(800, 1500, 3200),
    "Mehrere Switches oder 48+ Ports": _range(800, 1500, 3200),
}


def _first_selection(project: Project, key: str) -> str | None:
    selections = project.global_topics.get(key).selections if project.global_topics.get(key) else []
    return selections[0] if selections else None


def estimate_project_costs(project: Project) -> dict:
    net = network_rollup(project)
    line_items: List[dict] = []

    total_runs = net["total_cables"]
    if total_runs > 0:
        cable_price_per_run = _mul(CAT7_PRICE_PER_METER, CAT7_DEFAULT_METERS_PER_RUN)
        line_items.append(
            {
                "category": "CAT7-Verkabelung",
                "description": f"{total_runs} Kabelwege à ca. {CAT7_DEFAULT_METERS_PER_RUN} m",
                "quantity": total_runs,
                "cost": _mul(cable_price_per_run, total_runs),
            }
        )
        line_items.append(
            {
                "category": "Netzwerkdosen/Abschluss",
                "description": "Patchfeld/Keystone/Datendose je Kabelweg",
                "quantity": total_runs,
                "cost": _mul(LAN_TERMINATION_PER_RUN, total_runs),
            }
        )

    if net["total_ap_count"] > 0:
        line_items.append(
            {
                "category": "Indoor Access Points",
                "description": "Access Points im Innenbereich (PoE)",
                "quantity": net["total_ap_count"],
                "cost": _mul(INDOOR_AP_PRICE, net["total_ap_count"]),
            }
        )

    if net["outdoor_ap_count"] > 0:
        line_items.append(
            {
                "category": "Outdoor Access Points",
                "description": "Outdoor-APs (PoE)",
                "quantity": net["outdoor_ap_count"],
                "cost": _mul(OUTDOOR_AP_PRICE, net["outdoor_ap_count"]),
            }
        )

    if net["outdoor_camera_count"] > 0:
        line_items.append(
            {
                "category": "Außenkameras",
                "description": "PoE-Kameras außen",
                "quantity": net["outdoor_camera_count"],
                "cost": _mul(OUTDOOR_CAMERA_PRICE, net["outdoor_camera_count"]),
            }
        )

    if net["outdoor_doorbell_count"] > 0:
        line_items.append(
            {
                "category": "Smarte Türklingeln",
                "description": "PoE-Türklingeln",
                "quantity": net["outdoor_doorbell_count"],
                "cost": _mul(OUTDOOR_DOORBELL_PRICE, net["outdoor_doorbell_count"]),
            }
        )

    switch_selection = _first_selection(project, "global_switch_size") or net["recommended_switch"]
    switch_price = SWITCH_BY_SIZE.get(switch_selection)
    if switch_price and switch_price["typical"] > 0:
        line_items.append(
            {
                "category": "Switching",
                "description": f"Empfohlen/gewählt: {switch_selection}",
                "quantity": 1,
                "cost": switch_price,
            }
        )

    router_selection = _first_selection(project, "global_router")
    router_price = ROUTER_BY_SELECTION.get(router_selection) if router_selection else None
    if router_price and router_price["typical"] > 0:
        line_items.append(
            {
                "category": "Router",
                "description": router_selection,
                "quantity": 1,
                "cost": router_price,
            }
        )

    server_selection = _first_selection(project, "global_server_hw")
    server_price = SERVER_BY_SELECTION.get(server_selection) if server_selection else None
    if server_price and server_price["typical"] > 0:
        line_items.append(
            {
                "category": "Server-Plattform",
                "description": server_selection,
                "quantity": 1,
                "cost": server_price,
            }
        )

    totals = {
        "min": round(sum(i["cost"]["min"] for i in line_items), 2),
        "typical": round(sum(i["cost"]["typical"] for i in line_items), 2),
        "max": round(sum(i["cost"]["max"] for i in line_items), 2),
    }

    assumptions = [
        f"CAT7 mit ca. {CAT7_DEFAULT_METERS_PER_RUN} m pro Kabelweg angenommen.",
        "Alle Preise sind Richtwerte (Phase 1, lokal gepflegte Preisbänder).",
        "Montage-/Dienstleistungskosten sind nicht enthalten.",
    ]

    return {
        "line_items": line_items,
        "totals": totals,
        "assumptions": assumptions,
        "currency": "EUR",
    }
