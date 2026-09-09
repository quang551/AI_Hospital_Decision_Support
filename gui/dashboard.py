import sys
from datetime import datetime
from pathlib import Path

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.repository import (
    AppointmentRepository,
    DoctorRepository,
    PatientRepository,
    RoomRepository,
)


class DashboardContent(QWidget):

    navigate_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.db_path = PROJECT_ROOT / "hospital.db"

        self.patient_repo = PatientRepository(str(self.db_path))
        self.doctor_repo = DoctorRepository(str(self.db_path))
        self.room_repo = RoomRepository(str(self.db_path))
        self.appointment_repo = AppointmentRepository(str(self.db_path))

        self.build_ui()
        self.load_data()

    # =========================================================
    # BASIC UI HELPERS
    # =========================================================

    def label(
        self,
        text="",
        size=10,
        bold=False,
        color="#172033",
    ):
        lbl = QLabel(text)

        lbl.setFont(
            QFont(
                "Segoe UI",
                size,
                QFont.Bold if bold else QFont.Normal
            )
        )

        lbl.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }}
            """
        )

        return lbl

    def card(self):
        frame = QFrame()

        frame.setStyleSheet(
            """
            QFrame {
                background: #FFFFFF;
                border: none;
                border-radius: 18px;
            }
            """
        )

        frame.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        return frame

    def link_button(self, text):
        btn = QPushButton(text)

        btn.setCursor(Qt.PointingHandCursor)
        btn.setFlat(True)

        btn.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                color: #2563EB;
                font-size: 10px;
                font-weight: 700;
                padding: 4px 0px;
            }

            QPushButton:hover {
                color: #1D4ED8;
            }
            """
        )

        return btn

    def nav(self, index):
        self.navigate_requested.emit(index)

    # =========================================================
    # BUILD UI
    # =========================================================

    def build_ui(self):

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        content = QWidget()

        content.setStyleSheet(
            """
            QWidget {
                background: #F5F7FB;
            }
            """
        )

        main = QVBoxLayout(content)
        main.setContentsMargins(
            28,
            24,
            28,
            30
        )
        main.setSpacing(18)

        # =====================================================
        # HEADER
        # =====================================================

        header = QHBoxLayout()
        header.setSpacing(20)

        header_left = QVBoxLayout()
        header_left.setSpacing(5)

        title = self.label(
            "Tổng quan hệ thống",
            27,
            True,
            "#14213D"
        )

        subtitle = self.label(
            "Theo dõi bệnh nhân, phân loại ưu tiên và lịch khám.",
            11,
            False,
            "#64748B"
        )

        header_left.addWidget(title)
        header_left.addWidget(subtitle)

        header.addLayout(header_left)
        header.addStretch()

        # DATE BOX

        date_box = QFrame()

        date_box.setStyleSheet(
            """
            QFrame {
                background: #FFFFFF;
                border: none;
                border-radius: 14px;
            }
            """
        )

        date_box.setFixedWidth(155)

        date_layout = QVBoxLayout(date_box)
        date_layout.setContentsMargins(
            15,
            10,
            15,
            10
        )
        date_layout.setSpacing(2)

        date_title = self.label(
            "📅HÔM NAY",
            7,
            True,
            "#94A3B8"
        )

        date_title.setAlignment(Qt.AlignRight)

        self.date_label = self.label(
            datetime.now().strftime("%d/%m/%Y"),
            14,
            True,
            "#14213D"
        )

        self.date_label.setAlignment(Qt.AlignRight)

        date_layout.addWidget(date_title)
        date_layout.addWidget(self.date_label)

        header.addWidget(date_box)

        main.addLayout(header)

        # =====================================================
        # STAT CARDS
        # =====================================================

        stats = QGridLayout()
        stats.setHorizontalSpacing(14)
        stats.setVerticalSpacing(14)

        self.stat_total = self.make_stat(
            "👥",
            "TỔNG BỆNH NHÂN",
            "0",
            "Trong hệ thống",
            "#2563EB"
        )

        self.stat_critical = self.make_stat(
            "🚨",
            "KHẨN CẤP",
            "0",
            "CRITICAL",
            "#EF4444"
        )

        self.stat_high = self.make_stat(
            "⚠️",
            "ƯU TIÊN CAO",
            "0",
            "HIGH",
            "#F59E0B"
        )

        self.stat_waiting = self.make_stat(
            "⏳",
            "ĐANG CHỜ",
            "0",
            "Chưa khám",
            "#10B981"
        )

        self.stat_doctors = self.make_stat(
            "👨‍⚕️",
            "BÁC SĨ",
            "0",
            "Đang có dữ liệu",
            "#7C3AED"
        )

        self.stat_rooms = self.make_stat(
            "🏥",
            "PHÒNG KHÁM",
            "0",
            "Đang có dữ liệu",
            "#EA580C"
        )

        stat_list = [
            self.stat_total,
            self.stat_critical,
            self.stat_high,
            self.stat_waiting,
            self.stat_doctors,
            self.stat_rooms,
        ]

        for i, widget in enumerate(stat_list):
            stats.addWidget(widget, 0, i)
            stats.setColumnStretch(i, 1)

        main.addLayout(stats)

        # =====================================================
        # MIDDLE SECTION
        # =====================================================

        middle = QGridLayout()
        middle.setHorizontalSpacing(18)

        # =====================================================
        # PRIORITY CHART
        # =====================================================

        chart_card = self.card()

        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(
            20,
            18,
            20,
            16
        )

        chart_layout.setSpacing(8)

        chart_header = QHBoxLayout()

        chart_header.addWidget(
            self.label(
                "📈 Phân bố mức độ ưu tiên",
                15,
                True,
                "#14213D"
            )
        )

        chart_header.addStretch()

        chart_header.addWidget(
            self.label(
                "Theo dữ liệu real-time",
                9,
                False,
                "#94A3B8"
            )
        )

        chart_layout.addLayout(chart_header)

        self.priority_figure = Figure(
            figsize=(5.2, 2.5),
            dpi=100
        )

        self.priority_figure.patch.set_alpha(0)

        self.priority_canvas = FigureCanvas(
            self.priority_figure
        )

        self.priority_canvas.setMinimumHeight(220)

        chart_layout.addWidget(
            self.priority_canvas
        )

        middle.addWidget(
            chart_card,
            0,
            0
        )

        # =====================================================
        # PRIORITY QUEUE
        # =====================================================

        queue_card = self.card()

        queue_layout = QVBoxLayout(queue_card)

        queue_layout.setContentsMargins(
            20,
            18,
            20,
            16
        )

        queue_layout.setSpacing(8)

        queue_header = QHBoxLayout()

        queue_header.addWidget(
            self.label(
                " 📋 Hàng đợi ưu tiên",
                15,
                True,
                "#14213D"
            )
        )

        queue_header.addStretch()

        self.queue_count = self.label(
            "0 bệnh nhân",
            9,
            True,
            "#2563EB"
        )

        self.queue_count.setStyleSheet(
            """
            QLabel {
                color: #2563EB;
                background: #EEF4FF;
                border: none;
                border-radius: 8px;
                padding: 6px 10px;
            }
            """
        )

        queue_header.addWidget(
            self.queue_count
        )

        queue_layout.addLayout(
            queue_header
        )

        self.queue_table = QTableWidget(
            0,
            5
        )

        self.queue_table.setHorizontalHeaderLabels(
            [
                "#",
                "Mã BN",
                "Họ tên",
                "Ưu tiên",
                "Thời gian chờ"
            ]
        )

        self.setup_table(
            self.queue_table,
            215
        )

        queue_layout.addWidget(
            self.queue_table
        )

        view_patients = self.link_button(
            "Xem tất cả →"
        )
        view_patients.clicked.connect(
            lambda: self.nav(1)
        )

        queue_layout.addWidget(
            view_patients,
            0,
            Qt.AlignLeft
        )

        middle.addWidget(
            queue_card,
            0,
            1
        )

        middle.setColumnStretch(0, 1)
        middle.setColumnStretch(1, 1)

        main.addLayout(middle)

        # =====================================================
        # TODAY SCHEDULE
        # =====================================================

        schedule_card = self.card()

        schedule_layout = QVBoxLayout(
            schedule_card
        )

        schedule_layout.setContentsMargins(
            20,
            18,
            20,
            18
        )

        schedule_layout.setSpacing(10)

        schedule_header = QHBoxLayout()

        schedule_header.addWidget(
            self.label(
                " 📆 Lịch khám hôm nay",
                15,
                True,
                "#14213D"
            )
        )

        schedule_header.addWidget(
            self.label(
                datetime.now().strftime(
                    "%d/%m/%Y"
                ),
                10,
                False,
                "#64748B"
            )
        )

        schedule_header.addStretch()

        view_schedule = self.link_button(
            "Xem lịch đầy đủ →"
        )

        view_schedule.clicked.connect(
            lambda: self.nav(3)
        )

        schedule_header.addWidget(
            view_schedule
        )

        schedule_layout.addLayout(
            schedule_header
        )

        self.schedule_table = QTableWidget(
            0,
            5
        )

        self.schedule_table.setHorizontalHeaderLabels(
            [
                "Thời gian",
                "Mã BN",
                "Bệnh nhân",
                "Bác sĩ",
                "Phòng"
            ]
        )

        self.setup_table(
            self.schedule_table,
            185
        )

        schedule_layout.addWidget(
            self.schedule_table
        )

        main.addWidget(
            schedule_card
        )

        # =====================================================
        # AI CARD
        # =====================================================

        ai_card = QFrame()

        ai_card.setStyleSheet(
            """
            QFrame {
                background: #F0EBFF;
                border: none;
                border-radius: 18px;
            }
            """
        )

        ai_layout = QHBoxLayout(
            ai_card
        )

        ai_layout.setContentsMargins(
            22,
            18,
            22,
            18
        )

        ai_layout.setSpacing(15)

        brain = QLabel("🧠")

        brain.setFixedSize(
            52,
            52
        )

        brain.setAlignment(
            Qt.AlignCenter
        )

        brain.setStyleSheet(
            """
            QLabel {
                background: #FFFFFF;
                border: none;
                border-radius: 26px;
                font-size: 23px;
            }
            """
        )

        ai_layout.addWidget(
            brain
        )

        ai_text = QVBoxLayout()

        ai_text.setSpacing(4)

        ai_text.addWidget(
            self.label(
                "AI Decision Support System",
                16,
                True,
                "#4C1D95"
            )
        )

        ai_text.addWidget(
            self.label(
                "Phân tích triệu chứng và chỉ số sinh tồn "
                "để hỗ trợ đưa ra mức độ ưu tiên theo "
                "thuật toán Chuyên gia.",
                10,
                False,
                "#64748B"
            )
        )

        self.ai_status = self.label(
            "Hệ thống sẵn sàng phân tích.",
            9,
            False,
            "#7C3AED"
        )

        ai_text.addWidget(
            self.ai_status
        )

        ai_layout.addLayout(
            ai_text,
            1
        )

        start_button = QPushButton(
            "Bắt đầu phân tích →"
        )

        start_button.setCursor(
            Qt.PointingHandCursor
        )

        start_button.setFixedHeight(
            42
        )

        start_button.setStyleSheet(
            """
            QPushButton {
                background: #2563EB;
                color: white;
                border: none;
                border-radius: 9px;
                padding: 0px 20px;
                font-size: 10px;
                font-weight: 700;
            }

            QPushButton:hover {
                background: #1D4ED8;
            }

            QPushButton:pressed {
                background: #1E40AF;
            }
            """
        )

        start_button.clicked.connect(
            lambda: self.nav(4)
        )

        ai_layout.addWidget(
            start_button
        )

        main.addWidget(
            ai_card
        )

        # =====================================================
        # FOOTER
        # =====================================================

        footer = self.label(
            "● Trạng thái: Kết nối SQLite ổn định",
            9,
            True,
            "#10B981"
        )

        footer.setAlignment(
            Qt.AlignRight
        )

        main.addWidget(
            footer
        )

        scroll.setWidget(
            content
        )

        root.addWidget(
            scroll
        )

    # =========================================================
    # STAT CARD HELPER
    # =========================================================

    def make_stat(
        self,
        icon,
        title,
        value,
        subtitle,
        accent
    ):

        card = QFrame()

        card.setStyleSheet(
            """
            QFrame {
                background: #FFFFFF;
                border: none;
                border-radius: 16px;
            }
            """
        )

        layout = QHBoxLayout(card)

        layout.setContentsMargins(
            13,
            12,
            13,
            12
        )

        layout.setSpacing(10)

        icon_label = QLabel(icon)

        icon_label.setFixedSize(
            38,
            38
        )

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        icon_label.setStyleSheet(
            f"""
            QLabel {{
                background: {accent};
                color: white;
                border: none;
                border-radius: 19px;
                font-size: 16px;
                font-weight: 700;
            }}
            """
        )

        text = QVBoxLayout()

        text.setSpacing(1)

        text.addWidget(
            self.label(
                title,
                8,
                True,
                "#64748B"
            )
        )

        value_label = self.label(
            value,
            20,
            True,
            "#14213D"
        )

        text.addWidget(
            value_label
        )

        text.addWidget(
            self.label(
                subtitle,
                8,
                False,
                "#94A3B8"
            )
        )

        layout.addWidget(
            icon_label
        )

        layout.addLayout(
            text,
            1
        )

        card.value_label = value_label

        return card

    # =========================================================
    # TABLE SETUP HELPER (ĐÃ CĂN CHỈNH)
    # =========================================================

    def setup_table(
        self,
        table,
        min_height=200
    ):

        table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        table.setSelectionMode(
            QTableWidget.NoSelection
        )

        table.verticalHeader().setVisible(
            False
        )

        table.setShowGrid(
            False
        )

        table.setAlternatingRowColors(
            True
        )

        table.setMinimumHeight(
            min_height
        )

        table.setStyleSheet(
            """
            QTableWidget {
                background: #FFFFFF;
                border: none;
                outline: none;
                color: #172033;
                font-size: 10px;
                alternate-background-color: #F8FAFC;
                gridline-color: transparent;
            }

            QTableWidget::item {
                border: none;
                padding: 6px 12px;
            }

            QHeaderView {
                border: none;
                background: transparent;
            }

            QHeaderView::section {
                background: #F4F7FB;
                color: #64748B;
                border: none;
                padding: 8px 12px;
                font-size: 9px;
                font-weight: 700;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 5px;
                border: none;
            }

            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 2px;
                min-height: 30px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            """
        )

    # =========================================================
    # APPOINTMENT DATETIME HELPER
    # =========================================================

    def get_appointment_datetime(
        self,
        appointment
    ):

        raw = str(
            getattr(
                appointment,
                "time",
                ""
            )
        ).strip()

        if not raw:
            return None

        formats = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(
                    raw,
                    fmt
                )
            except ValueError:
                pass

        try:
            parsed = datetime.strptime(
                raw,
                "%H:%M"
            )

            return datetime.combine(
                datetime.now().date(),
                parsed.time()
            )
        except ValueError:
            return None

    # =========================================================
    # LOAD REAL DATABASE DATA
    # =========================================================

    def load_data(self):

        try:
            patients = (
                self.patient_repo
                .get_all_patients()
            )

            doctors = (
                self.doctor_repo
                .get_all_doctors()
            )

            rooms = (
                self.room_repo
                .get_all_rooms()
            )

            appointments = (
                self.appointment_repo
                .get_all_appointments()
            )

            # STATISTICS
            critical_count = sum(
                1
                for p in patients
                if str(
                    getattr(
                        p,
                        "priority",
                        ""
                    )
                ).upper() == "CRITICAL"
            )

            high_count = sum(
                1
                for p in patients
                if str(
                    getattr(
                        p,
                        "priority",
                        ""
                    )
                ).upper() == "HIGH"
            )

            self.stat_total.value_label.setText(
                str(len(patients))
            )

            self.stat_critical.value_label.setText(
                str(critical_count)
            )

            self.stat_high.value_label.setText(
                str(high_count)
            )

            self.stat_waiting.value_label.setText(
                str(len(patients))
            )

            self.stat_doctors.value_label.setText(
                str(len(doctors))
            )

            self.stat_rooms.value_label.setText(
                str(len(rooms))
            )

            # PRIORITY QUEUE
            priority_patients = [
                p
                for p in patients
                if str(
                    getattr(
                        p,
                        "priority",
                        "LOW"
                    )
                ).upper()
                in {
                    "CRITICAL",
                    "HIGH",
                    "MEDIUM",
                    "LOW"
                }
            ]

            self.queue_count.setText(
                f"{len(priority_patients)} bệnh nhân"
            )

            self.populate_priority_table(
                priority_patients
            )

            # SCHEDULE
            self.populate_schedule_table(
                appointments
            )

            # CHART
            self.update_priority_chart(
                patients
            )

            # STATUS
            self.ai_status.setText(
                f"Tải thành công: "
                f"{len(patients)} bệnh nhân | "
                f"{len(appointments)} lịch khám."
            )

            self.date_label.setText(
                datetime.now().strftime(
                    "%d/%m/%Y"
                )
            )

        except Exception as e:
            print(
                "Dashboard load error:",
                e
            )

            self.ai_status.setText(
                f"Lỗi tải dữ liệu: {e}"
            )

    # =========================================================
    # POPULATE PRIORITY TABLE (CĂN HÀNG CỘT THẲNG HÀNG)
    # =========================================================

    def populate_priority_table(
        self,
        patients
    ):

        order = {
            "CRITICAL": 0,
            "HIGH": 1,
            "MEDIUM": 2,
            "LOW": 3
        }

        patients = sorted(
            patients,
            key=lambda p: (
                order.get(
                    str(
                        getattr(
                            p,
                            "priority",
                            "LOW"
                        )
                    ).upper(),
                    3
                ),
                -int(
                    getattr(
                        p,
                        "waiting_time",
                        0
                    ) or 0
                )
            )
        )[:6]

        self.queue_table.setRowCount(0)

        header = self.queue_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)

        self.queue_table.setColumnWidth(1, 90)
        self.queue_table.setColumnWidth(3, 110)
        self.queue_table.setColumnWidth(4, 120)

        alignments = [
            Qt.AlignCenter,
            Qt.AlignVCenter | Qt.AlignLeft,
            Qt.AlignVCenter | Qt.AlignLeft,
            Qt.AlignVCenter | Qt.AlignLeft,
            Qt.AlignVCenter | Qt.AlignLeft
        ]

        # Đồng bộ căn lề của Header với dữ liệu bên dưới
        for col in range(5):
            header_item = self.queue_table.horizontalHeaderItem(col)
            if header_item:
                header_item.setTextAlignment(alignments[col])

        for i, patient in enumerate(patients, 1):
            row = self.queue_table.rowCount()
            self.queue_table.insertRow(row)

            priority = str(
                getattr(
                    patient,
                    "priority",
                    "LOW"
                )
            ).upper()

            values = [
                str(i),
                str(getattr(patient, "patient_id", "")),
                str(getattr(patient, "name", "")),
                priority,
                f"{getattr(patient, 'waiting_time', 0)} phút",
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(alignments[col])

                if col == 3:
                    if priority == "CRITICAL":
                        item.setForeground(Qt.red)
                    elif priority in ("HIGH", "MEDIUM"):
                        item.setForeground(Qt.darkYellow)
                    else:
                        item.setForeground(Qt.darkGreen)

                self.queue_table.setItem(row, col, item)

    # =========================================================
    # POPULATE TODAY SCHEDULE (CĂN HÀNG CỘT THẲNG HÀNG)
    # =========================================================

    def populate_schedule_table(
        self,
        appointments
    ):

        today = datetime.now().date()
        rows = []

        for appointment in appointments:
            dt = self.get_appointment_datetime(appointment)

            if dt is None:
                continue

            if dt.date() != today:
                continue

            rows.append(
                (
                    dt,
                    str(getattr(appointment.patient, "patient_id", "")),
                    str(getattr(appointment.patient, "name", "")),
                    str(getattr(appointment.doctor, "name", "")),
                    str(getattr(appointment.room, "name", ""))
                )
            )

        rows.sort(key=lambda x: x[0])
        rows = rows[:8]

        self.schedule_table.setRowCount(0)

        header = self.schedule_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Interactive)

        self.schedule_table.setColumnWidth(0, 90)
        self.schedule_table.setColumnWidth(1, 90)
        self.schedule_table.setColumnWidth(4, 100)

        alignments = [
            Qt.AlignCenter,
            Qt.AlignVCenter | Qt.AlignLeft,
            Qt.AlignVCenter | Qt.AlignLeft,
            Qt.AlignVCenter | Qt.AlignLeft,
            Qt.AlignVCenter | Qt.AlignLeft
        ]

        for col in range(5):
            header_item = self.schedule_table.horizontalHeaderItem(col)
            if header_item:
                header_item.setTextAlignment(alignments[col])

        if not rows:
            self.schedule_table.setRowCount(1)
            item = QTableWidgetItem("No appointments scheduled for today")
            item.setTextAlignment(Qt.AlignCenter)
            self.schedule_table.setSpan(0, 0, 1, 5)
            self.schedule_table.setItem(0, 0, item)
            return

        for dt, patient_id, patient_name, doctor_name, room_name in rows:
            row = self.schedule_table.rowCount()
            self.schedule_table.insertRow(row)

            values = [
                dt.strftime("%H:%M"),
                patient_id,
                patient_name,
                doctor_name,
                room_name
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(alignments[col])
                self.schedule_table.setItem(row, col, item)

    # =========================================================
    # UPDATE PRIORITY DONUT CHART
    # =========================================================

    def update_priority_chart(
        self,
        patients
    ):

        self.priority_figure.clear()

        priority_order = [
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW"
        ]

        labels = [
            "Critical",
            "High",
            "Medium",
            "Low"
        ]

        colors = [
            "#EF4444",
            "#F59E0B",
            "#3B82F6",
            "#10B981"
        ]

        counts = [0, 0, 0, 0]
        for p in patients:
            p_val = str(getattr(p, "priority", "LOW")).upper()
            if p_val in priority_order:
                idx = priority_order.index(p_val)
                counts[idx] += 1

        total = sum(counts)

        ax = self.priority_figure.add_subplot(111)

        if total == 0:
            ax.text(
                0.5, 0.5,
                "No data available",
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax.transAxes,
                color='#94A3B8',
                fontsize=12
            )
            ax.axis('off')
        else:
            wedges, texts, autotexts = ax.pie(
                counts,
                labels=None,
                autopct=lambda pct: f"{pct:.1f}%" if pct > 0 else "",
                startangle=140,
                colors=colors,
                pctdistance=0.75,
                wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
            )

            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(8)
                autotext.set_weight('bold')

            ax.legend(
                wedges,
                [f"{lbl} ({cnt})" for lbl, cnt in zip(labels, counts)],
                loc="center left",
                bbox_to_anchor=(0.9, 0.5),
                frameon=False,
                fontsize=9
            )

            ax.axis('equal')

        self.priority_figure.tight_layout()
        self.priority_canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    dashboard = DashboardContent()
    window.setCentralWidget(dashboard)
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())