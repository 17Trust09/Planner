# Final Scope Decisions (Brainstorming Ergebnis)

Stand: bestätigt im Chat

## 1) Scope & Prioritäten

1. **PDF-Export im MVP**: Ja, direkt in der ersten Version.
2. **MVP-Fokus**: Qualität/Prüfregeln vor „nur schnell nutzbar“.
3. **Projektverwaltung**: Mehrere Projekte von Anfang an.

---

## 2) Datenerfassung / Eingabelogik

4. **Anzahl Auswahlen pro Topic**: Flexibel pro Topic konfigurierbar (nicht starr 5).
5. **Doppelte Auswahlen**: Strikt verhindern.
6. **Pflichtfelder vor Export**: Ja, Export nur bei erfüllten Mindestdaten.

---

## 3) Gewerke-Übergabe

7. **Topic-Zuordnung**: Im MVP mit Domains pro Thema:
   - Smart Home
   - Elektrik
   - IT/Netzwerk
   (Mehrfachzuordnung erlaubt)
8. **Freigabe-Status**: Ja, mit Workflow:
   - Entwurf
   - Prüfung
   - Freigegeben
9. **Verantwortliche pro Thema**: Ja (z. B. Elektriker, IT, Integrator).

---

## 4) Auswertung & Qualität

10. **Auswertung im MVP**: Matrix + Kennzahlen + Konfliktchecks.
11. **Konfliktchecks**: Breiter Satz, nicht nur Einzelbeispiele („alle wichtigen“).
12. **Raum-Score**: Ja, Ampel (grün/gelb/rot) für Vollständigkeit/Konsistenz.

---

## 5) Export-Design

13. **PDF-Look**: Repräsentativ (mit Deckblatt/CI-Charakter), nicht nur nüchtern.
14. **Offene-Punkte-Liste**: Ja, inkl. Priorität + Verantwortlichem.
15. **Änderungsvergleich**: Ja, spätere Exporte sollen Delta zur Vorversion zeigen.

---

## 6) Abgeleitete Umsetzungsrichtlinien

- **Validation-First**: Zentrale Validierungsengine mit sofortigen UI-Hinweisen.
- **Release-Gating**: Export (v. a. PDF) standardmäßig nur ab Status „Freigegeben“.
- **Multi-Project-UX**: Startseite mit Projektliste, Suche und Schnellaktionen.
- **Reporting-Engine**: Gewerkefilter + Konfliktliste + Verantwortlichkeiten.
- **Versioning**: Projekt-/Export-Versionen, um Änderungsvergleiche sauber zu ermöglichen.

