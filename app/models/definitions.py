from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


DEFAULT_FLOORS: Dict[str, List[dict]] = {
    "EG": [
        {"name": "Wohnzimmer", "room_type": "living"},
        {"name": "HTR", "room_type": "utility"},
        {"name": "Flur EG", "room_type": "hallway"},
        {"name": "WC EG", "room_type": "bathroom"},
        {"name": "Büro", "room_type": "office"},
    ],
    "OG": [
        {"name": "Kinderzimmer 1", "room_type": "bedroom"},
        {"name": "Kinderzimmer 2", "room_type": "bedroom"},
        {"name": "Flur OG", "room_type": "hallway"},
        {"name": "Ankleide", "room_type": "bedroom"},
        {"name": "Schlafzimmer", "room_type": "bedroom"},
        {"name": "Bad", "room_type": "bathroom"},
    ],
}

ROOM_TYPE_OPTIONS: Dict[str, str] = {
    "living": "Wohnen",
    "bedroom": "Schlafen/Kinder",
    "office": "Arbeiten/Büro",
    "bathroom": "Bad/WC",
    "kitchen": "Küche",
    "hallway": "Flur/Verkehr",
    "utility": "Technik/HTR/Keller",
    "outdoor": "Außenbereich",
    "other": "Sonstiges",
}

DOMAIN_SMART = "SMART_HOME"
DOMAIN_ELEC = "ELEKTRIK"
DOMAIN_IT = "IT_NETZWERK"
DOMAINS = [DOMAIN_SMART, DOMAIN_ELEC, DOMAIN_IT]

