# Smarthome Planungsmappe (Desktop, Offline)

Lokales Desktop-Tool (PySide6) zur Planung von Smart Home / Elektrik / IT je Raum, inklusive Auswertung und Export nach Excel/PDF.

## Features
- Offline, lokale JSON-Projektspeicherung
- Multi-Projekt-Startseite
- Global- und Raumplanung mit strukturierten Sections
- Flexible Mehrfachauswahl pro Topic (ohne Duplikate)
- UX für Mehrfachauswahl: initial 1 Dropdown, weitere per Plus-Button
- Pflichtfeld-Validierung vor Export
- Konfliktchecks + Raum-Ampel-Score
- Export: XLSX und PDF

## Start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

## Datenablage
- Projekte: `data/projects/*.json`
- Projektindex: `data/projects_index.json`


## Erweiterte Planungspunkte (neu)
- Server/Plattform-Auswahl (z. B. Raspberry Pi, Unraid, Proxmox, NAS)
- Home-Assistant-Betriebsart (OS, Container, Supervised, Core)
- Backup-Strategie und Funk-/Bus-Protokolle
- Verdrahtungsart (inkl. Stern-/Misch-/BUS-Ansätzen)
- Zusätzliche Raumdetails: Automationsgrad, Dimmen, Luftqualität, Kamera-Aufzeichnung, Netzabdeckung, Szenenbedarf

## Hinweise
- PDF-Export ist nur im Status `Freigegeben` möglich (Status-Button in der linken Leiste).


## Themenübersicht
- Vollständiger Frage-/Themenkatalog: `docs/THEMENKATALOG.md`
