# Home Assistant / Smarthome Planungsmappe – Projektvorschlag

## 1) Zielbild

Ein lokal laufendes Windows-Desktop-Tool (PySide6), das die bisherige Excel-Planung digital abbildet und erweitert:

- **Offline-first** (kein Internet erforderlich)
- **Lokale Datenspeicherung** via JSON
- **Komfortable Erfassung im GUI** statt primär in Excel
- **Excel-Export als Backup / Austauschformat**
- **PDF-Export für Gewerke-Abstimmung** (Smart Home / Elektrik / IT)

Zusätzlich wird die Erfassung flexibler als ursprünglich:

- Pro Thema können optional **0 bis 5 Auswahloptionen** gesetzt werden (statt starr max. 3).
- Dadurch sind komplexe Räume/Themen besser abbildbar.
- Inhalte werden so strukturiert, dass sie als **professionelle Planungsunterlage** für Elektriker, IT-/Netzwerkdienstleister und Smart-Home-Integrator nutzbar sind.

---

## 2) UX-/UI-Vorschlag (professionell, klar, wartbar)

### Hauptlayout

- `QMainWindow` mit horizontalem Split:
  - **Links:** Navigation (Baum/Liste)
  - **Rechts:** Inhaltsbereich

### Navigation links

1. Start
2. Global
3. Auswertung
4. Räume
   - EG
     - Wohnzimmer
     - HTR
     - Flur
     - WC EG
     - Büro
   - OG
     - Kinderzimmer 1
     - Kinderzimmer 2
     - Flur
     - Ankleide
     - Schlafzimmer
     - Bad

### Inhaltsbereich rechts

- Seite „Global“ und jede Raumseite als **scrollbare Karten-/GroupBox-Abschnitte**:
  - ALLGEMEIN
  - LICHT
  - KLIMA
  - SICHERHEIT
  - NETZWERK
  - AUTOMATIONEN

### Zeilen-Widget je Thema

Jede Zeile enthält:

- Thema-Name (fett)
- Kurzbeschreibung (read-only)
- **Mehrfachauswahl bis zu 5 Optionen**
  - UX-Variante: 5 Comboboxen (Auswahl 1…5)
  - erste Box sichtbar, weitere über „+ Auswahl hinzufügen“ einblendbar
  - Dubletten werden verhindert
- Notizen (mehrzeilig)
- Tagging/Klassifizierung je Thema für spätere Ausgabe:
  - `SMART_HOME`
  - `ELEKTRIK`
  - `IT_NETZWERK`
  - optional Mehrfach-Tags

### Warum diese UX?

- Visuell klarer als eine große Tabelle
- Kognitiv sauber durch Abschnittstrennung
- Flexibel für einfache und komplexe Themen
- Grundlage für gefilterte, gewerkespezifische Exporte

---

## 3) Fachlicher Qualitätsrahmen (heutiger Standard)

Damit die Planung später von Gewerken direkt genutzt werden kann, werden Themen inhaltlich auf professionellem Niveau dokumentiert.

### Elektrik-Qualität

- Saubere Trennung von Stromkreisen / Lasten / Schutzkonzept
- Dokumentation von FI/RCD-Konzept, Phasen-/Lastverteilung, Anschlussplan
- Stern-/Aktorstrategie klar nachvollziehbar (zentral vs. dezentral)
- Hinweise auf Lastmanagement (z. B. WP/Wallbox)

### IT-/Netzwerk-Qualität

- Netzwerkstrategie je Raum dokumentiert (LAN/WLAN/AP/PoE)
- Geräte mit erhöhtem Bandbreiten-/Verfügbarkeitsbedarf markierbar
- AP- und PoE-Planung pro Raum nachvollziehbar
- Funkstrategie ergänzend zur kabelgebundenen Planung

### Übergabefähigkeit für Gewerke

Die finalen Exporte sollen strukturiert sein für:

1. **Smart Home Integrator** (Automationen, Sensorik, Bedienlogik)
2. **Elektriker** (Schutz, Lasten, Aktoren, Schalt-/Versorgungskonzept)
3. **IT-/Netzwerkdienstleister** (LAN/WLAN/AP/PoE/Topologiehinweise)

---

## 4) Datenmodell (Python Dataclasses)

