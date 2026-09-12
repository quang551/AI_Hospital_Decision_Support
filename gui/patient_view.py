# gui/patient_view.py

import sqlite3

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QSpinBox,
    QHeaderView,
    QFrame,
    QMessageBox,
)

from models.patient import Patient
from database.repository import PatientRepository

from knowledge.facts import extract_facts_from_patient
from knowledge.rules import get_default_knowledge_base
from knowledge.inference_engine import InferenceEngine


# ============================================================
# PALETTE
# ============================================================

BG_MAIN = "#F8FAFC"
CARD_BG = "#FFFFFF"
BORDER_COLOR = "#E2E8F0"
TEXT_PRIMARY = "#0F172A"
TEXT_MUTED = "#64748B"

PRIMARY_BLUE = "#2563EB"
PRIMARY_LIGHT = "#EFF6FF"

DANGER = "#DC2626"
DANGER_LIGHT = "#FEF2F2"
DANGER_BORDER = "#FECACA"

COLOR_CRITICAL_BG = "#FEE2E2"
COLOR_CRITICAL_TEXT = "#EF4444"

COLOR_HIGH_BG = "#FFEDD5"
COLOR_HIGH_TEXT = "#EA580C"

COLOR_MEDIUM_BG = "#FEF9C3"
COLOR_MEDIUM_TEXT = "#CA8A04"

COLOR_LOW_BG = "#DCFCE7"
COLOR_LOW_TEXT = "#16A34A"


# ============================================================
# PRIORITY BADGE
# ============================================================

def create_priority_badge(text, level):
    level_str = str(level or "LOW").upper()

    if "CRITICAL" in level_str:
        bg, fg = COLOR_CRITICAL_BG, COLOR_CRITICAL_TEXT
    elif "HIGH" in level_str:
        bg, fg = COLOR_HIGH_BG, COLOR_HIGH_TEXT
    elif "MEDIUM" in level_str:
        bg, fg = COLOR_MEDIUM_BG, COLOR_MEDIUM_TEXT
    else:
        bg, fg = COLOR_LOW_BG, COLOR_LOW_TEXT

    container = QWidget()

    layout = QHBoxLayout(container)
    layout.setContentsMargins(4, 2, 4, 2)
    layout.setAlignment(Qt.AlignCenter)

    label = QLabel(str(text or "LOW"))
    label.setAlignment(Qt.AlignCenter)
    label.setFont(QFont("Segoe UI", 9, QFont.Bold))
    label.setFixedHeight(26)

    label.setStyleSheet(
        f"""
        QLabel {{
            background-color: {bg};
            color: {fg};
            border-radius: 7px;
            padding: 0 12px;
            border: none;
        }}
        """
    )

    layout.addWidget(label)

    return container


# ============================================================
# PATIENT VIEW
# ============================================================

