# gui/schedule_view.py

from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import time

from PySide6.QtCore import Qt, Signal
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


# ============================================================
# DESIGN SYSTEM
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
    text="",
    size=10,
    bold=False,
    color=TEXT_MAIN,
    uppercase=False,
):
    if uppercase:
        text = text.upper()

    label = QLabel(text)

    font = QFont("Inter", size)

    if not font.exactMatch():
        font = QFont("Segoe UI", size)

    font.setBold(bold)

    label.setFont(font)

    label.setStyleSheet(
        f"color: {color}; "
        "background: transparent; "
        "border: none;"
    )

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

    shadow = QGraphicsDropShadowEffect(card)

    shadow.setBlurRadius(15)
    shadow.setColor(
        QColor(15, 23, 42, 12)
    )
    shadow.setOffset(0, 4)

    card.setGraphicsEffect(shadow)

    return card


# ============================================================
# STAT CARD
# ============================================================

class ScheduleStatCard(QFrame):

    def __init__(
        self,
        title,
        value,
        description,
        accent_color,
    ):
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
        shadow.setColor(
            QColor(15, 23, 42, 10)
        )
        shadow.setOffset(0, 3)

        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            12,
            16,
            12,
        )

        layout.setSpacing(4)

        top_layout = QHBoxLayout()

        title_label = make_label(
            title,
            size=9,
            bold=True,
            color=TEXT_MUTED,
            uppercase=True,
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

        top_layout.addWidget(
            title_label
        )

        top_layout.addStretch()

        top_layout.addWidget(dot)

        value_label = make_label(
            str(value),
            size=20,
            bold=True,
            color=TEXT_MAIN,
        )

        desc_label = make_label(
            description,
            size=9,
            color=TEXT_MUTED,
        )

        layout.addLayout(
            top_layout
        )

        layout.addWidget(
            value_label
        )

        layout.addWidget(
            desc_label
        )


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

            project_root = (
                Path(__file__).resolve().parent.parent
            )

            self.db_path = (
                project_root / "hospital.db"
            )

            database = Database(
                str(self.db_path)
            )

            database.create_tables()

            self.patient_repository = (
                PatientRepository(
                    str(self.db_path)
                )
            )

            self.doctor_repository = (
                DoctorRepository(
                    str(self.db_path)
                )
            )

            self.room_repository = (
                RoomRepository(
                    str(self.db_path)
                )
            )

            self.appointment_repository = (
                AppointmentRepository(
                    str(self.db_path)
                )
            )

        except Exception as e:

            print(
                "Database connection error:",
                e,
            )

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

        main_layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )

        main_layout.setSpacing(16)

        # ====================================================
        # HEADER
        # ====================================================

        header = QHBoxLayout()

        title_layout = QVBoxLayout()

        title_layout.setSpacing(2)

        title = make_label(
            "Schedule Management",
            size=20,
            bold=True,
            color=TEXT_MAIN,
        )

        subtitle = make_label(
            "Automate and manage patient appointment schedules",
            size=10,
            color=TEXT_MUTED,
        )

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header.addLayout(
            title_layout
        )

        header.addStretch()

        self.refresh_button = QPushButton(
            "↻  Refresh"
        )

        self.refresh_button.setCursor(
            Qt.PointingHandCursor
        )

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

        btn_shadow = QGraphicsDropShadowEffect(
            self.refresh_button
        )

        btn_shadow.setBlurRadius(8)
        btn_shadow.setColor(
            QColor(15, 23, 42, 8)
        )
        btn_shadow.setOffset(0, 2)

        self.refresh_button.setGraphicsEffect(
            btn_shadow
        )

        self.refresh_button.clicked.connect(
            self.load_data
        )

        header.addWidget(
            self.refresh_button
        )

        main_layout.addLayout(header)

        # ====================================================
        # STATISTICS
        # ====================================================

        self.stat_layout = QGridLayout()

        self.stat_layout.setSpacing(12)

        main_layout.addLayout(
            self.stat_layout
        )

        # ====================================================
        # CONTROL CARD
        # ====================================================

        control_card = create_card()

        control_layout = QVBoxLayout(
            control_card
        )

        control_layout.setContentsMargins(
            18,
            16,
            18,
            16,
        )

        control_layout.setSpacing(12)

        card_title = make_label(
            "Auto-Generate Schedule",
            size=12,
            bold=True,
            color=TEXT_MAIN,
        )

        control_layout.addWidget(
            card_title
        )

        options_layout = QHBoxLayout()

        options_layout.setSpacing(12)

        # ----------------------------------------------------
        # DOCTOR
        # ----------------------------------------------------

        doc_box = QVBoxLayout()

        doc_box.setSpacing(4)

        doc_box.addWidget(
            make_label(
                "Assigned Doctor",
                size=9,
                bold=True,
                color=TEXT_MUTED,
            )
        )

        self.doctor_combo = QComboBox()

        doc_box.addWidget(
            self.doctor_combo
        )

        options_layout.addLayout(
            doc_box,
            1,
        )

        # ----------------------------------------------------
        # ROOM
        # ----------------------------------------------------

        room_box = QVBoxLayout()

        room_box.setSpacing(4)

        room_box.addWidget(
            make_label(
                "Exam Room",
                size=9,
                bold=True,
                color=TEXT_MUTED,
            )
        )

        self.room_combo = QComboBox()

        room_box.addWidget(
            self.room_combo
        )

        options_layout.addLayout(
            room_box,
            1,
        )

        # ----------------------------------------------------
        # BUTTON
        # ----------------------------------------------------

        self.generate_button = QPushButton(
            "✦  Auto-Assign Schedule"
        )

        self.generate_button.setFixedHeight(
            36
        )

        self.generate_button.setCursor(
            Qt.PointingHandCursor
        )

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

        self.generate_button.clicked.connect(
            self.generate_schedule
        )

        btn_box = QVBoxLayout()

        btn_box.setSpacing(4)

        btn_box.addWidget(
            make_label("", size=9)
        )

        btn_box.addWidget(
            self.generate_button
        )

        options_layout.addLayout(
            btn_box,
            1,
        )

        control_layout.addLayout(
            options_layout
        )

        main_layout.addWidget(
            control_card
        )

        # ====================================================
        # TABLE
        # ====================================================

        table_card = create_card()

        table_layout = QVBoxLayout(
            table_card
        )

        table_layout.setContentsMargins(
            18,
            16,
            18,
            16,
        )

        table_layout.setSpacing(12)

        table_header = QHBoxLayout()

        table_title = make_label(
            "Appointments List",
            size=13,
            bold=True,
            color=TEXT_MAIN,
        )

        table_header.addWidget(
            table_title
        )

        table_header.addStretch()

        self.appointment_count = make_label(
            "0 appointments",
            size=9,
            bold=True,
            color=PRIMARY,
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

        table_header.addWidget(
            self.appointment_count
        )

        table_layout.addLayout(
            table_header
        )

        # ----------------------------------------------------
        # TABLE
        # ----------------------------------------------------

        self.table = QTableWidget()

        headers = [
            "Appt ID",
            "Patient Name",
            "Patient ID",
            "Doctor",
            "Room",
            "Date & Time",
        ]

        self.table.setColumnCount(
            len(headers)
        )

        self.table.setHorizontalHeaderLabels(
            headers
        )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.setShowGrid(False)

        header_view = (
            self.table.horizontalHeader()
        )

        header_view.setSectionResizeMode(
            QHeaderView.Stretch
        )

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

        table_layout.addWidget(
            self.table
        )

        main_layout.addWidget(
            table_card,
            1,
        )

        # ====================================================
        # FOOTER
        # ====================================================

        footer = QFrame()

        footer.setStyleSheet(
            f"""
            background-color: {SUCCESS_BG};
            border: none;
            border-radius: 8px;
            """
        )

        footer_layout = QHBoxLayout(
            footer
        )

        footer_layout.setContentsMargins(
            12,
            6,
            12,
            6,
        )

        footer_text = make_label(
            "✓  Real-time database sync active",
            size=9,
            bold=True,
            color=SUCCESS,
        )

        footer_layout.addWidget(
            footer_text
        )

        footer_layout.addStretch()

        main_layout.addWidget(
            footer
        )

    # ========================================================
    # MESSAGE BOX
    # ========================================================

    def show_message(
        self,
        title,
        message,
        icon=QMessageBox.Information,
    ):

        msg = QMessageBox(self)

        msg.setIcon(icon)

        msg.setWindowTitle(
            title
        )

        msg.setText(
            message
        )

        msg.setStyleSheet(
            """
            QMessageBox {
                background-color: white;
            }

            QMessageBox QLabel {
                color: #0F172A;
                background-color: white;
            }

            QMessageBox QPushButton {
                color: #0F172A;
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 16px;
                min-width: 60px;
            }

            QMessageBox QPushButton:hover {
                background-color: #E2E8F0;
            }
            """
        )

        msg.exec()

    # ========================================================
    # LOAD DATA
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

            print(
                "Schedule load error:",
                e,
            )

    # ========================================================
    # REFRESH
    # ========================================================

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
                    f"{doctor.name} - "
                    f"{doctor.specialization}",
                    doctor,
                )

        else:

            self.doctor_combo.addItem(
                "No doctors available",
                None,
            )

        self.room_combo.clear()

        if self.rooms:

            for room in self.rooms:

                self.room_combo.addItem(
                    f"{room.name} - "
                    f"{room.department}",
                    room,
                )

        else:

            self.room_combo.addItem(
                "No rooms available",
                None,
            )

    # ========================================================
    # UPDATE STATISTICS
    # ========================================================

    def update_statistics(self):

        while self.stat_layout.count():

            item = (
                self.stat_layout.takeAt(0)
            )

            if item.widget():

                item.widget().deleteLater()

        cards = [
            (
                "Patients",
                len(self.patients),
                "Registered",
                PRIMARY,
            ),
            (
                "Doctors",
                len(self.doctors),
                "Active",
                PURPLE,
            ),
            (
                "Exam Rooms",
                len(self.rooms),
                "Available",
                WARNING,
            ),
            (
                "Appointments",
                len(self.appointments),
                "Allocated",
                SUCCESS,
            ),
        ]

        for col, data in enumerate(cards):

            card = ScheduleStatCard(
                *data
            )

            self.stat_layout.addWidget(
                card,
                0,
                col,
            )

    # ========================================================
    # FORMATTING
    # ========================================================

    def format_appointment_time(
        self,
        appointment_time,
    ):

        if not appointment_time:
            return ""

        value = str(
            appointment_time
        ).strip()

        if not value:
            return ""

        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ):

            try:

                parsed = datetime.strptime(
                    value,
                    fmt,
                )

                return parsed.strftime(
                    "%Y-%m-%d %H:%M"
                )

            except ValueError:
                pass

        try:

            parsed_time = datetime.strptime(
                value,
                "%H:%M",
            )

            today = datetime.now().strftime(
                "%Y-%m-%d"
            )

            return (
                f"{today} "
                f"{parsed_time.strftime('%H:%M')}"
            )

        except ValueError:

            return value

    # ========================================================
    # NORMALIZE CLOCK
    # ========================================================

    def normalize_clock(self, value):

        if not value:
            return ""

        value = str(
            value
        ).strip()

        if " " in value:
            value = value.split()[-1]

        parts = value.split(":")

        if len(parts) >= 2:

            try:

                hour = int(parts[0])
                minute = int(parts[1])

                return (
                    f"{hour:02d}:"
                    f"{minute:02d}"
                )

            except ValueError:
                pass

        return value

    # ========================================================
    # DISPLAY APPOINTMENTS
    # ========================================================

    def display_appointments(self):

        self.table.setRowCount(0)

        sorted_appointments = sorted(
            self.appointments,
            key=lambda a: str(a.time),
        )

        for appointment in sorted_appointments:

            try:

                row = (
                    self.table.rowCount()
                )

                self.table.insertRow(row)

                display_time = (
                    self.format_appointment_time(
                        appointment.time
                    )
                )

                values = [
                    appointment.appointment_id,
                    appointment.patient.name,
                    appointment.patient.patient_id,
                    appointment.doctor.name,
                    appointment.room.name,
                    display_time,
                ]

                for col, value in enumerate(
                    values
                ):

                    item = QTableWidgetItem(
                        str(value)
                    )

                    item.setTextAlignment(
                        Qt.AlignLeft
                        | Qt.AlignVCenter
                    )

                    self.table.setItem(
                        row,
                        col,
                        item,
                    )

            except Exception as e:

                print(
                    "Display appointment error:",
                    e,
                )

        self.appointment_count.setText(
            f"{len(self.appointments)} appointments"
        )

    # ========================================================
    # NEXT APPOINTMENT ID
    # ========================================================

    def get_next_appointment_id(self):

        try:

            conn = sqlite3.connect(
                str(self.db_path),
                timeout=10,
            )

            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM appointments"
            )

            rows = cursor.fetchall()

            conn.close()

            max_number = 0

            for row in rows:

                value = row[0]

                if (
                    isinstance(value, str)
                    and value.startswith("A")
                ):

                    try:

                        max_number = max(
                            max_number,
                            int(value[1:]),
                        )

                    except (
                        ValueError,
                        TypeError,
                    ):

                        continue

            return (
                f"A{max_number + 1:03d}"
            )

        except Exception:

            return "A001"

    # ========================================================
    # SAFE SAVE
    # ========================================================

    def save_appointment_safe(
        self,
        appointment,
        max_retries=5,
    ):

        last_error = None

        for attempt in range(
            1,
            max_retries + 1,
        ):

            try:

                self.appointment_repository.add_appointment(
                    appointment
                )

                return True

            except sqlite3.IntegrityError as e:

                error_text = str(e).lower()

                if (
                    "appointments.id"
                    not in error_text
                    and "unique"
                    not in error_text
                ):

                    raise

                appointment.appointment_id = (
                    self.get_next_appointment_id()
                )

                last_error = e

                time.sleep(0.2)

            except sqlite3.OperationalError as e:

                last_error = e

                if "locked" not in str(e).lower():

                    raise

                time.sleep(
                    0.5 * attempt
                )

            except Exception as e:

                last_error = e

                raise

        raise Exception(
            "Failed to save appointment "
            f"after {max_retries} retries: "
            f"{last_error}"
        )

    # ========================================================
    # GET TIME SLOTS
    # ========================================================

    def get_time_slots(self):

        return [
            "08:00",
            "08:30",
            "09:00",
            "09:30",
            "10:00",
            "10:30",
            "11:00",
            "11:30",
            "13:30",
            "14:00",
            "14:30",
            "15:00",
            "15:30",
            "16:00",
        ]

    # ========================================================
    # FIND FREE SLOT ON DATE
    # ========================================================

    def find_free_slot_on_date(
        self,
        doctor,
        room,
        date_value,
        preferred_time,
        all_slots,
        occupied,
    ):

        normalized_slots = [
            self.normalize_clock(slot)
            for slot in all_slots
        ]

        preferred_time = (
            self.normalize_clock(
                preferred_time
            )
        )

        try:

            start_index = (
                normalized_slots.index(
                    preferred_time
                )
            )

        except ValueError:

            start_index = 0

        for index in range(
            start_index,
            len(normalized_slots),
        ):

            candidate = (
                normalized_slots[index]
            )

            key = (
                doctor.doctor_id,
                room.room_id,
                date_value,
                candidate,
            )

            if key not in occupied:

                return candidate

        return None

    # ========================================================
    # FIND NEXT FREE SLOT
    # ========================================================

    def find_next_free_slot_across_days(
        self,
        doctor,
        room,
        start_date,
        preferred_time,
        all_slots,
        occupied,
        max_days=365,
    ):

        current_date = datetime.strptime(
            start_date,
            "%Y-%m-%d",
        ).date()

        for day_offset in range(
            max_days
        ):

            date_value = (
                current_date
                + timedelta(
                    days=day_offset
                )
            ).strftime(
                "%Y-%m-%d"
            )

            if day_offset == 0:

                first_time = preferred_time

            else:

                first_time = all_slots[0]

            free_time = (
                self.find_free_slot_on_date(
                    doctor,
                    room,
                    date_value,
                    first_time,
                    all_slots,
                    occupied,
                )
            )

            if free_time is not None:

                return (
                    date_value,
                    free_time,
                )

        return None, None

    # ========================================================
    # BUILD OCCUPIED SLOTS
    # ========================================================

    def build_occupied_slots(self):

        occupied = set()

        for appointment in self.appointments:

            try:

                formatted_time = (
                    self.format_appointment_time(
                        appointment.time
                    )
                )

                if " " in formatted_time:

                    date_value, time_value = (
                        formatted_time.split(
                            " ",
                            1,
                        )
                    )

                else:

                    date_value = (
                        datetime.now().strftime(
                            "%Y-%m-%d"
                        )
                    )

                    time_value = (
                        appointment.time
                    )

                key = (
                    appointment.doctor.doctor_id,
                    appointment.room.room_id,
                    date_value,
                    self.normalize_clock(
                        time_value
                    ),
                )

                occupied.add(key)

            except Exception as e:

                print(
                    "Occupied slot error:",
                    e,
                )

        return occupied

    # ========================================================
    # GET DEPARTMENT RESOURCES
    # ========================================================

    def get_resource_pairs(
        self,
        priority,
    ):
        """
        CRITICAL/HIGH:
            Emergency Doctor + Emergency Room

        MEDIUM/LOW:
            General Medicine Doctor + General Medicine Room
        """

        priority = str(
            priority
        ).strip().upper()

        if priority in (
            "CRITICAL",
            "HIGH",
        ):

            doctors = [
                doctor
                for doctor in self.doctors
                if str(
                    doctor.specialization
                ).strip().lower()
                == "emergency"
            ]

            rooms = [
                room
                for room in self.rooms
                if str(
                    room.department
                ).strip().lower()
                == "emergency"
            ]

        else:

            doctors = [
                doctor
                for doctor in self.doctors
                if str(
                    doctor.specialization
                ).strip().lower()
                == "general medicine"
            ]

            rooms = [
                room
                for room in self.rooms
                if str(
                    room.department
                ).strip().lower()
                == "general medicine"
            ]

        return list(
            zip(
                doctors,
                rooms,
            )
        )

    # ========================================================
    # AUTO ASSIGN ONE PATIENT
    # ========================================================

    def generate_schedule_for_patient(
        self,
        patient,
    ):
        """
        Tự động xếp lịch cho MỘT bệnh nhân.

        Đây là hàm được MainWindow gọi ngay
        sau khi PatientView thêm bệnh nhân.

        Priority:
            CRITICAL / HIGH
                -> Emergency Doctor
                -> Emergency Room

            MEDIUM / LOW
                -> General Medicine Doctor
                -> General Medicine Room
        """

        if patient is None:

            print(
                "Auto schedule: patient is None."
            )

            return False

        # ----------------------------------------------------
        # Lấy priority của bệnh nhân
        # ----------------------------------------------------

        priority = str(
            getattr(
                patient,
                "priority",
                "LOW",
            )
        ).strip().upper()

        if priority not in (
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW",
        ):

            priority = "LOW"

        # ----------------------------------------------------
        # Kiểm tra đã có appointment chưa
        # ----------------------------------------------------

        patient_id = getattr(
            patient,
            "patient_id",
            None,
        )

        if patient_id is None:

            patient_id = getattr(
                patient,
                "id",
                None,
            )

        for appointment in self.appointments:

            appointment_patient = (
                getattr(
                    appointment,
                    "patient",
                    None,
                )
            )

            appointment_patient_id = None

            if appointment_patient is not None:

                appointment_patient_id = (
                    getattr(
                        appointment_patient,
                        "patient_id",
                        None,
                    )
                )

                if appointment_patient_id is None:

                    appointment_patient_id = (
                        getattr(
                            appointment_patient,
                            "id",
                            None,
                        )
                    )

            if (
                str(appointment_patient_id)
                == str(patient_id)
            ):

                print(
                    "Patient already scheduled:",
                    patient_id,
                )

                return False

        # ----------------------------------------------------
        # Lấy Doctor + Room theo Priority
        # ----------------------------------------------------

        resource_pairs = (
            self.get_resource_pairs(
                priority
            )
        )

        if not resource_pairs:

            if priority in (
                "CRITICAL",
                "HIGH",
            ):

                message = (
                    "Không có Emergency Doctor "
                    "hoặc Emergency Room."
                )

            else:

                message = (
                    "Không có General Medicine "
                    "Doctor hoặc Room."
                )

            print(
                "Auto schedule failed:",
                message,
            )

            return False

        # ----------------------------------------------------
        # Các giờ khám
        # ----------------------------------------------------

        all_slots = (
            self.get_time_slots()
        )

        # ----------------------------------------------------
        # Các slot đang bị chiếm
        # ----------------------------------------------------

        occupied = (
            self.build_occupied_slots()
        )

        # ----------------------------------------------------
        # Chọn Doctor + Room
        #
        # Tìm pair đầu tiên có slot trống.
        # ----------------------------------------------------

        start_date = (
            datetime.now().strftime(
                "%Y-%m-%d"
            )
        )

        selected_doctor = None
        selected_room = None
        selected_date = None
        selected_time = None

        for doctor, room in resource_pairs:

            date_value, time_value = (
                self.find_next_free_slot_across_days(
                    doctor,
                    room,
                    start_date,
                    "08:00",
                    all_slots,
                    occupied,
                )
            )

            if (
                date_value
                and time_value
            ):

                selected_doctor = doctor
                selected_room = room
                selected_date = date_value
                selected_time = time_value

                break

        # ----------------------------------------------------
        # Không tìm được slot
        # ----------------------------------------------------

        if (
            selected_doctor is None
            or selected_room is None
            or selected_date is None
            or selected_time is None
        ):

            print(
                "No available appointment slot "
                f"for patient {patient_id}."
            )

            return False

        # ----------------------------------------------------
        # Tạo appointment
        # ----------------------------------------------------

        full_time_str = (
            f"{selected_date} "
            f"{selected_time}"
        )

        appointment_id = (
            self.get_next_appointment_id()
        )

        new_appointment = Appointment(
            appointment_id=appointment_id,
            patient=patient,
            doctor=selected_doctor,
            room=selected_room,
            time=full_time_str,
        )

        # ----------------------------------------------------
        # Save database
        # ----------------------------------------------------

        try:

            self.save_appointment_safe(
                new_appointment
            )

        except Exception as e:

            print(
                "Auto schedule save error:",
                e,
            )

            return False

        # ----------------------------------------------------
        # Reload data
        # ----------------------------------------------------

        self.load_data()

        self.data_changed.emit()

        # ----------------------------------------------------
        # Console log
        # ----------------------------------------------------

        print(
            "[AUTO-SCHEDULE]"
        )

        print(
            f"Patient : {patient_id}"
        )

        print(
            f"Priority: {priority}"
        )

        print(
            f"Doctor  : {selected_doctor.name}"
        )

        print(
            f"Room    : {selected_room.name}"
        )

        print(
            f"Time    : {full_time_str}"
        )

        return True

    # ========================================================
    # GENERATE SCHEDULE FOR ALL PATIENTS
    # ========================================================

    def generate_schedule(self):

        if not self.patients:

            self.show_message(
                "No Patients",
                "There are no registered patients "
                "to generate a schedule for.",
                QMessageBox.Warning,
            )

            return

        all_slots = (
            self.get_time_slots()
        )

        # ----------------------------------------------------
        # Resource pairs
        # ----------------------------------------------------

        emergency_pairs = (
            self.get_resource_pairs(
                "HIGH"
            )
        )

        general_pairs = (
            self.get_resource_pairs(
                "LOW"
            )
        )

        # ----------------------------------------------------
        # Kiểm tra resource
        # ----------------------------------------------------

        if not emergency_pairs:

            self.show_message(
                "Missing Emergency Resources",
                "Emergency doctors or rooms "
                "are not available.",
                QMessageBox.Warning,
            )

            return

        if not general_pairs:

            self.show_message(
                "Missing General Medicine Resources",
                "General Medicine doctors or rooms "
                "are not available.",
                QMessageBox.Warning,
            )

            return

        # ----------------------------------------------------
        # Occupied slots
        # ----------------------------------------------------

        occupied = (
            self.build_occupied_slots()
        )

        start_date = (
            datetime.now().strftime(
                "%Y-%m-%d"
            )
        )

        emergency_index = 0
        general_index = 0

        created_count = 0

        # ----------------------------------------------------
        # Process patients
        # ----------------------------------------------------

        for patient in self.patients:

            # ------------------------------------------------
            # Skip patient đã có lịch
            # ------------------------------------------------

            already_scheduled = False

            for appointment in (
                self.appointments
            ):

                try:

                    if (
                        appointment.patient.patient_id
                        == patient.patient_id
                    ):

                        already_scheduled = True

                        break

                except Exception:

                    continue

            if already_scheduled:

                continue

            # ------------------------------------------------
            # Priority
            # ------------------------------------------------

            priority = str(
                getattr(
                    patient,
                    "priority",
                    "LOW",
                )
            ).strip().upper()

            if priority not in (
                "CRITICAL",
                "HIGH",
                "MEDIUM",
                "LOW",
            ):

                priority = "LOW"

            # ------------------------------------------------
            # Chọn resource
            # ------------------------------------------------

            if priority in (
                "CRITICAL",
                "HIGH",
            ):

                doctor, room = (
                    emergency_pairs[
                        emergency_index
                        % len(emergency_pairs)
                    ]
                )

                emergency_index += 1

            else:

                doctor, room = (
                    general_pairs[
                        general_index
                        % len(general_pairs)
                    ]
                )

                general_index += 1

            # ------------------------------------------------
            # Find slot
            # ------------------------------------------------

            date_value, time_value = (
                self.find_next_free_slot_across_days(
                    doctor,
                    room,
                    start_date,
                    "08:00",
                    all_slots,
                    occupied,
                )
            )

            if (
                not date_value
                or not time_value
            ):

                print(
                    "No available slot for:",
                    patient.patient_id,
                )

                continue

            # ------------------------------------------------
            # Mark occupied
            # ------------------------------------------------

            occupied.add(
                (
                    doctor.doctor_id,
                    room.room_id,
                    date_value,
                    time_value,
                )
            )

            # ------------------------------------------------
            # Appointment
            # ------------------------------------------------

            full_time_str = (
                f"{date_value} "
                f"{time_value}"
            )

            new_appointment = Appointment(
                appointment_id=(
                    self.get_next_appointment_id()
                ),
                patient=patient,
                doctor=doctor,
                room=room,
                time=full_time_str,
            )

            try:

                self.save_appointment_safe(
                    new_appointment
                )

                created_count += 1

                print(
                    "[AUTO-SCHEDULE] "
                    f"{patient.patient_id} | "
                    f"{priority} | "
                    f"{doctor.name} | "
                    f"{room.name} | "
                    f"{full_time_str}"
                )

            except Exception as e:

                print(
                    "Error saving appointment "
                    f"for {patient.patient_id}: {e}"
                )

        # ----------------------------------------------------
        # Reload UI
        # ----------------------------------------------------

        self.load_data()

        self.data_changed.emit()

        self.show_message(
            "Scheduling Complete",
            "Successfully allocated "
            f"{created_count} new appointment(s).",
            QMessageBox.Information,
        )