```text
Project
├── metadata: ProjectMetadata
├── global_topics: dict[str, TopicEntry]
└── rooms: dict[str, Room]

ProjectMetadata
├── project_name: str
├── created_at: str (ISO)
├── updated_at: str (ISO)
└── version: str

Room
├── name: str
├── floor: str (EG/OG)
└── topics: dict[str, TopicEntry]

TopicEntry
├── topic_key: str
├── selections: list[str]   # 0..5 Einträge
├── notes: str
└── domains: list[str]      # SMART_HOME / ELEKTRIK / IT_NETZWERK
```

Validierung:

- `selections` ist optional leer
- maximal 5 Einträge
- keine Duplikate
- `domains` mindestens ein valider Bereich

---

## 5) Vollständige Option-Sets (zentral definiert)

### A) CONTROL_OPTIONS
- Kippschalter (klassisch)
- Taster (Impuls)
- Doppeltaster / Szenentaster
- Drehdimmer
- Wallpanel/Tablet
- Sprachsteuerung (optional)
- App (nur Ergänzung)

### B) LIGHT_OPTIONS
- Nur Grundbeleuchtung
- Zonen (mehrere Lichtkreise)
- Indirekt (LED-Cove/Decke/Wand)
- Direkt (Spots/Downlights)
- Akzentlicht (Regal/Nische)
- RGB (Ambient)
- Tunable White (Warm/Kalt)

### C) LIGHT_LOGIC_OPTIONS
- Aktor im Schaltschrank (Stern)
- Aktor Unterputz (dezentral)
- Smarte Leuchtmittel (Dauerstrom)
- Mischform (Aktor + smarte Lampen)

### D) SENSOR_OPTIONS
- Bewegungsmelder
- Präsenzmelder (mmWave)
- Fensterkontakt
- Türkontakt
- Temperatur
- Luftfeuchte
- CO₂ / Luftqualität
- Helligkeit

### E) HEAT_OPTIONS
- Keine Einzelraumregelung
- Thermostat (Heizkörper)
- FBH (Fußbodenheizung) – Raumregelung
- Fenster-auf-Erkennung
- Zeitprogramm
- Nachtabsenkung / Eco-Modus

### F) SHADE_OPTIONS
- Keine Beschattung
- Manuell
- Zeitgesteuert
- Sonnenstand (Azimut/Höhe)
- Wetter/Windschutz
- Sommer-Hitzeschutz

### G) ROOM_NETWORK_OPTIONS
- LAN-Dose vorhanden
- LAN-Dose optional
- WLAN reicht
- AP in/nahe Raum geplant
- PoE im Raum (z.B. Panel/Kamera)

### H) SECURITY_OPTIONS
- Kein Bedarf
- Fensterkontakte
- Türkontakt
- Alarmmodus (Nacht/Abwesend)
- Sirene/Signalgeber
- Kamera (lokal)

### I) WATER_OPTIONS
- Nicht nötig
- Lecksensor
- Lecksensor + Push-Alarm
- Lecksensor + Absperrventil (optional)

### J) POWER_OPTIONS
- Normale Steckdosen
- Schaltbar (Smart Plug)
- Schaltbar + Messung
- Fester Aktor/Relais + Messung
- Großverbraucher separat messen

### K) YES_MAYBE_NO
- Ja
- Vielleicht
- Nein

### L) GLOBAL_STERN_OPTIONS
- Keine Sternverkabelung (klassisch)
- Teilweise Sternverkabelung
- Komplette Sternverkabelung
- Zentrale Aktoren (Hutschiene)
- Dezentrale Aktoren (UP)

### M) GLOBAL_PHASE_OPTIONS
- Nicht relevant
- 3 Phasen sauber verteilt
- 3 Phasen + Lastmanagement vorgesehen
- Lastmanagement zwingend (WP/Wallbox)

---

## 6) Vollständige Topics (Projektinhalt)

## A) Global_Planung

### ALLGEMEIN
1. Zielsetzung → `YES_MAYBE_NO`  
   Kurzbeschreibung: Fokus Komfort/Energie/Sicherheit/Technik
2. Cloud-Policy → `YES_MAYBE_NO`
3. Dokumentation → `YES_MAYBE_NO`

### ELEKTRIK & SCHALTSCHRANK
4. Sternverkabelung / Aktoren → `GLOBAL_STERN_OPTIONS`
5. Phasen-/Lastverteilung → `GLOBAL_PHASE_OPTIONS`
6. FI/RCD-Konzept → `YES_MAYBE_NO`
7. Anschlussplan → `YES_MAYBE_NO`

### NETZWERK & FUNK
8. Netzwerkstrategie → `ROOM_NETWORK_OPTIONS`
9. PoE-Planung → `YES_MAYBE_NO`
10. Funkstrategie → `YES_MAYBE_NO`

