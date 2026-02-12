# PyCharm Setup Anleitung

## 1) Projekt öffnen
1. PyCharm starten
2. **Open** wählen
3. Ordner `Planner` auswählen

## 2) Interpreter einrichten
1. `File -> Settings -> Project: Planner -> Python Interpreter`
2. `Add Interpreter -> New Virtualenv`
3. Als Basis Python 3.11+ wählen
4. Erstellen bestätigen

## 3) Abhängigkeiten installieren
Im Terminal in PyCharm:
```bash
pip install -r requirements.txt
```

## 4) Run Configuration anlegen
1. `Run -> Edit Configurations...`
2. `+ -> Python`
3. Name: `Smarthome Planner`
4. Script path: `<projekt>/app/main.py`
5. Working directory: `<projekt root>`
6. Interpreter: zuvor erstellte venv

## 5) App starten
- `Run 'Smarthome Planner'`

## 6) Typischer Workflow
1. Neues Projekt erstellen
2. Global + Räume ausfüllen
3. Status auf `Freigegeben` setzen
4. Excel/PDF exportieren
