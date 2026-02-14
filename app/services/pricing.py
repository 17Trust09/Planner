from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

from app.models.project import Project
from app.services.evaluation import network_rollup


def _range(min_price: float, typical_price: float, max_price: float) -> dict:
    return {"min": min_price, "typical": typical_price, "max": max_price}


def _mul(price: dict, quantity: int | float) -> dict:
    return {
        "min": round(price["min"] * quantity, 2),
        "typical": round(price["typical"] * quantity, 2),
        "max": round(price["max"] * quantity, 2),
    }


def default_pricing_settings() -> dict:
    return {
        "meters_per_run": 20,
        "switch_split_threshold_ports": 48,
        "switch_split_poe_ratio": 0.4,
        "ranges": {
            "cat7_per_meter": _range(0.8, 1.2, 1.8),
            "lan_termination_per_run": _range(12, 18, 30),
            "indoor_ap": _range(85, 140, 240),
            "outdoor_ap": _range(120, 190, 320),
            "outdoor_camera": _range(90, 170, 320),
            "outdoor_doorbell": _range(140, 240, 420),
            "sensor_standard": _range(20, 45, 120),
            "switch_poe_8": _range(95, 160, 300),
            "switch_poe_16": _range(190, 330, 620),
            "switch_poe_24": _range(290, 520, 980),
            "switch_poe_48": _range(650, 1100, 2200),
            "switch_non_poe_8": _range(35, 70, 150),
            "switch_non_poe_16": _range(70, 140, 280),
            "switch_non_poe_24": _range(100, 220, 420),
            "switch_non_poe_48": _range(220, 420, 850),
            "router_upgrade": _range(130, 220, 420),
            "router_new": _range(130, 260, 520),
            "router_provider_plus_own": _range(190, 320, 650),
            "server_raspberry_pi": _range(110, 170, 280),
            "server_intel_nuc": _range(260, 480, 900),
            "server_unraid": _range(500, 900, 1800),
            "server_proxmox": _range(500, 900, 1800),
            "server_nas": _range(300, 650, 1400),
            "server_ha_green_yellow": _range(110, 180, 320),
        },
    }


def _sanitize_range(value: object, fallback: dict) -> dict:
    if not isinstance(value, dict):
        return fallback
    parsed = {}
    for key in ["min", "typical", "max"]:
        raw = value.get(key, fallback[key])
        try:
            parsed[key] = float(raw)
        except (TypeError, ValueError):
            parsed[key] = fallback[key]
    ordered = sorted([parsed["min"], parsed["typical"], parsed["max"]])
    return {"min": ordered[0], "typical": ordered[1], "max": ordered[2]}


def merged_pricing_settings(project: Project) -> dict:
    merged = deepcopy(default_pricing_settings())
    overrides = project.pricing_settings if isinstance(project.pricing_settings, dict) else {}

    for key in ["meters_per_run", "switch_split_threshold_ports", "switch_split_poe_ratio"]:
        if key in overrides:
            try:
                merged[key] = float(overrides[key])
            except (TypeError, ValueError):
                pass

    if "ranges" in overrides and isinstance(overrides["ranges"], dict):
        for range_key, fallback in merged["ranges"].items():
            merged["ranges"][range_key] = _sanitize_range(overrides["ranges"].get(range_key), fallback)

    merged["meters_per_run"] = max(1, int(round(merged["meters_per_run"])))
    merged["switch_split_threshold_ports"] = max(24, int(round(merged["switch_split_threshold_ports"])))
    merged["switch_split_poe_ratio"] = min(1.0, max(0.05, float(merged["switch_split_poe_ratio"])))
    return merged


def _first_selection(project: Project, key: str) -> str | None:
    selections = project.global_topics.get(key).selections if project.global_topics.get(key) else []
    return selections[0] if selections else None


def _switch_price_key(size: str, poe: bool) -> str | None:
    suffix = None
    if "8" in size:
        suffix = "8"
    elif "16" in size:
        suffix = "16"
    elif "24" in size:
        suffix = "24"
    elif "48" in size:
        suffix = "48"
    if suffix is None:
        return None
    prefix = "switch_poe" if poe else "switch_non_poe"
    return f"{prefix}_{suffix}"


