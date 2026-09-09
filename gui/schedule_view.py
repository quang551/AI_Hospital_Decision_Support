# gui/schedule_view.py

from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import time

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database.database import Database
from database.repository import (
    AppointmentRepository,
    DoctorRepository,
    PatientRepository,
    RoomRepository,
)
from models.appointment import Appointment
from scheduling.scheduler import Scheduler

# ============================================================
# DESIGN SYSTEM (MODERN & BORDERLESS)
# ============================================================

BG = "#F8FAFC"
CARD_BG = "#FFFFFF"
INPUT_BG = "#F1F5F9"

PRIMARY = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
PRIMARY_LIGHT = "#EFF6FF"

TEXT_MAIN = "#0F172A"
TEXT_MUTED = "#64748B"

SUCCESS = "#10B981"
SUCCESS_BG = "#ECFDF5"

WARNING = "#F59E0B"
PURPLE = "#8B5CF6"


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def make_label(
    text="", size=10, bold=False, color=TEXT_MAIN, uppercase=False
):
    if uppercase:
        text = text.upper()
    label = QLabel(text)

    font = QFont("Inter", size)
    if not font.exactMatch():
        font = QFont("Segoe UI", size)

    font.setBold(bold)
    label.setFont(font)
    label.setStyleSheet(f"color: {color}; background: transparent; border: none;")
    return label


def create_card():
    card = QFrame()
    card.setStyleSheet(
        f"""
        QFrame {{
            background-color: {CARD_BG};
            border: none;
            border-radius: 12px;
        }}
        """
    )

    # Thêm hiệu ứng đổ bóng mượt mà thay cho đường viền cứng
    shadow = QGraphicsDropShadowEffect(card)
    shadow.setBlurRadius(15)
    shadow.setColor(QColor(15, 23, 42, 12))
    shadow.setOffset(0, 4)
    card.setGraphicsEffect(shadow)

    return card


# ============================================================
# STAT CARD WIDGET
# ============================================================


