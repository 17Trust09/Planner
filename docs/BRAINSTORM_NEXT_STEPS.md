# Brainstorming-Checkliste – nächste Planungsrunde

Diese Liste dient als strukturierter Check, bevor wir vom Konzept in die Umsetzung gehen.

## 1) Muss-Entscheidungen vor Coding-Start

1. **Mehrfachauswahl final bestätigen**
   - Aktuell geplant: 0 bis 5 Optionen pro Topic
   - Frage: Soll die maximale Anzahl je Topic konfigurierbar sein (z. B. 3/5/8)?

2. **Pflichtfelder definieren**
   - Welche Topics müssen zwingend ausgefüllt sein, bevor Export erlaubt ist?
   - Vorschlag: Global (Sternverkabelung, Lastverteilung, Netzwerkstrategie) + je Raum (Lichtkonzept, Netzwerk)

3. **Freigabeprozess für Gewerke-Export**
   - Braucht es einen Status wie `Entwurf`, `Prüfung`, `Freigegeben`?
   - Soll PDF nur bei Status `Freigegeben` erstellt werden dürfen?

4. **Prioritätenkennzeichnung**
   - Sollen Topics Priorität erhalten (Hoch / Mittel / Niedrig)?
   - Vorteil: bessere Umsetzungsreihenfolge für Elektriker/IT

---

## 2) Inhalte, die fachlich noch ergänzt werden könnten

## Smart Home

- Szenen-/Use-Case-Katalog pro Raum (z. B. „Abend“, „Abwesend“, „Reinigung“)
- Fallback-Verhalten bei Systemausfall (manuell weiterhin bedienbar?)
- Lokale vs. cloudbasierte Automationsanteile transparent markieren

## Elektrik

- Reserveplanung explizit je Schaltschrankfeld (freie TE, Reservekreise)
- Kritische Verbraucher markieren (Wallbox, WP, Server, USV)
- Wartungs-/Service-Hinweise als eigener Notizblock

## IT / Netzwerk

- VLAN-/Segmentierungsbedarf dokumentierbar (optional)
- Abdeckungskarte WLAN (Sollqualität je Raum)
- Kritische Netzwerkgeräte markieren (AP, Kamera, NAS, NVR)

---

## 3) UX-Feinschliff, der den Unterschied macht

1. **Schnellfilter im UI**
   - Nur offene Punkte anzeigen
   - Nur Elektrik / nur IT / nur Smart Home

2. **Konflikthinweise in Echtzeit**
   - Beispiel: „PoE geplant“, aber kein Netzwerkpunkt ausgewählt
   - Beispiel: „Beschattung automatisch“, aber keine Sensorik gewählt

3. **Konsistenz-Score pro Raum**
   - Ampelindikator (grün/gelb/rot)
   - Hilft direkt zu sehen, wo Planung noch lückenhaft ist

4. **Notizen mit Struktur**
   - Freitext plus optionale Tags (`ToDo`, `Risiko`, `Abhängigkeit`)

---

## 4) Exportqualität (Excel + PDF) für professionelle Übergabe

1. **Deckblatt in PDF**
   - Projektname, Adresse/Bauvorhaben, Stand, Version, Ansprechpartner

2. **Gewerkeblöcke klar trennen**
   - Smart Home
   - Elektrik
   - IT/Netzwerk

3. **Offene Punkte-Liste am Ende**
   - nach Priorität sortiert
   - mit Verantwortlichkeit (Bauherr / Elektriker / IT / Integrator)

4. **Versionsvergleich (optional, sehr nützlich)**
   - Was hat sich seit letzter Exportversion geändert?

---

## 5) Technische Entscheidungen (jetzt klären, später Aufwand sparen)

1. **PDF-Technologie**
   - WeasyPrint (HTML/CSS-basiert, sehr flexibel)
   - ReportLab (direkt in Python, präzise steuerbar)

2. **Autosave-Strategie**
   - Debounced Autosave (1–2 Sekunden)
   - plus manuelles Speichern

3. **Dateiversionierung im JSON**
   - Feld `schema_version`
   - spätere Migrationslogik von Anfang an vorbereiten

4. **Validierungs-Engine**
   - zentrale Regeln in `services/validation.py`
   - UI zeigt sofort verständliche Hinweise

---

## 6) Konkrete Fragen an dich (für den finalen Scope)

1. Soll der erste MVP bereits einen **vollen PDF-Export** enthalten oder reicht zuerst Excel + PDF als Phase 2?
2. Möchtest du eine **Statuslogik** (`Entwurf` / `Freigegeben`) für Exporte?
3. Sollen wir **Prioritäten + Verantwortliche** pro Topic direkt mit aufnehmen?
4. Willst du im MVP schon **Plausibilitätsregeln/Konfliktchecks** in der UI?
5. Soll das Tool von Beginn an **mehrere Projekte** in einer Liste verwalten können?

---

## 7) Vorschlag für den nächsten Schritt

Wenn du diese 6 Fragen kurz beantwortest, kann ich danach direkt:

1. den finalen Scope fixieren,
2. die konkrete Dateistruktur + Klassen planen,
3. und anschließend die lauffähige PySide6-MVP-Implementierung starten.

