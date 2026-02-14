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


## One-File EXE (PyInstaller, inkl. eingebettetem Logo)

### Ziel
Eine **einzige** `Smarthome-Planungsmappe.exe`, bei der das Splash-Logo bereits in der EXE enthalten ist (kein separates `data`-Verzeichnis neben der EXE nötig).

### 1) Build-Umgebung vorbereiten (Windows)
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
```

### 2) Optional: eigenes Splash-Logo ablegen
Lege dein Logo z. B. als `branding/logo.png` im Repo ab.

### 3) One-File bauen (Logo in EXE einbetten)
```bash
pyinstaller --noconfirm --clean --onefile --windowed --name "Smarthome-Planungsmappe" --add-data "branding/logo.png;data" app/main.py
```

Wichtig: Unter Windows ist das Format bei `--add-data` immer `Quelle;Ziel`.

### 4) Ergebnis
Die fertige Datei liegt unter:
- `dist/Smarthome-Planungsmappe.exe`

Diese EXE enthält das Logo intern. Beim Start entpackt PyInstaller intern temporär (unsichtbar für Endnutzer), daher sind **keine dauerhaften Zusatzordner** neben der EXE erforderlich.

### 5) Wie das Logo im Code gefunden wird
Die App sucht beim Splash-Start an mehreren Orten (u. a. One-File `_MEIPASS`) und bevorzugt `logo.png`/`logo.jpg` unter `data/`.
Wenn du wie oben mit `--add-data "branding/logo.png;data"` baust, wird das eingebettete Logo automatisch erkannt.