class PatientView(QWidget):

    patient_added = Signal(str)

    def __init__(self, database=None, parent=None):
        super().__init__(parent)

        self.db = (
            database
            if database is not None
            else PatientRepository()
        )

        self.setStyleSheet(
            f"background-color: {BG_MAIN};"
        )

        self.setup_ui()

    # ========================================================
    # MESSAGE BOX
    # ========================================================

    def show_message(
        self,
        title,
        message,
        icon=QMessageBox.Information,
        buttons=QMessageBox.Ok,
        default_button=QMessageBox.Ok,
    ):

        msg = QMessageBox(self)

        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(message)

        msg.setStandardButtons(buttons)
        msg.setDefaultButton(default_button)

        msg.setStyleSheet(
            f"""
            QMessageBox {{
                background-color: white;
            }}

            QMessageBox QLabel {{
                color: {TEXT_PRIMARY};
                background-color: white;
            }}

            QMessageBox QPushButton {{
                color: {TEXT_PRIMARY};
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 16px;
                min-width: 60px;
            }}

            QMessageBox QPushButton:hover {{
                background-color: #E2E8F0;
            }}

            QMessageBox QPushButton:pressed {{
                background-color: #CBD5E1;
            }}
            """
        )

        return msg.exec()

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            24, 20, 24, 24
        )

        main_layout.setSpacing(16)

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(3)

        title = QLabel("Patient Management")

        title.setFont(
            QFont("Segoe UI", 20, QFont.Bold)
        )

        title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; border: none;"
        )

        subtitle = QLabel(
            "Add patients, monitor priority levels, "
            "and manage patient records."
        )

        subtitle.setFont(
            QFont("Segoe UI", 10)
        )

        subtitle.setStyleSheet(
            f"color: {TEXT_MUTED}; border: none;"
        )

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        header.addLayout(title_box)
        header.addStretch()

        refresh = QPushButton("Refresh")

        refresh.setFixedHeight(38)
        refresh.setCursor(Qt.PointingHandCursor)

        refresh.setStyleSheet(
            f"""
            QPushButton {{
                background: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 0 16px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background: {PRIMARY_LIGHT};
                border-color: #93C5FD;
                color: {PRIMARY_BLUE};
            }}
            """
        )

        refresh.clicked.connect(
            self.load_patients
        )

        header.addWidget(refresh)

        main_layout.addLayout(header)

        # ----------------------------------------------------
        # CONTENT
        # ----------------------------------------------------

        body = QHBoxLayout()
        body.setSpacing(16)

        # ====================================================
        # ADD PATIENT CARD
        # ====================================================

        form_card = QFrame()

        form_card.setFixedWidth(310)

        form_card.setStyleSheet(
            f"""
            QFrame {{
                background: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 12px;
            }}
            """
        )

        form = QVBoxLayout(form_card)

        form.setContentsMargins(
            18, 18, 18, 18
        )

        form.setSpacing(10)

        form_title = QLabel("Add Patient")

        form_title.setFont(
            QFont("Segoe UI", 14, QFont.Bold)
        )

        form_title.setStyleSheet(
            f"color: {TEXT_PRIMARY}; border: none;"
        )

        form.addWidget(form_title)

        form_note = QLabel(
            "Enter the patient information below."
        )

        form_note.setFont(
            QFont("Segoe UI", 9)
        )

        form_note.setStyleSheet(
            f"color: {TEXT_MUTED}; border: none;"
        )

        form_note.setWordWrap(True)

        form.addWidget(form_note)

        form.addSpacing(5)

        # Patient ID

        form.addWidget(
            self.create_label("Patient ID *")
        )

        self.txt_code = QLineEdit()

        self.txt_code.setPlaceholderText(
            "e.g. P008"
        )

        form.addWidget(
            self.style_input(self.txt_code)
        )

        # Full name

        form.addWidget(
            self.create_label("Full Name *")
        )

        self.txt_name = QLineEdit()

        self.txt_name.setPlaceholderText(
            "Enter full name"
        )

        form.addWidget(
            self.style_input(self.txt_name)
        )

        # Age

        form.addWidget(
            self.create_label("Age *")
        )

        self.spin_age = QSpinBox()

        self.spin_age.setRange(
            1, 120
        )

        self.spin_age.setValue(25)

        form.addWidget(
            self.style_input(self.spin_age)
        )

        # Symptoms

        form.addWidget(
            self.create_label("Symptoms")
        )

        self.txt_symptoms = QLineEdit()

        self.txt_symptoms.setPlaceholderText(
            "e.g. fever, shortness_of_breath"
        )

        form.addWidget(
            self.style_input(self.txt_symptoms)
        )

        # Severity / Emergency

        levels = [
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL"
        ]

        combo_row = QHBoxLayout()
        combo_row.setSpacing(8)

        level_box = QVBoxLayout()
        level_box.setSpacing(5)

        level_box.addWidget(
            self.create_label("Severity")
        )

        self.cb_level = QComboBox()

        self.cb_level.addItems(levels)

        level_box.addWidget(
            self.style_input(self.cb_level)
        )

        emergency_box = QVBoxLayout()
        emergency_box.setSpacing(5)

        emergency_box.addWidget(
            self.create_label("Emergency")
        )

        self.cb_urgency = QComboBox()

        self.cb_urgency.addItems(levels)

        emergency_box.addWidget(
            self.style_input(self.cb_urgency)
        )

        combo_row.addLayout(level_box)
        combo_row.addLayout(emergency_box)

        form.addLayout(combo_row)

        form.addStretch()

        # Buttons

        button_row = QHBoxLayout()
        button_row.setSpacing(8)

        clear_btn = QPushButton("Clear")

        clear_btn.setFixedHeight(40)
        clear_btn.setCursor(
            Qt.PointingHandCursor
        )

        clear_btn.setStyleSheet(
            """
            QPushButton {
                background: #F1F5F9;
                color: #0F172A;
                border: none;
                border-radius: 8px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #E2E8F0;
            }
            """
        )

        clear_btn.clicked.connect(
            self.clear_form
        )

        add_btn = QPushButton(
            "+ Add Patient"
        )

        add_btn.setFixedHeight(40)
        add_btn.setCursor(
            Qt.PointingHandCursor
        )

        add_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {PRIMARY_BLUE};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
            }}

            QPushButton:hover {{
                background: #1D4ED8;
            }}
            """
        )

        add_btn.clicked.connect(
            self.add_patient
        )

        button_row.addWidget(
            clear_btn, 1
        )

        button_row.addWidget(
            add_btn, 2
        )

        form.addLayout(button_row)

        body.addWidget(form_card)

        # ====================================================
        # RIGHT SIDE
        # ====================================================

        right = QVBoxLayout()
        right.setSpacing(12)

        # ====================================================
        # KPI
        # ====================================================

        kpis = QHBoxLayout()
        kpis.setSpacing(10)

        self.card_total = self.create_kpi_mini(
            "TOTAL",
            "0",
            TEXT_PRIMARY
        )

        self.card_critical = self.create_kpi_mini(
            "CRITICAL",
            "0",
            COLOR_CRITICAL_TEXT
        )

        self.card_high = self.create_kpi_mini(
            "HIGH",
            "0",
            COLOR_HIGH_TEXT
        )

        # ====================================================
        # MEDIUM - thay cho NORMAL
        # ====================================================

        self.card_medium = self.create_kpi_mini(
            "MEDIUM",
            "0",
            COLOR_MEDIUM_TEXT
        )

        # ====================================================
        # LOW - thay cho NORMAL
        # ====================================================

        self.card_low = self.create_kpi_mini(
            "LOW",
            "0",
            COLOR_LOW_TEXT
        )

        for card in (
            self.card_total,
            self.card_critical,
            self.card_high,
            self.card_medium,
            self.card_low,
        ):
            kpis.addWidget(card)

        right.addLayout(kpis)

        # ====================================================
        # TABLE CARD
        # ====================================================

        table_card = QFrame()

        table_card.setStyleSheet(
            f"""
            QFrame {{
                background: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 12px;
            }}
            """
        )

        table_layout = QVBoxLayout(
            table_card
        )

        table_layout.setContentsMargins(
            16, 16, 16, 16
        )

        table_layout.setSpacing(12)

        # Search

        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self.txt_search = QLineEdit()

        self.txt_search.setPlaceholderText(
            "Search by patient ID, name, or symptom..."
        )

        self.style_input(
            self.txt_search
        )

        self.txt_search.textChanged.connect(
            self.filter_patients
        )

        filter_row.addWidget(
            self.txt_search, 1
        )

        # Priority filter

        self.cb_filter_priority = QComboBox()

        self.cb_filter_priority.addItems(
            [
                "All Priorities",
                "CRITICAL",
                "HIGH",
                "MEDIUM",
                "LOW",
            ]
        )

        self.cb_filter_priority.setFixedWidth(
            150
        )

        self.style_input(
            self.cb_filter_priority
        )

        self.cb_filter_priority.currentIndexChanged.connect(
            self.filter_patients
        )

        filter_row.addWidget(
            self.cb_filter_priority
        )

        table_layout.addLayout(
            filter_row
        )

        # Table

        self.table = QTableWidget(
            0, 8
        )

        self.table.setHorizontalHeaderLabels(
            [
                "PATIENT ID",
                "NAME",
                "AGE",
                "SYMPTOMS",
                "SEVERITY",
                "EMERGENCY",
                "PRIORITY",
                "ACTION",
            ]
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.setShowGrid(False)

        self.table.setFrameShape(
            QFrame.NoFrame
        )

        self.table.verticalHeader().setDefaultSectionSize(
            44
        )

        self.table.setAlternatingRowColors(
            False
        )

        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}

            QTableWidget::item {{
                color: {TEXT_PRIMARY};
                border-bottom: 1px solid {BORDER_COLOR};
                padding: 5px;
            }}

            QTableWidget::item:selected {{
                background: {PRIMARY_LIGHT};
                color: {TEXT_PRIMARY};
            }}

            QHeaderView::section {{
                background: #F8FAFC;
                color: {TEXT_MUTED};
                font-weight: 700;
                font-size: 10px;
                border: none;
                border-bottom: 1px solid {BORDER_COLOR};
                padding: 8px 5px;
            }}
            """
        )

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            6,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            7,
            QHeaderView.ResizeToContents
        )

        table_layout.addWidget(
            self.table, 1
        )

        right.addWidget(
            table_card, 1
        )

        body.addLayout(
            right, 1
        )

        main_layout.addLayout(
            body, 1
        )

        self.load_patients()

    # ========================================================
    # HELPERS
    # ========================================================

    def create_label(self, text):

        label = QLabel(text)

        label.setFont(
            QFont("Segoe UI", 9, QFont.Bold)
        )

        label.setStyleSheet(
            f"color: {TEXT_MUTED}; border: none;"
        )

        return label

    def style_input(self, widget):

        widget.setFixedHeight(38)

        widget.setStyleSheet(
            f"""
            QLineEdit, QComboBox, QSpinBox {{
                background: #F8FAFC;
                border: 1px solid {BORDER_COLOR};
                border-radius: 7px;
                padding: 0 9px;
                color: {TEXT_PRIMARY};
            }}

            QLineEdit:focus,
            QComboBox:focus,
            QSpinBox:focus {{
                background: white;
                border: 1px solid #60A5FA;
            }}
            """
        )

        return widget

    def create_kpi_mini(
        self,
        title,
        count,
        color
    ):

        card = QFrame()

        card.setMinimumHeight(76)

        card.setStyleSheet(
            f"""
            QFrame {{
                background: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 9px;
            }}
            """
        )

        layout = QVBoxLayout(card)

        layout.setContentsMargins(
            12, 9, 12, 9
        )

        layout.setSpacing(1)

        title_label = QLabel(title)

        title_label.setFont(
            QFont("Segoe UI", 8, QFont.Bold)
        )

        title_label.setStyleSheet(
            f"color: {TEXT_MUTED}; border: none;"
        )

        count_label = QLabel(
            str(count)
        )

        count_label.setFont(
            QFont("Segoe UI", 17, QFont.Bold)
        )

        count_label.setStyleSheet(
            f"color: {color}; border: none;"
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            count_label
        )

        return card

    # ========================================================
    # DATABASE
    # ========================================================

    def load_patients(self):

        try:

            patients = (
                self.db.get_all_patients()
            )

            self.display_data(
                patients
            )

        except Exception as e:

            print(
                "Patient database error:",
                e
            )

            self.display_data([])

    # ========================================================
    # DISPLAY
    # ========================================================

    def display_data(self, data):

        self.table.setRowCount(0)

        critical_cnt = 0
        high_cnt = 0
        medium_cnt = 0
        low_cnt = 0

        for row_idx, patient in enumerate(data):

            if isinstance(
                patient,
                Patient
            ):

                code = patient.patient_id
                name = patient.name
                age = patient.age
                symptoms = patient.symptoms
                level = patient.severity
                urgency = patient.emergency
                priority = patient.priority

            else:

                (
                    code,
                    name,
                    age,
                    symptoms,
                    level,
                    urgency,
                    priority,
                ) = patient[:7]

            if isinstance(
                symptoms,
                list
            ):

                symptoms_display = ", ".join(
                    str(x)
                    for x in symptoms
                )

            else:

                symptoms_display = str(
                    symptoms or ""
                )

            p_upper = str(
                priority or "LOW"
            ).upper()

            if "CRITICAL" in p_upper:

                critical_cnt += 1

            elif "HIGH" in p_upper:

                high_cnt += 1

            elif "MEDIUM" in p_upper:

                medium_cnt += 1

            else:

                low_cnt += 1

            self.table.insertRow(
                row_idx
            )

            # Patient ID

            code_item = QTableWidgetItem(
                str(code)
            )

            code_item.setFont(
                QFont(
                    "Segoe UI",
                    9,
                    QFont.Bold
                )
            )

            code_item.setForeground(
                Qt.GlobalColor.darkBlue
            )

            self.table.setItem(
                row_idx,
                0,
                code_item
            )

            # Name

            self.table.setItem(
                row_idx,
                1,
                QTableWidgetItem(
                    str(name)
                )
            )

            # Age

            age_item = QTableWidgetItem(
                str(age)
            )

            age_item.setTextAlignment(
                Qt.AlignCenter
            )

            self.table.setItem(
                row_idx,
                2,
                age_item
            )

            # Symptoms

            self.table.setItem(
                row_idx,
                3,
                QTableWidgetItem(
                    symptoms_display
                )
            )

            # Severity

            self.table.setItem(
                row_idx,
                4,
                QTableWidgetItem(
                    str(level or "LOW")
                )
            )

            # Emergency

            self.table.setItem(
                row_idx,
                5,
                QTableWidgetItem(
                    str(urgency or "LOW")
                )
            )

            # Priority

            self.table.setCellWidget(
                row_idx,
                6,
                create_priority_badge(
                    priority or "LOW",
                    priority or "LOW",
                ),
            )

            # Delete button

            delete_btn = QPushButton(
                "Delete"
            )

            delete_btn.setFixedHeight(
                30
            )

            delete_btn.setCursor(
                Qt.PointingHandCursor
            )

            delete_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background: {DANGER_LIGHT};
                    color: {DANGER};
                    border: 1px solid {DANGER_BORDER};
                    border-radius: 6px;
                    padding: 0 10px;
                    font-size: 9px;
                    font-weight: 700;
                }}

                QPushButton:hover {{
                    background: {DANGER};
                    color: white;
                }}
                """
            )

            delete_btn.clicked.connect(
                lambda checked=False,
                pid=str(code):
                self.delete_patient(pid)
            )

            self.table.setCellWidget(
                row_idx,
                7,
                delete_btn
            )

        self.card_total.findChildren(
            QLabel
        )[1].setText(
            str(len(data))
        )

        self.card_critical.findChildren(
            QLabel
        )[1].setText(
            str(critical_cnt)
        )

        self.card_high.findChildren(
            QLabel
        )[1].setText(
            str(high_cnt)
        )

        self.card_medium.findChildren(
            QLabel
        )[1].setText(
            str(medium_cnt)
        )

        self.card_low.findChildren(
            QLabel
        )[1].setText(
            str(low_cnt)
        )

        self.filter_patients()

    # ========================================================
    # SEARCH / FILTER
    # ========================================================

    def filter_patients(self):

        search_text = (
            self.txt_search.text()
            .strip()
            .lower()
        )

        filter_priority = (
            self.cb_filter_priority
            .currentText()
        )

        for row in range(
            self.table.rowCount()
        ):

            code_item = self.table.item(
                row, 0
            )

            name_item = self.table.item(
                row, 1
            )

            symptoms_item = self.table.item(
                row, 3
            )

            if (
                not code_item
                or not name_item
                or not symptoms_item
            ):
                continue

            code = (
                code_item.text()
                .lower()
            )

            name = (
                name_item.text()
                .lower()
            )

            symptoms = (
                symptoms_item.text()
                .lower()
            )

            match_search = (
                not search_text
                or search_text in code
                or search_text in name
                or search_text in symptoms
            )

            match_priority = True

            if filter_priority != "All Priorities":

                badge = self.table.cellWidget(
                    row, 6
                )

                label = (
                    badge.findChild(QLabel)
                    if badge
                    else None
                )

                priority_text = (
                    label.text()
                    if label
                    else ""
                )

                match_priority = (
                    priority_text
                    == filter_priority
                )

            self.table.setRowHidden(
                row,
                not (
                    match_search
                    and match_priority
                )
            )

    # ========================================================
    # ADD PATIENT
    # ========================================================

    def add_patient(self):

        code = (
            self.txt_code.text()
            .strip()
            .upper()
        )

        name = (
            self.txt_name.text()
            .strip()
        )

        age = (
            self.spin_age.value()
        )

        symptoms_text = (
            self.txt_symptoms.text()
            .strip()
        )

        severity = (
            self.cb_level.currentText()
        )

        emergency = (
            self.cb_urgency.currentText()
        )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not code:

            self.show_message(
                "Missing Patient ID",
                "Please enter a Patient ID.",
                QMessageBox.Warning,
            )

            self.txt_code.setFocus()

            return

        if not name:

            self.show_message(
                "Missing Name",
                "Please enter the patient's full name.",
                QMessageBox.Warning,
            )

            self.txt_name.setFocus()

            return

        # ----------------------------------------------------
        # DUPLICATE CHECK
        # ----------------------------------------------------

        try:

            existing_patients = (
                self.db.get_all_patients()
            )

            for p in existing_patients:

                if (
                    isinstance(p, Patient)
                    and str(
                        p.patient_id
                    ).upper()
                    == code
                ):

                    self.show_message(
                        "Duplicate Patient ID",
                        (
                            f"Patient ID "
                            f"{code} already exists."
                        ),
                        QMessageBox.Warning,
                    )

                    return

        except Exception as e:

            print(
                "Duplicate check error:",
                e
            )

        # ----------------------------------------------------
        # SYMPTOMS
        # ----------------------------------------------------

        symptoms = (
            [
                s.strip()
                for s in symptoms_text.split(",")
                if s.strip()
            ]
            if symptoms_text
            else []
        )

        # ----------------------------------------------------
        # CREATE PATIENT
        # ----------------------------------------------------

        patient = Patient(
            patient_id=code,
            name=name,
            age=age,
            symptoms=symptoms,
            severity=severity,
            emergency=emergency,
            waiting_time=0,
            priority="LOW",
        )

        # ----------------------------------------------------
        # AI REASONING
        # ----------------------------------------------------

        try:

            facts = (
                extract_facts_from_patient(
                    patient
                )
            )

            engine = InferenceEngine(
                get_default_knowledge_base()
            )

            result = engine.run(
                facts
            )

            patient.priority = (
                result.get(
                    "priority",
                    "LOW"
                )
            )

            print(
                f"AI result for {code}: "
                f"risk={result.get('risk')}, "
                f"priority={patient.priority}"
            )

        except Exception as e:

            print(
                "AI reasoning error:",
                e
            )

            patient.priority = "LOW"

        # ----------------------------------------------------
        # SAVE DATABASE
        # ----------------------------------------------------

        try:

            self.db.add_patient(
                patient
            )

        except Exception as e:

            self.show_message(
                "Add Patient Failed",
                (
                    "Could not save the patient."
                    f"\n\n{e}"
                ),
                QMessageBox.Critical,
            )

            print(
                "ERROR ADD PATIENT:",
                e
            )

            return

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        self.show_message(
            "Patient Added",
            (
                f"Patient {code} "
                "has been added successfully."
                f"\n\nAI Priority: "
                f"{patient.priority}"
            ),
            QMessageBox.Information,
        )

        self.clear_form()

        self.load_patients()

        self.patient_added.emit(patient.patient_id)

    # ========================================================
    # DELETE PATIENT
    # ========================================================

    def delete_patient(
        self,
        patient_id
    ):

        patient_name = ""

        # ----------------------------------------------------
        # FIND PATIENT NAME
        # ----------------------------------------------------

        try:

            for patient in (
                self.db.get_all_patients()
            ):

                if (
                    isinstance(
                        patient,
                        Patient
                    )
                    and str(
                        patient.patient_id
                    )
                    == str(patient_id)
                ):

                    patient_name = (
                        patient.name
                    )

                    break

        except Exception:
            pass

        display_name = (
            f" - {patient_name}"
            if patient_name
            else ""
        )

        # ----------------------------------------------------
        # CONFIRM
        # ----------------------------------------------------

        reply = self.show_message(
            "Delete Patient",
            (
                f"Are you sure you want "
                f"to delete patient "
                f"{patient_id}"
                f"{display_name}?"
                "\n\n"
                "This action cannot be undone."
            ),
            QMessageBox.Question,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        conn = None

        # ----------------------------------------------------
        # DELETE
        # ----------------------------------------------------

        try:

            db_path = getattr(
                self.db,
                "db_path",
                "hospital.db"
            )

            conn = sqlite3.connect(
                str(db_path)
            )

            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM patients
                WHERE id = ?
                """,
                (str(patient_id),)
            )

            deleted_rows = (
                cursor.rowcount
            )

            conn.commit()

            if deleted_rows == 0:

                self.show_message(
                    "Delete Failed",
                    (
                        f"Patient "
                        f"{patient_id} "
                        "was not found."
                    ),
                    QMessageBox.Warning,
                )

                return

            self.load_patients()

            self.patient_added.emit(" ")

            self.show_message(
                "Patient Deleted",
                (
                    f"Patient "
                    f"{patient_id} "
                    "has been deleted successfully."
                ),
                QMessageBox.Information,
            )

        except Exception as e:

            if conn:
                conn.rollback()

            self.show_message(
                "Delete Failed",
                (
                    f"Could not delete "
                    f"patient {patient_id}."
                    f"\n\n{e}"
                ),
                QMessageBox.Critical,
            )

            print(
                "ERROR DELETE PATIENT:",
                e
            )

        finally:

            if conn:
                conn.close()

    # ========================================================
    # CLEAR FORM
    # ========================================================

    def clear_form(self):

        self.txt_code.clear()

        self.txt_name.clear()

        self.spin_age.setValue(
            25
        )

        self.txt_symptoms.clear()

        self.cb_level.setCurrentIndex(
            0
        )

        self.cb_urgency.setCurrentIndex(
            0
        )