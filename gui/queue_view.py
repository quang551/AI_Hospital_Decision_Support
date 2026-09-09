# gui/queue_view.py

from pathlib import Path

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
    QHeaderView,
    QFrame,
    QMessageBox,
)

from database.repository import PatientRepository


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "hospital.db"


# ============================================================
# DESIGN CONSTANTS
# ============================================================

BG_MAIN = "#F8FAFC"
CARD_BG = "#FFFFFF"
BORDER_COLOR = "#E2E8F0"

TEXT_PRIMARY = "#0F172A"
TEXT_MUTED = "#64748B"

PRIMARY_BLUE = "#2563EB"
PRIMARY_LIGHT = "#EFF6FF"

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

def create_queue_badge(text, level):
    level_str = str(level).upper()

    if "CRITICAL" in level_str:
        bg = COLOR_CRITICAL_BG
        fg = COLOR_CRITICAL_TEXT

    elif "HIGH" in level_str:
        bg = COLOR_HIGH_BG
        fg = COLOR_HIGH_TEXT

    elif "MEDIUM" in level_str:
        bg = COLOR_MEDIUM_BG
        fg = COLOR_MEDIUM_TEXT

    else:
        bg = COLOR_LOW_BG
        fg = COLOR_LOW_TEXT

    container = QWidget()

    layout = QHBoxLayout(container)
    layout.setContentsMargins(4, 2, 4, 2)
    layout.setAlignment(Qt.AlignCenter)

    label = QLabel(str(text))
    label.setAlignment(Qt.AlignCenter)
    label.setFont(QFont("Segoe UI", 9, QFont.Bold))
    label.setFixedHeight(24)

    label.setStyleSheet(
        f"""
        QLabel {{
            background-color: {bg};
            color: {fg};
            border-radius: 6px;
            padding-left: 10px;
            padding-right: 10px;
            border: none;
        }}
        """
    )

    layout.addWidget(label)

    return container


# ============================================================
# QUEUE VIEW
# ============================================================

