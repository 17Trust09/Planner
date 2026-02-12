# Projektvorstellung: Home Assistant / Smarthome Planungsmappe (Desktop, Offline)

## Kurzüberblick

Das Tool wird als **lokale Windows-Desktop-Anwendung mit PySide6** umgesetzt und ersetzt die primäre Arbeit in Excel durch eine professionelle, strukturierte Planungsoberfläche.

Kernziele:

- Offline nutzbar, lokale Speicherung als JSON
- Zentral gepflegte Themen für **Global_Planung**, **Raumplanung** und **Auswertung**
- Mehrfachauswahl pro Thema (0 bis 5 Optionen) + Freitext-Notizen
- Export in **Excel (Pflicht)** und später **PDF (gewerkespezifisch)**
- Aufbereitung für Übergabe an Smart-Home-, Elektrik- und IT-Gewerke

---

## Was das Projekt konkret beinhaltet

## 1) Bereiche im Tool

1. **Start**
   - Projektname, Kurzstatus, letzte Änderungen
   - Schnellaktionen: Neues Projekt, Laden, Speichern, Export

2. **Global**
   - Hausweite Leitplanken, z. B. Sternverkabelung, Lastmanagement, Netzwerkstrategie

3. **Räume (EG/OG)**
   - Je Raum gleiche Struktur:
     - ALLGEMEIN
     - LICHT
     - KLIMA
     - SICHERHEIT
     - NETZWERK
     - AUTOMATIONEN

4. **Auswertung**
   - Matrixvergleich über alle Räume
   - Kennzahlen pro Topic (Abdeckung, Häufigkeit, Konsistenz, Diversity)

---

## 2) Inhalte: Option-Sets + Topics

Alle Option-Sets (A–M) und alle Pflicht-Topics sind vollständig definiert und zentral gehalten, damit die Anwendung konsistent bleibt.

- Bedienkonzept, Lichtkonzept, Licht-Logik
- Sensorik, Heizung/Klima, Beschattung
- Netzwerk, Sicherheit, Wasserleck, Steckdosen/Messung
- Global: Stern-/Aktorstrategie, Phasen-/Lastverteilung, FI/RCD usw.

Details siehe vollständiger Blueprint:

- `docs/PROJECT_BLUEPRINT.md`

---

## 3) Daten- und Exportstrategie

### Speichern/Laden

- Projektdatei als JSON
- Funktionen: Neu, Laden, Speichern, Speichern unter
- Fehlerbehandlung bei ungültigen/fehlenden Dateien

### Export

1. **Excel (Pflicht)**
   - Global-Sheet
   - je Raum ein Sheet
   - Raumvergleich als separates Sheet
   - professionelles Layout (Headerfarben, Abschnittszeilen, Spaltenbreiten)

2. **PDF (Ziel, gewerkefähig)**
   - Gesamtbericht
   - gefilterte Berichte nach Smart Home, Elektrik, IT/Netzwerk

---

## 4) UX-Konzept (wie es sich anfühlen soll)

- Linke Navigation + großer Inhaltsbereich rechts
- GroupBoxes/Karten mit klaren Überschriften
- Pro Topic kompakte Zeile mit:
  - Titel + Beschreibung
  - bis zu 5 Auswahlfelder
  - Notizfeld
- Ausreichend Weißraum, klare Typografie, gute Lesbarkeit

---

## 5) Technische Struktur (für PyCharm)

```text
/app
  main.py
  ui/
  models/
  services/
requirements.txt
README.md
```

Detailliert ausgearbeitet in:
- `docs/PROJECT_BLUEPRINT.md`

---

## 6) Umsetzungsvorschlag in Phasen

1. MVP: UI + JSON + Auswertung + Excel-Export
2. Gewerkereporting: PDF-Export + Filterprofile
3. Polish: Autosave, UI-Feinschliff, optional Import

