from __future__ import annotations

from typing import Dict

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.project import Project
from app.services.pricing import default_pricing_settings, merged_pricing_settings


FIELD_DEFS = [
    ("cat7_per_meter", "CAT7 Kabel €/m"),
    ("lan_termination_per_run", "LAN-Abschluss je Kabelweg"),
    ("indoor_ap", "Indoor Access Point"),
    ("outdoor_ap", "Outdoor Access Point"),
    ("outdoor_camera", "Außenkamera"),
    ("outdoor_doorbell", "Smarte Türklingel"),
    ("sensor_standard", "Sensorik Standard je Auswahl"),
    ("switch_poe_8", "PoE-Switch 8 Port"),
    ("switch_poe_16", "PoE-Switch 16 Port"),
    ("switch_poe_24", "PoE-Switch 24 Port"),
    ("switch_poe_48", "PoE-Switch 48 Port"),
    ("switch_non_poe_8", "Non-PoE Switch 8 Port"),
    ("switch_non_poe_16", "Non-PoE Switch 16 Port"),
    ("switch_non_poe_24", "Non-PoE Switch 24 Port"),
    ("switch_non_poe_48", "Non-PoE Switch 48 Port"),
    ("router_upgrade", "Router Upgrade"),
    ("router_new", "Router Neuanschaffung"),
    ("router_provider_plus_own", "Provider + eigener Router"),
    ("server_raspberry_pi", "Server: Raspberry Pi"),
    ("server_intel_nuc", "Server: Intel NUC / Mini-PC"),
    ("server_unraid", "Server: Unraid"),
    ("server_proxmox", "Server: Proxmox"),
    ("server_nas", "Server: NAS"),
    ("server_ha_green_yellow", "Server: HA Green/Yellow"),
]


class PricingPage(QWidget):
    changed = Signal()

    def __init__(self, project: Project):
        super().__init__()
        self.project = project
        self.range_inputs: Dict[str, tuple[QLineEdit, QLineEdit, QLineEdit]] = {}

        root = QVBoxLayout(self)
        head = QHBoxLayout()
        head.addWidget(QLabel("<h2>Preise & Preisprofile</h2>"))
        help_btn = QPushButton("?")
        help_btn.setObjectName("helpButton")
        help_btn.setFixedWidth(28)
        help_btn.clicked.connect(self._show_help)
        head.addStretch()
        head.addWidget(help_btn)
        root.addLayout(head)
        root.addWidget(QLabel("Hier kannst du Min/Typ/Max-Preisbereiche pflegen und die Switch-Strategie beeinflussen."))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        body_layout = QVBoxLayout(body)

        base_box = QGroupBox("Basisannahmen")
        base_form = QFormLayout(base_box)
        self.meters_per_run = QLineEdit()
        self.switch_split_threshold_ports = QLineEdit()
        self.switch_split_poe_ratio = QLineEdit()
        for w in [self.meters_per_run, self.switch_split_threshold_ports, self.switch_split_poe_ratio]:
            w.textChanged.connect(self.changed.emit)

        base_form.addRow("CAT7 Meter je Kabelweg", self.meters_per_run)
        base_form.addRow("Switch-Split ab Portanzahl", self.switch_split_threshold_ports)
        base_form.addRow("Switch-Split ab PoE-Anteil (0.0-1.0)", self.switch_split_poe_ratio)
        body_layout.addWidget(base_box)

        range_box = QGroupBox("Preisbereiche (Min / Typisch / Max)")
        range_layout = QVBoxLayout(range_box)
        for key, label in FIELD_DEFS:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            min_edit = QLineEdit()
            min_edit.setPlaceholderText("min")
            typ_edit = QLineEdit()
            typ_edit.setPlaceholderText("typisch")
            max_edit = QLineEdit()
            max_edit.setPlaceholderText("max")
            for w in [min_edit, typ_edit, max_edit]:
                w.setFixedWidth(90)
                w.textChanged.connect(self.changed.emit)
                row.addWidget(w)
            row.addStretch()
            range_layout.addLayout(row)
            self.range_inputs[key] = (min_edit, typ_edit, max_edit)

        body_layout.addWidget(range_box)
        body_layout.addStretch()
        scroll.setWidget(body)
        root.addWidget(scroll)

        self._load_from_project()

    def _show_help(self) -> None:
        QMessageBox.information(
            self,
            "Hilfe: Preise",
            "Du kannst hier alle Preisbänder anpassen.\n"
            "Min/Typ/Max wird direkt in der Kosten-Auswertung verwendet.\n"
            "Bei hoher Portlast oder hohem PoE-Anteil kann automatisch ein Split in PoE- und Non-PoE-Switch erfolgen.",
        )

    def _load_from_project(self) -> None:
        cfg = merged_pricing_settings(self.project)
        self.meters_per_run.setText(str(cfg["meters_per_run"]))
        self.switch_split_threshold_ports.setText(str(cfg["switch_split_threshold_ports"]))
        self.switch_split_poe_ratio.setText(str(cfg["switch_split_poe_ratio"]))

        for key, edits in self.range_inputs.items():
            v = cfg["ranges"][key]
            edits[0].setText(str(v["min"]))
            edits[1].setText(str(v["typical"]))
            edits[2].setText(str(v["max"]))

    def persist(self) -> None:
        defaults = default_pricing_settings()
        new_settings = {
            "meters_per_run": self.meters_per_run.text().strip() or defaults["meters_per_run"],
            "switch_split_threshold_ports": self.switch_split_threshold_ports.text().strip() or defaults["switch_split_threshold_ports"],
            "switch_split_poe_ratio": self.switch_split_poe_ratio.text().strip() or defaults["switch_split_poe_ratio"],
            "ranges": {},
        }

        for key, edits in self.range_inputs.items():
            fallback = defaults["ranges"][key]
            new_settings["ranges"][key] = {
                "min": edits[0].text().strip() or fallback["min"],
                "typical": edits[1].text().strip() or fallback["typical"],
                "max": edits[2].text().strip() or fallback["max"],
            }

        self.project.pricing_settings = new_settings
