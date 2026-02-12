# Smarthome Planungsmappe (Desktop, Offline)

Lokales Desktop-Tool (PySide6) zur Planung von Smart Home / Elektrik / IT je Raum, inklusive Auswertung und Export nach Excel/PDF.

## Features
- Offline, lokale JSON-Projektspeicherung
- Multi-Projekt-Startseite
- Global- und Raumplanung mit strukturierten Sections
- Flexible Mehrfachauswahl pro Topic (ohne Duplikate)
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

## Hinweise
- PDF-Export ist nur im Status `Freigegeben` möglich (Status-Button in der linken Leiste).