OPTION_SETS: Dict[str, List[str]] = {
    "CONTROL_OPTIONS": [
        "Kippschalter (klassisch)", "Taster (Impuls)", "Doppeltaster / Szenentaster", "Drehdimmer",
        "Wallpanel/Tablet", "Sprachsteuerung (optional)", "App (nur Ergänzung)",
    ],
    "LIGHT_OPTIONS": [
        "Nur Grundbeleuchtung", "Zonen (mehrere Lichtkreise)", "Indirekt (LED-Cove/Decke/Wand)",
        "Direkt (Spots/Downlights)", "Akzentlicht (Regal/Nische)", "RGB (Ambient)",
        "Tunable White (Warm/Kalt)",
    ],
    "LIGHT_LOGIC_OPTIONS": [
        "Aktor im Schaltschrank (Stern)", "Aktor Unterputz (dezentral)",
        "Smarte Leuchtmittel (Dauerstrom)", "Mischform (Aktor + smarte Lampen)",
    ],
    "SENSOR_OPTIONS": [
        "Bewegungsmelder", "Präsenzmelder (mmWave)", "Fensterkontakt", "Türkontakt", "Temperatur",
        "Luftfeuchte", "CO₂ / Luftqualität", "Helligkeit",
    ],
    "HEAT_OPTIONS": [
        "Keine Einzelraumregelung", "Thermostat (Heizkörper)", "FBH (Fußbodenheizung) – Raumregelung",
        "Fenster-auf-Erkennung", "Zeitprogramm", "Nachtabsenkung / Eco-Modus",
    ],
    "SHADE_OPTIONS": [
        "Keine Beschattung", "Manuell", "Zeitgesteuert", "Sonnenstand (Azimut/Höhe)",
        "Wetter/Windschutz", "Sommer-Hitzeschutz",
    ],
    "ROOM_NETWORK_OPTIONS": [
        "LAN-Dose vorhanden", "LAN-Dose optional", "WLAN reicht", "AP in/nahe Raum geplant",
        "PoE im Raum (z.B. Panel/Kamera)",
    ],
    "SECURITY_OPTIONS": [
        "Kein Bedarf", "Fensterkontakte", "Türkontakt", "Alarmmodus (Nacht/Abwesend)",
        "Sirene/Signalgeber", "Kamera (lokal)",
    ],
    "WATER_OPTIONS": [
        "Nicht nötig", "Lecksensor", "Lecksensor + Push-Alarm", "Lecksensor + Absperrventil (optional)",
    ],
    "POWER_OPTIONS": [
        "Normale Steckdosen", "Schaltbar (Smart Plug)", "Schaltbar + Messung", "Fester Aktor/Relais + Messung",
        "Großverbraucher separat messen",
    ],
    "YES_MAYBE_NO": ["Ja", "Vielleicht", "Nein"],
    "GLOBAL_STERN_OPTIONS": [
        "Keine Sternverkabelung (klassisch)", "Teilweise Sternverkabelung", "Komplette Sternverkabelung",
        "Zentrale Aktoren (Hutschiene)", "Dezentrale Aktoren (UP)",
    ],
    "GLOBAL_PHASE_OPTIONS": [
        "Nicht relevant", "3 Phasen sauber verteilt", "3 Phasen + Lastmanagement vorgesehen",
        "Lastmanagement zwingend (WP/Wallbox)",
    ],
    "SERVER_OPTIONS": [
        "Raspberry Pi", "Intel NUC / Mini-PC", "Unraid Server", "Proxmox Host",
        "NAS (Synology/QNAP)", "Home Assistant Green/Yellow", "VM auf bestehendem Server",
    ],
    "HA_OS_OPTIONS": [
        "Home Assistant OS", "Home Assistant Container", "Home Assistant Supervised", "Home Assistant Core",
    ],
    "BACKUP_OPTIONS": [
        "Keine Strategie", "Lokales Backup", "NAS-Backup", "Offsite-Backup", "3-2-1 Backup-Strategie",
    ],
    "PROTOCOL_OPTIONS": [
        "Zigbee", "Z-Wave", "Thread/Matter", "KNX", "Modbus", "WLAN", "Bluetooth", "MQTT",
    ],
    "CABLE_OPTIONS": [
        "Klassische Verdrahtung", "Teilweise Sternverdrahtung", "Komplette Sternverdrahtung",
        "BUS-basierte Verdrahtung", "Mischform",
    ],
    "ROOM_ROLE_OPTIONS": [
        "Wohnen", "Arbeiten", "Schlafen", "Kinder", "Bad/Wellness", "Technikraum", "Verkehrsfläche",
    ],
    "COVERAGE_OPTIONS": [
        "Hoch (Office/Streaming)", "Mittel", "Basis", "Optional",
    ],
    "CAMERA_STORAGE_OPTIONS": [
        "Keine Kamera", "NVR lokal", "NAS-Aufzeichnung", "SD-Karte lokal", "Hybrid",
    ],
    "AUTOMATION_LEVEL_OPTIONS": [
        "Keine Automationen", "Basis (Zeit/Schwellwert)", "Mittel (Szenen + Präsenz)", "Erweitert (Kontext + Energie)",
    ],
}


@dataclass(frozen=True)
class TopicDefinition:
    key: str
    section: str
    title: str
    description: str
    option_set: str
    domains: List[str]
    required_for_export: bool = False
    max_selections: int = 3
    applicable_room_types: List[str] | None = None


