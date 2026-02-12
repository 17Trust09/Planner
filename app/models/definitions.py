from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


FLOORS: Dict[str, List[str]] = {
    "EG": ["Wohnzimmer", "HTR", "Flur EG", "WC EG", "Büro"],
    "OG": ["Kinderzimmer 1", "Kinderzimmer 2", "Flur OG", "Ankleide", "Schlafzimmer", "Bad"],
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
    max_selections: int = 5


GLOBAL_TOPICS: List[TopicDefinition] = [
    TopicDefinition("global_goal", "ALLGEMEIN", "Zielsetzung", "Fokus Komfort/Energie/Sicherheit/Technik", "YES_MAYBE_NO", [DOMAIN_SMART], True),
    TopicDefinition("global_cloud", "ALLGEMEIN", "Cloud-Policy", "Cloud-Nutzung gewünscht oder vermeiden", "YES_MAYBE_NO", [DOMAIN_SMART, DOMAIN_IT]),
    TopicDefinition("global_docs", "ALLGEMEIN", "Dokumentation", "Planung und Änderungen dokumentieren", "YES_MAYBE_NO", [DOMAIN_SMART, DOMAIN_ELEC, DOMAIN_IT], True),
    TopicDefinition("global_stern", "ELEKTRIK & SCHALTSCHRANK", "Sternverkabelung / Aktoren", "Zentrale/dezentrale Strategie", "GLOBAL_STERN_OPTIONS", [DOMAIN_ELEC], True),
    TopicDefinition("global_phase", "ELEKTRIK & SCHALTSCHRANK", "Phasen-/Lastverteilung", "Belastung und Lastmanagement", "GLOBAL_PHASE_OPTIONS", [DOMAIN_ELEC], True),
    TopicDefinition("global_fi", "ELEKTRIK & SCHALTSCHRANK", "FI/RCD-Konzept", "Schutzkonzept abgestimmt", "YES_MAYBE_NO", [DOMAIN_ELEC], True),
    TopicDefinition("global_anschluss", "ELEKTRIK & SCHALTSCHRANK", "Anschlussplan", "Anschluss-/Klemmenplan vorhanden", "YES_MAYBE_NO", [DOMAIN_ELEC], True),
    TopicDefinition("global_network", "NETZWERK & FUNK", "Netzwerkstrategie", "LAN/WLAN/AP Strategie", "ROOM_NETWORK_OPTIONS", [DOMAIN_IT], True),
    TopicDefinition("global_poe", "NETZWERK & FUNK", "PoE-Planung", "PoE-Versorgung geplant", "YES_MAYBE_NO", [DOMAIN_IT]),
    TopicDefinition("global_radio", "NETZWERK & FUNK", "Funkstrategie", "Zigbee/Thread/WLAN Positionierung", "YES_MAYBE_NO", [DOMAIN_IT, DOMAIN_SMART]),
    TopicDefinition("global_pv", "ENERGIE & LASTMANAGEMENT", "PV/Monitoring", "PV-Daten in Planung integriert", "YES_MAYBE_NO", [DOMAIN_ELEC, DOMAIN_SMART]),
    TopicDefinition("global_load", "ENERGIE & LASTMANAGEMENT", "Lastmanagement", "Leistungssteuerung vorgesehen", "YES_MAYBE_NO", [DOMAIN_ELEC], True),
    TopicDefinition("global_usv", "ENERGIE & LASTMANAGEMENT", "USV/Notbetrieb", "kritische Systeme absichern", "YES_MAYBE_NO", [DOMAIN_IT, DOMAIN_SMART]),
]

ROOM_TOPICS: List[TopicDefinition] = [
    TopicDefinition("room_control", "ALLGEMEIN", "Bedienkonzept", "Bedienlogik im Raum", "CONTROL_OPTIONS", [DOMAIN_SMART], True),
    TopicDefinition("room_light_logic", "ALLGEMEIN", "Licht-Logik", "Schalt-/Aktorlogik", "LIGHT_LOGIC_OPTIONS", [DOMAIN_SMART, DOMAIN_ELEC], True),
    TopicDefinition("room_light", "LICHT", "Lichtkonzept", "Lichtarten/Zonen im Raum", "LIGHT_OPTIONS", [DOMAIN_SMART, DOMAIN_ELEC], True),
    TopicDefinition("room_switch", "LICHT", "Schaltpunkte", "Anzahl/Position in Notizen", "YES_MAYBE_NO", [DOMAIN_ELEC]),
    TopicDefinition("room_heat", "KLIMA", "Heizung/Regelung", "Heiz-/Regelstrategie", "HEAT_OPTIONS", [DOMAIN_SMART, DOMAIN_ELEC]),
    TopicDefinition("room_climate_sensors", "KLIMA", "Sensorik Klima", "Klima-Sensorik", "SENSOR_OPTIONS", [DOMAIN_SMART]),
    TopicDefinition("room_security", "SICHERHEIT", "Tür/Fenster/Alarm", "Sicherheitsbedarf", "SECURITY_OPTIONS", [DOMAIN_SMART], True),
    TopicDefinition("room_water", "SICHERHEIT", "Wasserleck", "Leckschutzbedarf", "WATER_OPTIONS", [DOMAIN_SMART, DOMAIN_ELEC]),
    TopicDefinition("room_network", "NETZWERK", "Netzwerk", "LAN/WLAN/PoE im Raum", "ROOM_NETWORK_OPTIONS", [DOMAIN_IT], True),
    TopicDefinition("room_power", "NETZWERK", "Steckdosen & Messung", "Schalt-/Messbedarf", "POWER_OPTIONS", [DOMAIN_ELEC, DOMAIN_SMART]),
    TopicDefinition("room_sensor_general", "AUTOMATIONEN", "Sensorik allgemein", "Automationssensorik", "SENSOR_OPTIONS", [DOMAIN_SMART]),
    TopicDefinition("room_shade", "AUTOMATIONEN", "Beschattung", "Beschattungslogik", "SHADE_OPTIONS", [DOMAIN_SMART, DOMAIN_ELEC]),
]


def topic_map(topics: List[TopicDefinition]) -> Dict[str, TopicDefinition]:
    return {t.key: t for t in topics}