def estimate_project_costs(project: Project) -> dict:
    net = network_rollup(project)
    cfg = merged_pricing_settings(project)
    ranges: Dict[str, dict] = cfg["ranges"]
    line_items: List[dict] = []

    total_runs = net["total_cables"]
    if total_runs > 0:
        cable_price_per_run = _mul(ranges["cat7_per_meter"], cfg["meters_per_run"])
        line_items.append(
            {
                "category": "CAT7-Verkabelung",
                "description": f"{total_runs} Kabelwege à ca. {cfg['meters_per_run']} m",
                "quantity": total_runs,
                "cost": _mul(cable_price_per_run, total_runs),
            }
        )
        line_items.append(
            {
                "category": "Netzwerkdosen/Abschluss",
                "description": "Patchfeld/Keystone/Datendose je Kabelweg",
                "quantity": total_runs,
                "cost": _mul(ranges["lan_termination_per_run"], total_runs),
            }
        )

    if net["total_ap_count"] > 0:
        line_items.append(
            {
                "category": "Indoor Access Points",
                "description": "Access Points im Innenbereich (PoE)",
                "quantity": net["total_ap_count"],
                "cost": _mul(ranges["indoor_ap"], net["total_ap_count"]),
            }
        )

    if net["outdoor_ap_count"] > 0:
        line_items.append(
            {
                "category": "Outdoor Access Points",
                "description": "Outdoor-APs (PoE)",
                "quantity": net["outdoor_ap_count"],
                "cost": _mul(ranges["outdoor_ap"], net["outdoor_ap_count"]),
            }
        )

    if net["outdoor_camera_count"] > 0:
        line_items.append(
            {
                "category": "Außenkameras",
                "description": "PoE-Kameras außen",
                "quantity": net["outdoor_camera_count"],
                "cost": _mul(ranges["outdoor_camera"], net["outdoor_camera_count"]),
            }
        )

    if net["outdoor_doorbell_count"] > 0:
        line_items.append(
            {
                "category": "Smarte Türklingeln",
                "description": "PoE-Türklingeln",
                "quantity": net["outdoor_doorbell_count"],
                "cost": _mul(ranges["outdoor_doorbell"], net["outdoor_doorbell_count"]),
            }
        )

    sensor_units = 0
    for room in project.rooms.values():
        sensor_units += len(room.topics["room_sensor_general"].selections)
        sensor_units += len(room.topics["room_climate_sensors"].selections)
    sensor_units += len(project.outdoor_topics["outdoor_smart_sensors"].selections)
    if sensor_units > 0:
        line_items.append(
            {
                "category": "Sensorik gesamt",
                "description": "Gewählte Sensor-Optionen (Innen + Außen)",
                "quantity": sensor_units,
                "cost": _mul(ranges["sensor_standard"], sensor_units),
            }
        )

    split_threshold_ports = cfg["switch_split_threshold_ports"]
    split_poe_ratio = cfg["switch_split_poe_ratio"]
    auto_split = net["ports_with_overhead"] >= split_threshold_ports or net["poe_ratio"] >= split_poe_ratio
    split_active = net["split_recommended"] or auto_split

    if split_active:
        poe_switch_key = _switch_price_key(net["split_plan"]["poe_switch"], poe=True)
        if poe_switch_key:
            line_items.append(
                {
                    "category": "PoE-Switch",
                    "description": f"PoE-Last separat ({net['split_plan']['poe_switch']})",
                    "quantity": 1,
                    "cost": ranges[poe_switch_key],
                }
            )

        client_switch_key = _switch_price_key(net["split_plan"]["client_switch"], poe=False)
        if client_switch_key:
            line_items.append(
                {
                    "category": "Non-PoE-Switch",
                    "description": f"Client/LAN separat ({net['split_plan']['client_switch']})",
                    "quantity": 1,
                    "cost": ranges[client_switch_key],
                }
            )
    else:
        selected = _first_selection(project, "global_switch_size") or net["recommended_switch"]
        key = _switch_price_key(selected, poe=True)
        if key:
            line_items.append(
                {
                    "category": "Switching",
                    "description": f"Einzelswitch: {selected}",
                    "quantity": 1,
                    "cost": ranges[key],
                }
            )

    router_selection = _first_selection(project, "global_router")
    router_mapping = {
        "Vorhanden, Upgrade empfohlen": "router_upgrade",
        "Neuanschaffung geplant": "router_new",
        "Provider-Router + eigener Router": "router_provider_plus_own",
    }
    router_key = router_mapping.get(router_selection)
    if router_key:
        line_items.append(
            {
                "category": "Router",
                "description": router_selection,
                "quantity": 1,
                "cost": ranges[router_key],
            }
        )

    server_selection = _first_selection(project, "global_server_hw")
    server_mapping = {
        "Raspberry Pi": "server_raspberry_pi",
        "Intel NUC / Mini-PC": "server_intel_nuc",
        "Unraid Server": "server_unraid",
        "Proxmox Host": "server_proxmox",
        "NAS (Synology/QNAP)": "server_nas",
        "Home Assistant Green/Yellow": "server_ha_green_yellow",
    }
    server_key = server_mapping.get(server_selection)
    if server_key:
        line_items.append(
            {
                "category": "Server-Plattform",
                "description": server_selection,
                "quantity": 1,
                "cost": ranges[server_key],
            }
        )

    totals = {
        "min": round(sum(i["cost"]["min"] for i in line_items), 2),
        "typical": round(sum(i["cost"]["typical"] for i in line_items), 2),
        "max": round(sum(i["cost"]["max"] for i in line_items), 2),
    }

    assumptions = [
        f"CAT7 mit ca. {cfg['meters_per_run']} m pro Kabelweg angenommen.",
        f"Switch-Split aktiv ab {cfg['switch_split_threshold_ports']} Ports oder PoE-Anteil >= {int(cfg['switch_split_poe_ratio'] * 100)}%.",
        "Alle Preise sind Richtwerte (lokal pflegbare Preisbänder).",
        "Montage-/Dienstleistungskosten sind nicht enthalten.",
    ]

    return {
        "line_items": line_items,
        "totals": totals,
        "assumptions": assumptions,
        "currency": "EUR",
        "settings_used": cfg,
        "switch_split_active": split_active,
    }