GLOBAL_TOPICS: List[TopicDefinition] = [
    TopicDefinition("global_goal", "ALLGEMEIN", "Zielsetzung", "Fokus Komfort/Energie/Sicherheit/Technik", "YES_MAYBE_NO", [DOMAIN_SMART], True, 3),
    TopicDefinition("global_cloud", "ALLGEMEIN", "Cloud-Policy", "Cloud-Nutzung gewünscht oder vermeiden", "YES_MAYBE_NO", [DOMAIN_SMART, DOMAIN_IT], False, 3),
    TopicDefinition("global_docs", "ALLGEMEIN", "Dokumentation", "Planung und Änderungen dokumentieren", "YES_MAYBE_NO", [DOMAIN_SMART, DOMAIN_ELEC, DOMAIN_IT], True, 3),
    TopicDefinition("global_room_roles", "ALLGEMEIN", "Raumnutzungsprofil", "Nutzungsarten als Planungsbasis", "ROOM_ROLE_OPTIONS", [DOMAIN_SMART], True, 3),

    TopicDefinition("global_server_hw", "SERVER & PLATTFORM", "Server-Hardware", "Hostsystem für Smart Home", "SERVER_OPTIONS", [DOMAIN_IT, DOMAIN_SMART], True, 3),
    TopicDefinition("global_ha_mode", "SERVER & PLATTFORM", "Home-Assistant-Betriebsart", "Installationsmodus für HA", "HA_OS_OPTIONS", [DOMAIN_IT, DOMAIN_SMART], True, 2),
    TopicDefinition("global_backup", "SERVER & PLATTFORM", "Backup-Strategie", "Datensicherung & Restore", "BACKUP_OPTIONS", [DOMAIN_IT], True, 3),

    TopicDefinition("global_stern", "VERDRAHTUNG & ELEKTRIK", "Sternverkabelung / Aktoren", "Zentrale/dezentrale Strategie", "GLOBAL_STERN_OPTIONS", [DOMAIN_ELEC], True),
    TopicDefinition("global_cable_type", "VERDRAHTUNG & ELEKTRIK", "Verdrahtungsart", "Wahl der grundlegenden Verdrahtung", "CABLE_OPTIONS", [DOMAIN_ELEC], True),
    TopicDefinition("global_phase", "VERDRAHTUNG & ELEKTRIK", "Phasen-/Lastverteilung", "Belastung und Lastmanagement", "GLOBAL_PHASE_OPTIONS", [DOMAIN_ELEC], True),
    TopicDefinition("global_fi", "VERDRAHTUNG & ELEKTRIK", "FI/RCD-Konzept", "Schutzkonzept abgestimmt", "YES_MAYBE_NO", [DOMAIN_ELEC], True),
    TopicDefinition("global_anschluss", "VERDRAHTUNG & ELEKTRIK", "Anschlussplan", "Anschluss-/Klemmenplan vorhanden", "YES_MAYBE_NO", [DOMAIN_ELEC], True),

    TopicDefinition("global_network", "NETZWERK & FUNK", "Netzwerkstrategie", "LAN/WLAN/AP Strategie", "ROOM_NETWORK_OPTIONS", [DOMAIN_IT], True),
    TopicDefinition("global_poe", "NETZWERK & FUNK", "PoE-Planung", "PoE-Versorgung geplant", "YES_MAYBE_NO", [DOMAIN_IT]),
    TopicDefinition("global_coverage", "NETZWERK & FUNK", "WLAN-Abdeckungsziel", "Qualitätsziel je Hausbereich", "COVERAGE_OPTIONS", [DOMAIN_IT], True, 2),
    TopicDefinition("global_protocols", "NETZWERK & FUNK", "Funk-/Bus-Protokolle", "Genutzte Smart-Home-Protokolle", "PROTOCOL_OPTIONS", [DOMAIN_IT, DOMAIN_SMART], True, 3),
    TopicDefinition("global_radio", "NETZWERK & FUNK", "Funkstrategie", "Funknutzung / Stabilitätsplanung", "YES_MAYBE_NO", [DOMAIN_IT, DOMAIN_SMART], False, 3),

    TopicDefinition("global_pv", "ENERGIE & LASTMANAGEMENT", "PV/Monitoring", "PV-Daten in Planung integriert", "YES_MAYBE_NO", [DOMAIN_ELEC, DOMAIN_SMART]),
    TopicDefinition("global_load", "ENERGIE & LASTMANAGEMENT", "Lastmanagement", "Leistungssteuerung vorgesehen", "YES_MAYBE_NO", [DOMAIN_ELEC], True),
    TopicDefinition("global_usv", "ENERGIE & LASTMANAGEMENT", "USV/Notbetrieb", "kritische Systeme absichern", "YES_MAYBE_NO", [DOMAIN_IT, DOMAIN_SMART]),
]

