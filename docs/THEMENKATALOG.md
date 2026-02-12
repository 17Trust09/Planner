# Vordefinierter Themenkatalog (Global + Raum)

Dieser Katalog zeigt transparent, welche Fragen/Themen aktuell im Tool vordefiniert abgefragt werden.

## A) Global_Planung (hausweite Leitplanken)

### ALLGEMEIN
1. Zielsetzung — Option Set: `YES_MAYBE_NO`
2. Cloud-Policy — Option Set: `YES_MAYBE_NO`
3. Dokumentation — Option Set: `YES_MAYBE_NO`
4. Raumnutzungsprofil — Option Set: `ROOM_ROLE_OPTIONS`

### SERVER & PLATTFORM
5. Server-Hardware — Option Set: `SERVER_OPTIONS` (inkl. Raspberry Pi, Unraid, Proxmox etc.)
6. Home-Assistant-Betriebsart — Option Set: `HA_OS_OPTIONS`
7. Backup-Strategie — Option Set: `BACKUP_OPTIONS`

### VERDRAHTUNG & ELEKTRIK
8. Sternverkabelung / Aktoren — Option Set: `GLOBAL_STERN_OPTIONS`
9. Verdrahtungsart — Option Set: `CABLE_OPTIONS`
10. Phasen-/Lastverteilung — Option Set: `GLOBAL_PHASE_OPTIONS`
11. FI/RCD-Konzept — Option Set: `YES_MAYBE_NO`
12. Anschlussplan — Option Set: `YES_MAYBE_NO`

### NETZWERK & FUNK
13. Netzwerkstrategie — Option Set: `ROOM_NETWORK_OPTIONS`
14. PoE-Planung — Option Set: `YES_MAYBE_NO`
15. WLAN-Abdeckungsziel — Option Set: `COVERAGE_OPTIONS`
16. Funk-/Bus-Protokolle — Option Set: `PROTOCOL_OPTIONS`
17. Funkstrategie — Option Set: `YES_MAYBE_NO`

### ENERGIE & LASTMANAGEMENT
18. PV/Monitoring — Option Set: `YES_MAYBE_NO`
19. Lastmanagement — Option Set: `YES_MAYBE_NO`
20. USV/Notbetrieb — Option Set: `YES_MAYBE_NO`

---

## B) Raumplanung (pro Raum identisch)

### ALLGEMEIN
1. Bedienkonzept — Option Set: `CONTROL_OPTIONS`
2. Licht-Logik — Option Set: `LIGHT_LOGIC_OPTIONS`
3. Automationsgrad — Option Set: `AUTOMATION_LEVEL_OPTIONS`

### LICHT
4. Lichtkonzept — Option Set: `LIGHT_OPTIONS`
5. Schaltpunkte — Option Set: `YES_MAYBE_NO`
6. Dimmen — Option Set: `YES_MAYBE_NO`

### KLIMA
7. Heizung/Regelung — Option Set: `HEAT_OPTIONS`
8. Sensorik Klima — Option Set: `SENSOR_OPTIONS`
9. Luftqualität — Option Set: `YES_MAYBE_NO`

### SICHERHEIT
10. Tür/Fenster/Alarm — Option Set: `SECURITY_OPTIONS`
11. Wasserleck — Option Set: `WATER_OPTIONS`
12. Kamera-Aufzeichnung — Option Set: `CAMERA_STORAGE_OPTIONS`

### NETZWERK
13. Netzwerk — Option Set: `ROOM_NETWORK_OPTIONS`
14. Netzabdeckung Raum — Option Set: `COVERAGE_OPTIONS`
15. Steckdosen & Messung — Option Set: `POWER_OPTIONS`

### AUTOMATIONEN
16. Sensorik allgemein — Option Set: `SENSOR_OPTIONS`
17. Beschattung — Option Set: `SHADE_OPTIONS`
18. Szenenbedarf — Option Set: `YES_MAYBE_NO`

---

## Hinweise zur Eingabe
- Jede Frage ist vordefiniert (Thema + Kurzbeschreibung + Option Set).
- Mehrfachauswahl ist auf **max. 3** begrenzt.
- UX: Start mit **einem** Dropdown, weitere per **Plus-Button**.
- Notizen sind frei erfassbar.
- Global und Raum sind klar getrennt.