class QueueView(QWidget):

    queue_updated = Signal()

    def __init__(self, database=None, parent=None):
        super().__init__(parent)

        # database có thể là PatientRepository
        # hoặc None.
        self.db = database

        self.repository = self._create_repository()

        self.setStyleSheet(
            f"""
            QWidget {{
                font-family: "Segoe UI";
            }}
            """
        )

        self.setup_ui()

        # Load dữ liệu ngay khi mở Queue
        self.load_queue()

    # ========================================================
    # DATABASE
    # ========================================================

    def _create_repository(self):

        # ----------------------------------------------------
        # Trường hợp MainWindow truyền PatientRepository
        # ----------------------------------------------------

        if self.db is not None:
            if hasattr(self.db, "get_all_patients"):
                return self.db

        # ----------------------------------------------------
        # Nếu không có database được truyền vào
        # thì tự động dùng hospital.db của project
        # ----------------------------------------------------

        return PatientRepository(str(DB_PATH))

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            24,
            20,
            24,
            24
        )

        main_layout.setSpacing(16)

        # ====================================================
        # HEADER
        # ====================================================

        header_layout = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(3)

        title = QLabel("Priority Queue")

        title.setFont(
            QFont(
                "Segoe UI",
                18,
                QFont.Bold
            )
        )

        title.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            border: none;
            """
        )

        subtitle = QLabel(
            "Monitor and prioritize patients based on their priority level"
        )

        subtitle.setFont(
            QFont(
                "Segoe UI",
                10
            )
        )

        subtitle.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            border: none;
            """
        )

        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        header_layout.addLayout(title_box)
        header_layout.addStretch()

        # ----------------------------------------------------
        # Refresh button
        # ----------------------------------------------------

        btn_refresh = QPushButton("↻  Refresh")

        btn_refresh.setCursor(
            Qt.PointingHandCursor
        )

        btn_refresh.setFixedHeight(36)

        btn_refresh.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 7px;
                padding-left: 14px;
                padding-right: 14px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background-color: {PRIMARY_LIGHT};
                border-color: {PRIMARY_BLUE};
                color: {PRIMARY_BLUE};
            }}

            QPushButton:pressed {{
                background-color: #DBEAFE;
            }}
            """
        )

        btn_refresh.clicked.connect(
            self.load_queue
        )

        header_layout.addWidget(
            btn_refresh
        )

        main_layout.addLayout(
            header_layout
        )

        # ====================================================
        # SUMMARY CARDS
        # ====================================================

        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(16)

        self.card_total = self.create_summary_card(
            "TOTAL QUEUE",
            "0",
            "Patients in queue",
            TEXT_PRIMARY,
            PRIMARY_BLUE
        )

        self.card_critical = self.create_summary_card(
            "CRITICAL",
            "0",
            "Emergency cases",
            COLOR_CRITICAL_TEXT,
            COLOR_CRITICAL_TEXT
        )

        self.card_high = self.create_summary_card(
            "HIGH",
            "0",
            "High priority",
            COLOR_HIGH_TEXT,
            COLOR_HIGH_TEXT
        )

        self.card_normal = self.create_summary_card(
            "MEDIUM / LOW",
            "0",
            "Normal priority",
            COLOR_LOW_TEXT,
            COLOR_LOW_TEXT
        )

        kpi_layout.addWidget(
            self.card_total
        )

        kpi_layout.addWidget(
            self.card_critical
        )

        kpi_layout.addWidget(
            self.card_high
        )

        kpi_layout.addWidget(
            self.card_normal
        )

        main_layout.addLayout(
            kpi_layout
        )

        # ====================================================
        # TABLE CARD
        # ====================================================

        table_card = QFrame()

        table_card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 12px;
            }}
            """
        )

        card_layout = QVBoxLayout(
            table_card
        )

        card_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        card_layout.setSpacing(14)

        # ----------------------------------------------------
        # Table header
        # ----------------------------------------------------

        table_header = QHBoxLayout()

        list_title = QLabel(
            "Patients Waiting"
        )

        list_title.setFont(
            QFont(
                "Segoe UI",
                13,
                QFont.Bold
            )
        )

        list_title.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            border: none;
            """
        )

        table_header.addWidget(
            list_title
        )

        table_header.addStretch()

        # ----------------------------------------------------
        # Search
        # ----------------------------------------------------

        self.txt_search = QLineEdit()

        self.txt_search.setPlaceholderText(
            "🔍  Search patient ID or name..."
        )

        self.txt_search.setFixedHeight(36)
        self.txt_search.setFixedWidth(280)

        self.txt_search.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: #F8FAFC;
                border: 1px solid {BORDER_COLOR};
                border-radius: 7px;
                padding-left: 12px;
                color: {TEXT_PRIMARY};
            }}

            QLineEdit:focus {{
                border: 1px solid {PRIMARY_BLUE};
                background-color: #FFFFFF;
            }}
            """
        )

        self.txt_search.textChanged.connect(
            self.filter_queue
        )

        table_header.addWidget(
            self.txt_search
        )

        card_layout.addLayout(
            table_header
        )

        # ====================================================
        # TABLE
        # ====================================================

        self.table = QTableWidget(
            0,
            9
        )

        self.table.setHorizontalHeaderLabels(
            [
                "NO.",
                "PATIENT ID",
                "NAME",
                "AGE",
                "SYMPTOMS",
                "SEVERITY",
                "EMERGENCY",
                "WAITING TIME",
                "PRIORITY",
            ]
        )

        # Hide vertical header
        self.table.verticalHeader().setVisible(
            False
        )

        # No grid
        self.table.setShowGrid(
            False
        )

        self.table.setFrameShape(
            QFrame.NoFrame
        )

        # Row height
        self.table.verticalHeader().setDefaultSectionSize(
            48
        )

        # Table stylesheet
        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: transparent;
                border: none;
                color: {TEXT_PRIMARY};
                font-size: 10pt;
            }}

            QTableWidget::item {{
                border-bottom: 1px solid {BORDER_COLOR};
                padding: 6px;
            }}

            QTableWidget::item:selected {{
                background-color: {PRIMARY_LIGHT};
                color: {TEXT_PRIMARY};
            }}

            QHeaderView::section {{
                background-color: transparent;
                color: {TEXT_MUTED};
                font-weight: bold;
                font-size: 9pt;
                border: none;
                border-bottom: 2px solid {BORDER_COLOR};
                padding-bottom: 9px;
            }}
            """
        )

        # ----------------------------------------------------
        # Column sizes
        # ----------------------------------------------------

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents
        )

        card_layout.addWidget(
            self.table
        )

        main_layout.addWidget(
            table_card,
            1
        )

        # ====================================================
        # FOOTER
        # ====================================================

        footer_layout = QHBoxLayout()

        rule_label = QLabel(
            "💡 Priority: CRITICAL → HIGH → MEDIUM → LOW"
        )

        rule_label.setFont(
            QFont(
                "Segoe UI",
                9,
                QFont.Bold
            )
        )

        rule_label.setStyleSheet(
            f"""
            color: {PRIMARY_BLUE};
            border: none;
            """
        )

        self.lbl_count_footer = QLabel(
            "Showing 0 / 0 patients"
        )

        self.lbl_count_footer.setFont(
            QFont(
                "Segoe UI",
                9
            )
        )

        self.lbl_count_footer.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            border: none;
            """
        )

        footer_layout.addWidget(
            rule_label
        )

        footer_layout.addStretch()

        footer_layout.addWidget(
            self.lbl_count_footer
        )

        main_layout.addLayout(
            footer_layout
        )

    # ========================================================
    # SUMMARY CARD
    # ========================================================

    def create_summary_card(
        self,
        title,
        count,
        subtitle,
        count_color,
        border_left_color
    ):

        card = QFrame()

        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
                border-left: 4px solid {border_left_color};
                border-radius: 8px;
            }}
            """
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            16,
            12,
            16,
            12
        )

        layout.setSpacing(4)

        title_label = QLabel(
            title
        )

        title_label.setFont(
            QFont(
                "Segoe UI",
                9,
                QFont.Bold
            )
        )

        title_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            border: none;
            """
        )

        count_label = QLabel(
            count
        )

        count_label.setFont(
            QFont(
                "Segoe UI",
                20,
                QFont.Bold
            )
        )

        count_label.setStyleSheet(
            f"""
            color: {count_color};
            border: none;
            """
        )

        subtitle_label = QLabel(
            subtitle
        )

        subtitle_label.setFont(
            QFont(
                "Segoe UI",
                9
            )
        )

        subtitle_label.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            border: none;
            """
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            count_label
        )

        layout.addWidget(
            subtitle_label
        )

        return card

    # ========================================================
    # LOAD QUEUE FROM DATABASE
    # ========================================================

    def load_queue(self):

        try:

            # -----------------------------------------------
            # ALWAYS READ CURRENT DATA FROM hospital.db
            # -----------------------------------------------

            patients = self.repository.get_all_patients()

            data = []

            for patient in patients:

                symptoms = patient.symptoms

                if isinstance(symptoms, list):
                    symptoms_text = ", ".join(
                        str(x).strip()
                        for x in symptoms
                        if str(x).strip()
                    )

                else:
                    symptoms_text = str(
                        symptoms or ""
                    )

                priority = (
                    patient.priority
                    if patient.priority
                    else "LOW"
                )

                waiting_time = (
                    patient.waiting_time
                    if patient.waiting_time is not None
                    else 0
                )

                data.append(
                    (
                        patient.patient_id,
                        patient.name,
                        patient.age,
                        symptoms_text,
                        patient.severity,
                        patient.emergency,
                        f"{waiting_time} min",
                        priority
                    )
                )

            # -----------------------------------------------
            # Display
            # -----------------------------------------------

            self.display_queue(
                data
            )

            self.queue_updated.emit()

        except Exception as e:

            print(
                "Queue database error:",
                e
            )

            self.display_queue([])

            QMessageBox.warning(
                self,
                "Database Error",
                f"Unable to load patients.\n\n{e}"
            )

    # ========================================================
    # DISPLAY DATA
    # ========================================================

    def display_queue(
        self,
        data
    ):

        self.table.setRowCount(
            0
        )

        critical_count = 0
        high_count = 0
        normal_count = 0

        # ----------------------------------------------------
        # Sort priority
        # ----------------------------------------------------

        priority_order = {
            "CRITICAL": 1,
            "HIGH": 2,
            "MEDIUM": 3,
            "LOW": 4
        }

        data = sorted(
            data,
            key=lambda row: priority_order.get(
                str(row[7]).upper(),
                4
            )
        )

        # ----------------------------------------------------
        # Add rows
        # ----------------------------------------------------

        for idx, row in enumerate(data):

            self.table.insertRow(
                idx
            )

            code = row[0]
            name = row[1]
            age = row[2]
            symptoms = row[3]
            severity = row[4]
            emergency = row[5]
            waiting_time = row[6]
            priority = row[7]

            # =================================================
            # KPI COUNT
            # =================================================

            priority_upper = str(
                priority
            ).upper()

            if priority_upper == "CRITICAL":

                critical_count += 1

            elif priority_upper == "HIGH":

                high_count += 1

            else:

                normal_count += 1

            # =================================================
            # NO.
            # =================================================

            no_item = QTableWidgetItem(
                str(idx + 1)
            )

            no_item.setTextAlignment(
                Qt.AlignCenter
            )

            self.table.setItem(
                idx,
                0,
                no_item
            )

            # =================================================
            # PATIENT ID
            # =================================================

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
                idx,
                1,
                code_item
            )

            # =================================================
            # NAME
            # =================================================

            self.table.setItem(
                idx,
                2,
                QTableWidgetItem(
                    str(name)
                )
            )

            # =================================================
            # AGE
            # =================================================

            age_item = QTableWidgetItem(
                str(age)
            )

            age_item.setTextAlignment(
                Qt.AlignCenter
            )

            self.table.setItem(
                idx,
                3,
                age_item
            )

            # =================================================
            # SYMPTOMS
            # =================================================

            self.table.setItem(
                idx,
                4,
                QTableWidgetItem(
                    str(symptoms)
                )
            )

            # =================================================
            # SEVERITY
            # =================================================

            self.table.setItem(
                idx,
                5,
                QTableWidgetItem(
                    str(severity)
                )
            )

            # =================================================
            # EMERGENCY
            # =================================================

            emergency_item = QTableWidgetItem(
                str(emergency)
            )

            emergency_upper = str(
                emergency
            ).upper()

            if emergency_upper in (
                "HIGH",
                "CRITICAL"
            ):

                emergency_item.setFont(
                    QFont(
                        "Segoe UI",
                        9,
                        QFont.Bold
                    )
                )

                emergency_item.setForeground(
                    Qt.GlobalColor.red
                )

            self.table.setItem(
                idx,
                6,
                emergency_item
            )

            # =================================================
            # WAITING TIME
            # =================================================

            wait_item = QTableWidgetItem(
                str(waiting_time)
            )

            wait_item.setTextAlignment(
                Qt.AlignCenter
            )

            self.table.setItem(
                idx,
                7,
                wait_item
            )

            # =================================================
            # PRIORITY BADGE
            # =================================================

            badge = create_queue_badge(
                str(priority),
                priority
            )

            self.table.setCellWidget(
                idx,
                8,
                badge
            )

        # ====================================================
        # UPDATE KPI
        # ====================================================

        total_count = len(
            data
        )

        self.card_total.findChildren(
            QLabel
        )[1].setText(
            str(total_count)
        )

        self.card_critical.findChildren(
            QLabel
        )[1].setText(
            str(critical_count)
        )

        self.card_high.findChildren(
            QLabel
        )[1].setText(
            str(high_count)
        )

        self.card_normal.findChildren(
            QLabel
        )[1].setText(
            str(normal_count)
        )

        # ====================================================
        # FOOTER
        # ====================================================

        self.lbl_count_footer.setText(
            f"Showing {total_count} / {total_count} patients"
        )

    # ========================================================
    # SEARCH
    # ========================================================

    def filter_queue(
        self
    ):

        text = (
            self.txt_search
            .text()
            .strip()
            .lower()
        )

        visible_count = 0

        for row in range(
            self.table.rowCount()
        ):

            code_item = self.table.item(
                row,
                1
            )

            name_item = self.table.item(
                row,
                2
            )

            if not code_item or not name_item:
                continue

            code = (
                code_item
                .text()
                .lower()
            )

            name = (
                name_item
                .text()
                .lower()
            )

            match = (
                text in code
                or text in name
            )

            self.table.setRowHidden(
                row,
                not match
            )

            if match:
                visible_count += 1

        total_count = self.table.rowCount()

        self.lbl_count_footer.setText(
            f"Showing {visible_count} / {total_count} patients"
        )


# ============================================================
# ALIAS
# ============================================================

PriorityQueueView = QueueView