ROOM_TOPICS: List[TopicDefinition] = [
    TopicDefinition("room_control", "ALLGEMEIN", "Bedienkonzept", "Bedienlogik im Raum", "CONTROL_OPTIONS", [DOMAIN_SMART], True),
    TopicDefinition("room_light_logic", "ALLGEMEIN", "Licht-Logik", "Schalt-/Aktorlogik", "LIGHT_LOGIC_OPTIONS", [DOMAIN_SMART, DOMAIN_ELEC], True),
    TopicDefinition("room_automation_level", "ALLGEMEIN", "Automationsgrad", "Gewünschter Automationsumfang", "AUTOMATION_LEVEL_OPTIONS", [DOMAIN_SMART], True, 2),

    TopicDefinition("room_light", "LICHT", "Lichtkonzept", "Lichtarten/Zonen im Raum", "LIGHT_OPTIONS", [DOMAIN_SMART, DOMAIN_ELEC], True),
    TopicDefinition("room_switch", "LICHT", "Schaltpunkte", "Anzahl/Position in Notizen", "YES_MAYBE_NO", [DOMAIN_ELEC]),
    TopicDefinition("room_dimming", "LICHT", "Dimmen", "Dimmfunktion pro Lichtzone", "YES_MAYBE_NO", [DOMAIN_SMART, DOMAIN_ELEC]),

    TopicDefinition("room_heat", "KLIMA", "Heizung/Regelung", "Heiz-/Regelstrategie", "HEAT_OPTIONS", [DOMAIN_SMART, DOMAIN_ELEC], False, 3, ["living", "bedroom", "office", "bathroom", "kitchen"]),
    TopicDefinition("room_climate_sensors", "KLIMA", "Sensorik Klima", "Klima-Sensorik", "SENSOR_OPTIONS", [DOMAIN_SMART], False, 3, ["living", "bedroom", "office", "bathroom", "kitchen"]),
    TopicDefinition("room_air_quality", "KLIMA", "Luftqualität", "CO₂/Luftgüte aktiv überwachen", "YES_MAYBE_NO", [DOMAIN_SMART], False, 3, ["living", "bedroom", "office", "kitchen"]),

    TopicDefinition("room_security", "SICHERHEIT", "Tür/Fenster/Alarm", "Sicherheitsbedarf", "SECURITY_OPTIONS", [DOMAIN_SMART], True),
    TopicDefinition("room_water", "SICHERHEIT", "Wasserleck", "Leckschutzbedarf", "WATER_OPTIONS", [DOMAIN_SMART, DOMAIN_ELEC], False, 3, ["bathroom", "kitchen", "utility"]),
    TopicDefinition("room_camera_storage", "SICHERHEIT", "Kamera-Aufzeichnung", "Wie Kameradaten gespeichert werden", "CAMERA_STORAGE_OPTIONS", [DOMAIN_IT, DOMAIN_SMART], False, 2, ["outdoor", "hallway", "living"]),

    TopicDefinition("room_network", "NETZWERK", "Netzwerk", "LAN/WLAN/PoE im Raum", "ROOM_NETWORK_OPTIONS", [DOMAIN_IT], True),
    TopicDefinition("room_coverage", "NETZWERK", "Netzabdeckung Raum", "Abdeckungsziel pro Raum", "COVERAGE_OPTIONS", [DOMAIN_IT], True, 2),
    TopicDefinition("room_power", "NETZWERK", "Steckdosen & Messung", "Schalt-/Messbedarf", "POWER_OPTIONS", [DOMAIN_ELEC, DOMAIN_SMART]),

    TopicDefinition("room_sensor_general", "AUTOMATIONEN", "Sensorik allgemein", "Automationssensorik", "SENSOR_OPTIONS", [DOMAIN_SMART]),
    TopicDefinition("room_shade", "AUTOMATIONEN", "Beschattung", "Beschattungslogik", "SHADE_OPTIONS", [DOMAIN_SMART, DOMAIN_ELEC], False, 3, ["living", "bedroom", "office", "kitchen"]),
    TopicDefinition("room_scenes", "AUTOMATIONEN", "Szenenbedarf", "Szenen wie Abend/Abwesend/Urlaub", "YES_MAYBE_NO", [DOMAIN_SMART], True),
]


def topic_map(topics: List[TopicDefinition]) -> Dict[str, TopicDefinition]:
    return {t.key: t for t in topics}