### ENERGIE & LASTMANAGEMENT
11. PV/Monitoring → `YES_MAYBE_NO`
12. Lastmanagement → `YES_MAYBE_NO`
13. USV/Notbetrieb → `YES_MAYBE_NO`

## B) Raumplanung (identisch je Raum)

### ALLGEMEIN
1. Bedienkonzept → `CONTROL_OPTIONS`
2. Licht-Logik → `LIGHT_LOGIC_OPTIONS`

### LICHT
3. Lichtkonzept → `LIGHT_OPTIONS`
4. Schaltpunkte → `YES_MAYBE_NO` (Details in Notizen)

### KLIMA
5. Heizung/Regelung → `HEAT_OPTIONS`
6. Sensorik Klima → `SENSOR_OPTIONS`

### SICHERHEIT
7. Tür/Fenster/Alarm → `SECURITY_OPTIONS`
8. Wasserleck → `WATER_OPTIONS`

### NETZWERK
9. Netzwerk → `ROOM_NETWORK_OPTIONS`
10. Steckdosen & Messung → `POWER_OPTIONS`

### AUTOMATIONEN
11. Sensorik allgemein → `SENSOR_OPTIONS`
12. Beschattung → `SHADE_OPTIONS`

---

## 7) Auswertungskonzept

Seite „Auswertung“ mit 2 Bereichen:

1. **Matrix**
   - Zeilen: Raum-Topics (z. B. „Lichtkonzept“)
   - Spalten: Räume
   - Zelle: kommaseparierte Auswahloptionen (0..5) oder „—“

2. **Kennzahlen je Topic**
   - Räume mit Auswahl (Anzahl / Prozent)
   - Häufigkeitsliste der gewählten Optionen
   - Diversity Score = Anzahl unterschiedlicher Optionen
   - Konsistenzwert = Anteil der häufigsten Option

Alles in Python berechnet (kein Formel-Excel).

---

## 8) Speichern/Laden

- Neues Projekt
- Projekt laden (`*.json`)
- Projekt speichern
- Speichern unter…
- Optional Autosave (debounced, z. B. 1–2 Sekunden nach letzter Änderung)

Robuste Fehlerbehandlung:

- Datei fehlt
- Ungültiges JSON
- Inkompatible Datenversion

---

## 9) Exportstrategie (Excel Pflicht, PDF ergänzt)

### Excel (`openpyxl`) – Pflicht

- Sheet `Global_Planung`
- je Raum ein Sheet
- `Auswertung_Raumvergleich`

Formatierung:

- farbige Kopfzeilen
- Abschnittstitel als gemergte Zeilen
- alternierende Datenzeilen
- gute Spaltenbreiten
- Zeilenumbruch für Notizen

### PDF – Ziel für Gewerke-Übergabe

PDF-Export wird als zusätzlicher, klar priorisierter Baustein aufgenommen:

- Gesamtreport **und** gewerkespezifische Reports
- Filterprofile:
  1. Smart Home
  2. Elektrik
  3. IT/Netzwerk
- Inhalt je Report:
  - Projektmetadaten
  - relevante Global-Themen
  - relevante Raum-Themen
  - offene Punkte / Notizen
  - priorisierte To-dos (optional)

Technisch pragmatischer Ansatz:

1. zunächst HTML-Template + PDF-Rendering (z. B. WeasyPrint) oder ReportLab
2. später Layout-Polish (Logo, Deckblatt, Inhaltsverzeichnis)

---

## 10) Projektstruktur

```text
/app
  main.py
  ui/
    main_window.py
    navigation.py
    pages/
      start_page.py
      global_page.py
      room_page.py
      evaluation_page.py
    widgets/
      topic_card.py
      topic_row_widget.py
  models/
    project.py
    definitions.py
  services/
    storage.py
    export_excel.py
    export_pdf.py
    evaluation.py
  resources/
    (optional)
requirements.txt
README.md
```

---

## 11) Empfohlener nächster Schritt

Wenn dieser Blueprint passt, folgt als nächstes die Implementierung in 3 Wellen:

1. **MVP lauffähig:** UI + JSON + Auswertung + Excel-Export
2. **Gewerke-Output:** PDF-Export (gesamt + Smart Home/Elektrik/IT-Filter)
3. **Polish:** Autosave, UI-Feinschliff, Import (optional), Worker-Export mit Fortschritt

Damit bekommst du schnell ein nutzbares Tool und danach eine wirklich professionelle, vorlagefähige Dokumentation für alle beteiligten Gewerke.