class ScheduleStatCard(QFrame):

    def __init__(self, title, value, description, accent_color):
        super().__init__()

        self.setMinimumHeight(95)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {CARD_BG};
                border: none;
                border-radius: 12px;
            }}
            """
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(15, 23, 42, 10))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        top_layout = QHBoxLayout()

        title_label = make_label(
            title, size=9, bold=True, color=TEXT_MUTED, uppercase=True
        )

        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(
            f"""
            background-color: {accent_color};
            border-radius: 4px;
            border: none;
            """
        )

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(dot)

        value_label = make_label(str(value), size=20, bold=True, color=TEXT_MAIN)
        desc_label = make_label(
            description, size=9, bold=False, color=TEXT_MUTED
        )

        layout.addLayout(top_layout)
        layout.addWidget(value_label)
        layout.addWidget(desc_label)


# ============================================================
# SCHEDULE VIEW
# ============================================================


class ScheduleView(QWidget):

    data_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.db_path = None
        self.patient_repository = None
        self.doctor_repository = None
        self.room_repository = None
        self.appointment_repository = None

        self.patients = []
        self.doctors = []
        self.rooms = []
        self.appointments = []

        self.setup_database()
        self.setup_ui()
        self.load_data()

    # ========================================================
    # DATABASE SETUP
    # ========================================================

    def setup_database(self):
        try:
            project_root = Path(__file__).resolve().parent.parent
            self.db_path = project_root / "hospital.db"

            database = Database(str(self.db_path))
            database.create_tables()

            self.patient_repository = PatientRepository(str(self.db_path))
            self.doctor_repository = DoctorRepository(str(self.db_path))
            self.room_repository = RoomRepository(str(self.db_path))
            self.appointment_repository = AppointmentRepository(str(self.db_path))

        except Exception as e:
            print("Database connection error:", e)
            self.patient_repository = None
            self.doctor_repository = None
            self.room_repository = None
            self.appointment_repository = None

    # ========================================================
    # UI SETUP
    # ========================================================

    def setup_ui(self):
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {BG};
                font-family: "Segoe UI", "Inter", sans-serif;
            }}

            QComboBox {{
                background-color: {INPUT_BG};
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 6px 12px;
                color: {TEXT_MAIN};
                font-size: 12px;
            }}

            QComboBox:focus {{
                background-color: #FFFFFF;
                border: 1px solid {PRIMARY};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # ----------------------------------------------------
        # HEADER SECTION
        # ----------------------------------------------------
        header = QHBoxLayout()

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title = make_label("Schedule Management", size=20, bold=True, color=TEXT_MAIN)
        subtitle = make_label(
            "Automate and manage patient appointment schedules",
            size=10,
            bold=False,
            color=TEXT_MUTED,
        )

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header.addLayout(title_layout)
        header.addStretch()

        self.refresh_button = QPushButton("↻  Refresh")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {CARD_BG};
                color: {TEXT_MAIN};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background-color: {PRIMARY_LIGHT};
                color: {PRIMARY};
            }}
            """
        )

        # Shadow cho nút Refresh
        btn_shadow = QGraphicsDropShadowEffect(self.refresh_button)
        btn_shadow.setBlurRadius(8)
        btn_shadow.setColor(QColor(15, 23, 42, 8))
        btn_shadow.setOffset(0, 2)
        self.refresh_button.setGraphicsEffect(btn_shadow)

        self.refresh_button.clicked.connect(self.load_data)
        header.addWidget(self.refresh_button)

        main_layout.addLayout(header)

        # ----------------------------------------------------
        # STATISTICS CARDS
        # ----------------------------------------------------
        self.stat_layout = QGridLayout()
        self.stat_layout.setSpacing(12)
        main_layout.addLayout(self.stat_layout)

        # ----------------------------------------------------
        # CONTROL CARD (AUTO-SCHEDULE)
        # ----------------------------------------------------
        control_card = create_card()
        control_layout = QVBoxLayout(control_card)
        control_layout.setContentsMargins(18, 16, 18, 16)
        control_layout.setSpacing(12)

        card_title = make_label(
            "Auto-Generate Schedule", size=12, bold=True, color=TEXT_MAIN
        )
        control_layout.addWidget(card_title)

        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)

        # Doctor Selection
        doc_box = QVBoxLayout()
        doc_box.setSpacing(4)
        doc_box.addWidget(
            make_label("Assigned Doctor", size=9, bold=True, color=TEXT_MUTED)
        )
        self.doctor_combo = QComboBox()
        doc_box.addWidget(self.doctor_combo)
        options_layout.addLayout(doc_box, 1)

        # Room Selection
        room_box = QVBoxLayout()
        room_box.setSpacing(4)
        room_box.addWidget(
            make_label("Exam Room", size=9, bold=True, color=TEXT_MUTED)
        )
        self.room_combo = QComboBox()
        room_box.addWidget(self.room_combo)
        options_layout.addLayout(room_box, 1)

        # Action Button
        self.generate_button = QPushButton("✦  Auto-Assign Schedule")
        self.generate_button.setFixedHeight(36)
        self.generate_button.setCursor(Qt.PointingHandCursor)
        self.generate_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 18px;
                font-size: 12px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
            """
        )
        self.generate_button.clicked.connect(self.generate_schedule)

        btn_box = QVBoxLayout()
        btn_box.setSpacing(4)
        btn_box.addWidget(make_label("", size=9))
        btn_box.addWidget(self.generate_button)

        options_layout.addLayout(btn_box, 1)
        control_layout.addLayout(options_layout)

        main_layout.addWidget(control_card)

        # ----------------------------------------------------
        # TABLE CARD
        # ----------------------------------------------------
        table_card = create_card()
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(18, 16, 18, 16)
        table_layout.setSpacing(12)

        table_header = QHBoxLayout()
        table_title = make_label(
            "Appointments List", size=13, bold=True, color=TEXT_MAIN
        )
        table_header.addWidget(table_title)
        table_header.addStretch()

        self.appointment_count = make_label(
            "0 appointments", size=9, bold=True, color=PRIMARY
        )
        self.appointment_count.setStyleSheet(
            f"""
            color: {PRIMARY};
            background-color: {PRIMARY_LIGHT};
            border-radius: 6px;
            padding: 4px 10px;
            border: none;
            """
        )
        table_header.addWidget(self.appointment_count)
        table_layout.addLayout(table_header)

        # Table Widget
        self.table = QTableWidget()
        headers = [
            "Appt ID",
            "Patient Name",
            "Patient ID",
            "Doctor",
            "Room",
            "Date & Time",
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.Stretch)

        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: transparent;
                border: none;
                color: {TEXT_MAIN};
                font-size: 11px;
            }}

            QHeaderView::section {{
                background-color: {BG};
                color: {TEXT_MUTED};
                border: none;
                padding: 8px;
                font-size: 10px;
                font-weight: 700;
            }}

            QTableWidget::item {{
                padding: 10px 8px;
                border-bottom: 1px solid #F1F5F9;
            }}

            QTableWidget::item:selected {{
                background-color: {PRIMARY_LIGHT};
                color: {PRIMARY};
            }}
            """
        )

        table_layout.addWidget(self.table)
        main_layout.addWidget(table_card, 1)

        # ----------------------------------------------------
        # FOOTER STATUS
        # ----------------------------------------------------
        footer = QFrame()
        footer.setStyleSheet(
            f"""
            background-color: {SUCCESS_BG};
            border: none;
            border-radius: 8px;
            """
        )

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(12, 6, 12, 6)

        footer_text = make_label(
            "✓  Real-time database sync active", size=9, bold=True, color=SUCCESS
        )
        footer_layout.addWidget(footer_text)
        footer_layout.addStretch()

        main_layout.addWidget(footer)

    # ========================================================
    # DATA LOADING & REFRESH
    # ========================================================

    def load_data(self):
        try:
            self.patients = (
                self.patient_repository.get_all_patients()
                if self.patient_repository
                else []
            )
            self.doctors = (
                self.doctor_repository.get_all_doctors()
                if self.doctor_repository
                else []
            )
            self.rooms = (
                self.room_repository.get_all_rooms()
                if self.room_repository
                else []
            )
            self.appointments = (
                self.appointment_repository.get_all_appointments()
                if self.appointment_repository
                else []
            )

            self.update_combos()
            self.update_statistics()
            self.display_appointments()

        except Exception as e:
            print("Schedule load error:", e)

    def refresh(self):
        self.load_data()

    # ========================================================
    # UPDATE COMBOBOXES
    # ========================================================

    def update_combos(self):
        self.doctor_combo.clear()
        if self.doctors:
            for doctor in self.doctors:
                self.doctor_combo.addItem(
                    f"{doctor.name} - {doctor.specialization}", doctor
                )
        else:
            self.doctor_combo.addItem("No doctors available", None)

        self.room_combo.clear()
        if self.rooms:
            for room in self.rooms:
                self.room_combo.addItem(
                    f"{room.name} - {room.department}", room
                )
        else:
            self.room_combo.addItem("No rooms available", None)

    # ========================================================
    # UPDATE STATISTICS
    # ========================================================

    def update_statistics(self):
        while self.stat_layout.count():
            item = self.stat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cards = [
            ("Patients", len(self.patients), "Registered", PRIMARY),
            ("Doctors", len(self.doctors), "Active", PURPLE),
            ("Exam Rooms", len(self.rooms), "Available", WARNING),
            ("Appointments", len(self.appointments), "Allocated", SUCCESS),
        ]

        for col, data in enumerate(cards):
            card = ScheduleStatCard(*data)
            self.stat_layout.addWidget(card, 0, col)

    # ========================================================
    # FORMATTING UTILS
    # ========================================================

    def format_appointment_time(self, appointment_time):
        if not appointment_time:
            return ""

        value = str(appointment_time).strip()
        if not value:
            return ""

        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                parsed = datetime.strptime(value, fmt)
                return parsed.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                pass

        try:
            parsed_time = datetime.strptime(value, "%H:%M")
            today = datetime.now().strftime("%Y-%m-%d")
            return f"{today} {parsed_time.strftime('%H:%M')}"
        except ValueError:
            return value

    def normalize_clock(self, value):
        if not value:
            return ""
        value = str(value).strip()
        if " " in value:
            value = value.split()[-1]

        parts = value.split(":")
        if len(parts) >= 2:
            try:
                hour = int(parts[0])
                minute = int(parts[1])
                return f"{hour:02d}:{minute:02d}"
            except ValueError:
                pass
        return value

    # ========================================================
    # DISPLAY APPOINTMENTS
    # ========================================================

    def display_appointments(self):
        self.table.setRowCount(0)
        sorted_appointments = sorted(
            self.appointments, key=lambda a: str(a.time)
        )

        for appointment in sorted_appointments:
            try:
                row = self.table.rowCount()
                self.table.insertRow(row)

                display_time = self.format_appointment_time(appointment.time)
                values = [
                    appointment.appointment_id,
                    appointment.patient.name,
                    appointment.patient.patient_id,
                    appointment.doctor.name,
                    appointment.room.name,
                    display_time,
                ]

                for col, val in enumerate(values):
                    item = QTableWidgetItem(str(val))
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.table.setItem(row, col, item)

            except Exception as e:
                print("Display appointment error:", e)

        self.appointment_count.setText(f"{len(self.appointments)} appointments")

    # ========================================================
    # AUTO ID GENERATOR & SAFE SAVE
    # ========================================================

    def get_next_appointment_id(self):
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM appointments")
            rows = cursor.fetchall()
            conn.close()

            max_number = 0
            for row in rows:
                val = row[0]
                if isinstance(val, str) and val.startswith("A"):
                    try:
                        max_number = max(max_number, int(val[1:]))
                    except (ValueError, TypeError):
                        continue

            return f"A{max_number + 1:03d}"
        except Exception:
            return "A001"

    def save_appointment_safe(self, appointment, max_retries=5):
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                self.appointment_repository.add_appointment(appointment)
                return True
            except sqlite3.IntegrityError as e:
                if "appointments.id" not in str(e).lower() and "unique" not in str(e).lower():
                    raise
                appointment.appointment_id = self.get_next_appointment_id()
                last_error = e
                time.sleep(0.2)
            except sqlite3.OperationalError as e:
                last_error = e
                if "locked" not in str(e).lower():
                    raise
                time.sleep(0.5 * attempt)
            except Exception as e:
                last_error = e
                raise

        raise Exception(f"Failed to save appointment after {max_retries} retries: {last_error}")

    # ========================================================
    # SLOT SEARCH LOGIC
    # ========================================================

    def find_free_slot_on_date(self, doctor, room, date_value, preferred_time, all_slots, occupied):
        normalized_slots = [self.normalize_clock(slot) for slot in all_slots]
        preferred_time = self.normalize_clock(preferred_time)

        try:
            start_index = normalized_slots.index(preferred_time)
        except ValueError:
            start_index = 0

        for index in range(start_index, len(normalized_slots)):
            candidate = normalized_slots[index]
            key = (doctor.doctor_id, room.room_id, date_value, candidate)
            if key not in occupied:
                return candidate
        return None

    def find_next_free_slot_across_days(self, doctor, room, start_date, preferred_time, all_slots, occupied, max_days=365):
        current_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        for day_offset in range(max_days):
            date_value = (current_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            first_time = preferred_time if day_offset == 0 else all_slots[0]

            free_time = self.find_free_slot_on_date(
                doctor, room, date_value, first_time, all_slots, occupied
            )
            if free_time is not None:
                return date_value, free_time

        return None, None

    # ========================================================
    # GENERATE SCHEDULE ACTION
    # ========================================================

    def generate_schedule(self):
        if not self.patients:
            QMessageBox.warning(
                self, "No Patients", "There are no registered patients to generate a schedule for."
            )
            return

        selected_doctor = self.doctor_combo.currentData()
        selected_room = self.room_combo.currentData()

        if not selected_doctor or not selected_room:
            QMessageBox.warning(
                self, "Missing Selection", "Please select a valid doctor and exam room."
            )
            return

        # Prepare default slots
        all_slots = [
            "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
            "11:00", "11:30", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00"
        ]

        # Gather currently occupied slots
        occupied = set()
        for appt in self.appointments:
            d_val, t_val = self.format_appointment_time(appt.time).split(" ", 1) if " " in self.format_appointment_time(appt.time) else (datetime.now().strftime("%Y-%m-%d"), appt.time)
            occupied.add((appt.doctor.doctor_id, appt.room.room_id, d_val, self.normalize_clock(t_val)))

        start_date = datetime.now().strftime("%Y-%m-%d")
        created_count = 0

        for patient in self.patients:
            # Skip if patient already scheduled
            if any(a.patient.patient_id == patient.patient_id for a in self.appointments):
                continue

            date_val, time_val = self.find_next_free_slot_across_days(
                selected_doctor, selected_room, start_date, "08:00", all_slots, occupied
            )

            if date_val and time_val:
                # Key fix: Immediately mark slot occupied locally
                occupied.add((selected_doctor.doctor_id, selected_room.room_id, date_val, time_val))

                full_time_str = f"{date_val} {time_val}"
                new_appt = Appointment(
                    appointment_id=self.get_next_appointment_id(),
                    patient=patient,
                    doctor=selected_doctor,
                    room=selected_room,
                    time=full_time_str,
                )

                try:
                    self.save_appointment_safe(new_appt)
                    created_count += 1
                except Exception as e:
                    print(f"Error saving appointment for {patient.name}: {e}")

        self.load_data()
        self.data_changed.emit()

        QMessageBox.information(
            self,
            "Scheduling Complete",
            f"Successfully allocated {created_count} new appointment(s).",
        )