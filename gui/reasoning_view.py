# gui/reasoning_view.py

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QComboBox,
    QTextEdit,
    QMessageBox,
    QScrollArea,
    QGraphicsDropShadowEffect,
)

# ============================================================
# FIX IMPORT CHO CODE KNOWLEDGE CỦA NHÓM
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(KNOWLEDGE_DIR) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_DIR))

from knowledge.facts import extract_facts_from_patient
from knowledge.rules import get_default_knowledge_base
from knowledge.inference_engine import InferenceEngine

from database.repository import PatientRepository


# ============================================================
# DESIGN SYSTEM
# ============================================================

BG_MAIN = "#F8FAFC"
CARD_BG = "#FFFFFF"
BORDER_COLOR = "#E2E8F0"

NAVY = "#0F172A"
TEXT_PRIMARY = "#1E293B"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#94A3B8"

BLUE = "#2563EB"
BLUE_LIGHT = "#EFF6FF"
BLUE_BORDER = "#BFDBFE"

RED = "#DC2626"
RED_LIGHT = "#FEF2F2"
RED_BORDER = "#FECACA"

ORANGE = "#EA580C"
ORANGE_LIGHT = "#FFF7ED"
ORANGE_BORDER = "#FED7AA"

GREEN = "#16A34A"
GREEN_LIGHT = "#F0FDF4"
GREEN_BORDER = "#BBF7D0"

PURPLE = "#7C3AED"
PURPLE_LIGHT = "#FAF5FF"
PURPLE_BORDER = "#E9D5FF"


# ============================================================
# HELPER
# ============================================================

def apply_shadow(widget, blur=12, opacity=0.04, offset_y=3):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setColor(QColor(15, 23, 42, int(255 * opacity)))
    shadow.setOffset(0, offset_y)
    widget.setGraphicsEffect(shadow)


def create_card_frame():
    card = QFrame()
    card.setStyleSheet(
        f"""
        QFrame {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER_COLOR};
            border-radius: 12px;
        }}
        """
    )
    apply_shadow(card)
    return card


# ============================================================
# RESULT METRIC BOX
# ============================================================

class ResultMetricBox(QFrame):

    def __init__(
        self,
        title,
        default_val="--",
        bg_color=BG_MAIN,
        border_color=BORDER_COLOR,
        text_color=TEXT_PRIMARY
    ):
        super().__init__()

        self.setObjectName("MetricBox")

        self.update_style(bg_color, border_color)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        lbl_title = QLabel(title.upper())
        lbl_title.setFont(QFont("Segoe UI", 8, QFont.Bold))
        lbl_title.setStyleSheet(
            f"""
            color: {TEXT_MUTED};
            border: none;
            background: transparent;
            """
        )

        self.lbl_value = QLabel(default_val)
        self.lbl_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.lbl_value.setStyleSheet(
            f"""
            color: {text_color};
            border: none;
            background: transparent;
            """
        )

        layout.addWidget(lbl_title)
        layout.addWidget(self.lbl_value)

    def update_style(self, bg_color, border_color):
        self.setStyleSheet(
            f"""
            QFrame#MetricBox {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 10px;
            }}
            """
        )

    def set_value(
        self,
        value,
        color,
        bg_color=None,
        border_color=None
    ):
        self.lbl_value.setText(str(value))

        self.lbl_value.setStyleSheet(
            f"""
            color: {color};
            border: none;
            background: transparent;
            """
        )

        if bg_color and border_color:
            self.update_style(bg_color, border_color)


# ============================================================
# REASONING VIEW
# ============================================================

class ReasoningView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Database
        self.db_path = str(PROJECT_ROOT / "hospital.db")

        self.patient_repository = PatientRepository(
            self.db_path
        )

        # Danh sách bệnh nhân
        self.patients = []

        # Bệnh nhân hiện tại
        self.current_patient = None

        self.setup_ui()
        self.load_patients()

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {BG_MAIN};
                font-family: 'Segoe UI', sans-serif;
            }}

            QComboBox {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 0px 12px;
                color: {TEXT_PRIMARY};
                font-size: 11px;
                font-weight: 500;
            }}

            QComboBox:focus {{
                border: 1px solid {BLUE};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            """
        )

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(
            f"background-color: {BG_MAIN}; border: none;"
        )

        scroll_content = QWidget()

        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(20)

        # ====================================================
        # 1. HEADER
        # ====================================================

        header = QHBoxLayout()

        title_box = QVBoxLayout()
        title_box.setSpacing(4)

        lbl_title = QLabel("AI Reasoning Engine")
        lbl_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        lbl_title.setStyleSheet(
            f"color: {NAVY}; border: none;"
        )

        lbl_sub = QLabel(
            "Phân tích lâm sàng và đưa ra quyết định xử lý "
            "dựa trên suy luận tiến (Forward Chaining)"
        )

        lbl_sub.setFont(QFont("Segoe UI", 10))
        lbl_sub.setStyleSheet(
            f"color: {TEXT_SECONDARY}; border: none;"
        )

        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)

        header.addLayout(title_box)
        header.addStretch()

        self.refresh_button = QPushButton("↻  Làm mới")
        self.refresh_button.setFixedHeight(40)
        self.refresh_button.setCursor(Qt.PointingHandCursor)

        self.refresh_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {CARD_BG};
                color: {NAVY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 0px 16px;
                font-size: 11px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background-color: {BLUE_LIGHT};
                border-color: {BLUE};
                color: {BLUE};
            }}
            """
        )

        self.refresh_button.clicked.connect(self.load_patients)

        header.addWidget(self.refresh_button)

        main_layout.addLayout(header)

        # ====================================================
        # 2. CHỌN BỆNH NHÂN
        # ====================================================

        select_card = create_card_frame()

        select_layout = QVBoxLayout(select_card)
        select_layout.setContentsMargins(20, 18, 20, 18)
        select_layout.setSpacing(12)

        lbl_select_title = QLabel(
            "Chọn bệnh nhân để phân tích"
        )

        lbl_select_title.setFont(
            QFont("Segoe UI", 11, QFont.Bold)
        )

        lbl_select_title.setStyleSheet(
            f"color: {NAVY}; border: none;"
        )

        select_layout.addWidget(lbl_select_title)

        control_row = QHBoxLayout()
        control_row.setSpacing(12)

        # ----------------------------------------------------
        # COMBO BỆNH NHÂN
        # ----------------------------------------------------

        self.patient_combo = QComboBox()
        self.patient_combo.setFixedHeight(42)

        # Khi đổi bệnh nhân -> cập nhật thông tin
        self.patient_combo.currentIndexChanged.connect(
            self.on_patient_changed
        )

        control_row.addWidget(
            self.patient_combo,
            1
        )

        # ----------------------------------------------------
        # BUTTON PHÂN TÍCH
        # ----------------------------------------------------

        self.analyze_button = QPushButton(
            "✦  Phân tích ngay"
        )

        self.analyze_button.setFixedHeight(42)
        self.analyze_button.setFixedWidth(160)
        self.analyze_button.setCursor(
            Qt.PointingHandCursor
        )

        self.analyze_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {BLUE};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 11px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background-color: #1D4ED8;
            }}

            QPushButton:pressed {{
                background-color: #1E40AF;
            }}
            """
        )

        self.analyze_button.clicked.connect(
            self.run_reasoning
        )

        control_row.addWidget(
            self.analyze_button
        )

        select_layout.addLayout(control_row)

        main_layout.addWidget(select_card)

        # ====================================================
        # 3. PATIENT INFO
        # ====================================================

        self.patient_card = QFrame()

        self.patient_card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {BLUE_LIGHT};
                border: 1px solid {BLUE_BORDER};
                border-radius: 10px;
            }}
            """
        )

        patient_layout = QHBoxLayout(
            self.patient_card
        )

        patient_layout.setContentsMargins(
            16, 12, 16, 12
        )

        self.patient_info = QLabel(
            "Chưa chọn bệnh nhân"
        )

        self.patient_info.setFont(
            QFont("Segoe UI", 10)
        )

        self.patient_info.setStyleSheet(
            f"""
            color: {TEXT_PRIMARY};
            border: none;
            """
        )

        patient_layout.addWidget(
            self.patient_info
        )

        main_layout.addWidget(
            self.patient_card
        )

        # ====================================================
        # 4. FACTS + RULES
        # ====================================================

        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        # ----------------------------------------------------
        # FACTS
        # ----------------------------------------------------

        facts_card = create_card_frame()

        facts_layout = QVBoxLayout(
            facts_card
        )

        facts_layout.setContentsMargins(
            18, 16, 18, 16
        )

        facts_layout.setSpacing(12)

        lbl_facts_head = QLabel(
            "FACTS ĐẦU VÀO"
        )

        lbl_facts_head.setFont(
            QFont("Segoe UI", 11, QFont.Bold)
        )

        lbl_facts_head.setStyleSheet(
            f"color: {NAVY}; border: none;"
        )

        facts_layout.addWidget(
            lbl_facts_head
        )

        self.facts_text = QTextEdit()
        self.facts_text.setReadOnly(True)
        self.facts_text.setMinimumHeight(240)

        self.facts_text.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {BG_MAIN};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 12px;
                color: {TEXT_PRIMARY};
                font-size: 11px;
            }}
            """
        )

        facts_layout.addWidget(
            self.facts_text
        )

        content_layout.addWidget(
            facts_card,
            1
        )

        # ----------------------------------------------------
        # RULES
        # ----------------------------------------------------

        rules_card = create_card_frame()

        rules_layout = QVBoxLayout(
            rules_card
        )

        rules_layout.setContentsMargins(
            18, 16, 18, 16
        )

        rules_layout.setSpacing(12)

        lbl_rules_head = QLabel(
            " RULES KÍCH HOẠT"
        )

        lbl_rules_head.setFont(
            QFont("Segoe UI", 11, QFont.Bold)
        )

        lbl_rules_head.setStyleSheet(
            f"color: {PURPLE}; border: none;"
        )

        rules_layout.addWidget(
            lbl_rules_head
        )

        self.rules_text = QTextEdit()
        self.rules_text.setReadOnly(True)
        self.rules_text.setMinimumHeight(240)

        self.rules_text.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {PURPLE_LIGHT};
                border: 1px solid {PURPLE_BORDER};
                border-radius: 8px;
                padding: 12px;
                color: {TEXT_PRIMARY};
                font-size: 11px;
            }}
            """
        )

        rules_layout.addWidget(
            self.rules_text
        )

        content_layout.addWidget(
            rules_card,
            1
        )

        main_layout.addLayout(
            content_layout
        )

        # ====================================================
        # 5. CONCLUSION
        # ====================================================

        conclusion_card = create_card_frame()

        conclusion_layout = QVBoxLayout(
            conclusion_card
        )

        conclusion_layout.setContentsMargins(
            20, 18, 20, 18
        )

        conclusion_layout.setSpacing(14)

        lbl_conc_head = QLabel(
            " KẾT LUẬN AI & TIẾN TRÌNH SUY LUẬN"
        )

        lbl_conc_head.setFont(
            QFont("Segoe UI", 11, QFont.Bold)
        )

        lbl_conc_head.setStyleSheet(
            f"color: {NAVY}; border: none;"
        )

        conclusion_layout.addWidget(
            lbl_conc_head
        )

        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(16)

        self.risk_box = ResultMetricBox(
            "Mức độ rủi ro",
            "--",
            BG_MAIN,
            BORDER_COLOR,
            TEXT_PRIMARY
        )

        self.priority_box = ResultMetricBox(
            "Mức độ ưu tiên",
            "--",
            BG_MAIN,
            BORDER_COLOR,
            TEXT_PRIMARY
        )

        metrics_row.addWidget(
            self.risk_box,
            1
        )

        metrics_row.addWidget(
            self.priority_box,
            1
        )

        metrics_row.addStretch(1)

        conclusion_layout.addLayout(
            metrics_row
        )

        # ----------------------------------------------------
        # STEPS
        # ----------------------------------------------------

        lbl_steps = QLabel(
            "Các bước suy luận chi tiết:"
        )

        lbl_steps.setFont(
            QFont("Segoe UI", 10, QFont.Bold)
        )

        lbl_steps.setStyleSheet(
            f"color: {TEXT_SECONDARY}; border: none;"
        )

        conclusion_layout.addWidget(
            lbl_steps
        )

        self.steps_text = QTextEdit()
        self.steps_text.setReadOnly(True)
        self.steps_text.setMinimumHeight(140)

        self.steps_text.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {BG_MAIN};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 12px;
                color: {TEXT_PRIMARY};
                font-size: 11px;
            }}
            """
        )

        conclusion_layout.addWidget(
            self.steps_text
        )

        main_layout.addWidget(
            conclusion_card
        )

        # ====================================================
        # MOUNT SCROLL
        # ====================================================

        scroll_area.setWidget(
            scroll_content
        )

        outer_layout.addWidget(
            scroll_area
        )

        self.clear_results()

    # ========================================================
    # LOAD PATIENTS
    # ========================================================

    def load_patients(self):

        try:

            # Lấy bệnh nhân thật từ SQLite
            self.patients = (
                self.patient_repository
                .get_all_patients()
            )

            self.patient_combo.blockSignals(True)

            self.patient_combo.clear()

            # Không có bệnh nhân
            if not self.patients:

                self.patient_combo.addItem(
                    "Chưa có bệnh nhân nào",
                    None
                )

                self.current_patient = None

                self.patient_combo.blockSignals(False)

                self.clear_results()

                return

            # ------------------------------------------------
            # ADD TẤT CẢ BỆNH NHÂN VÀO COMBO
            # ------------------------------------------------

            for patient in self.patients:

                display_text = (
                    f"{patient.patient_id}  |  "
                    f"{patient.name}"
                )

                # QUAN TRỌNG:
                # Chỉ lưu ID bệnh nhân
                self.patient_combo.addItem(
                    display_text,
                    patient.patient_id
                )

            self.patient_combo.blockSignals(False)

            # Chọn bệnh nhân đầu tiên
            self.patient_combo.setCurrentIndex(0)

            self.on_patient_changed(0)

        except Exception as e:

            self.patient_combo.blockSignals(False)

            QMessageBox.critical(
                self,
                "Lỗi tải bệnh nhân",
                f"Không thể tải danh sách bệnh nhân:\n\n{e}"
            )

            print(
                "Load patients error:",
                repr(e)
            )

    # ========================================================
    # FIND CURRENT PATIENT
    # ========================================================

    def get_selected_patient(self):

        patient_id = (
            self.patient_combo.currentData()
        )

        if patient_id is None:
            return None

        # Tìm Patient object trong danh sách
        for patient in self.patients:

            if str(patient.patient_id) == str(patient_id):
                return patient

        return None

    # ========================================================
    # CHANGE PATIENT
    # ========================================================

    def on_patient_changed(self, index):

        if index < 0:
            return

        patient = self.get_selected_patient()

        self.current_patient = patient

        if patient is None:

            self.patient_info.setText(
                "Chưa chọn bệnh nhân"
            )

            self.clear_results()

            return

        symptoms = self.format_symptoms(
            patient.symptoms
        )

        self.patient_info.setText(
            f"<b>Mã BN:</b> {patient.patient_id}"
            f"&nbsp;&nbsp; | &nbsp;&nbsp;"
            f"<b>Họ tên:</b> {patient.name}"
            f"&nbsp;&nbsp; | &nbsp;&nbsp;"
            f"<b>Tuổi:</b> {patient.age}"
            f"&nbsp;&nbsp; | &nbsp;&nbsp;"
            f"<b>Triệu chứng:</b> "
            f"<span style='color:{BLUE};'>{symptoms}</span>"
        )

        # Khi đổi bệnh nhân thì xoá kết quả cũ
        self.clear_results(
            keep_patient_info=True
        )

    # ========================================================
    # FORMAT SYMPTOMS
    # ========================================================

    def format_symptoms(self, symptoms):

        if symptoms is None:
            return "-"

        if isinstance(symptoms, list):

            if not symptoms:
                return "-"

            return ", ".join(
                str(x).strip()
                for x in symptoms
            )

        return str(symptoms)

    # ========================================================
    # CLEAR RESULTS
    # ========================================================

    def clear_results(
        self,
        keep_patient_info=False
    ):

        if not keep_patient_info:

            self.patient_info.setText(
                "Vui lòng chọn một bệnh nhân "
                "và bấm <b>'Phân tích ngay'</b>"
            )

        self.facts_text.setHtml(
            f"""
            <span style='color:{TEXT_MUTED};'>
                Dữ liệu Fact sẽ hiển thị ở đây.
            </span>
            """
        )

        self.rules_text.setHtml(
            f"""
            <span style='color:{TEXT_MUTED};'>
                Các Rule được kích hoạt sẽ hiển thị ở đây.
            </span>
            """
        )

        self.steps_text.setHtml(
            f"""
            <span style='color:{TEXT_MUTED};'>
                Chi tiết các bước suy luận sẽ xuất hiện ở đây.
            </span>
            """
        )

        self.risk_box.set_value(
            "--",
            TEXT_PRIMARY,
            BG_MAIN,
            BORDER_COLOR
        )

        self.priority_box.set_value(
            "--",
            TEXT_PRIMARY,
            BG_MAIN,
            BORDER_COLOR
        )

    # ========================================================
    # RUN AI REASONING
    # ========================================================

    def run_reasoning(self):

        # Lấy đúng bệnh nhân đang chọn
        patient = self.get_selected_patient()

        if patient is None:

            QMessageBox.warning(
                self,
                "Thông báo",
                "Vui lòng chọn bệnh nhân trước khi phân tích."
            )

            return

        try:

            # =================================================
            # QUAN TRỌNG:
            # TẠO ENGINE MỚI CHO MỖI LẦN PHÂN TÍCH
            # =================================================

            engine = InferenceEngine(
                get_default_knowledge_base()
            )

            # Lưu engine hiện tại
            self.engine = engine

            # =================================================
            # 1. EXTRACT FACTS
            # =================================================

            facts = extract_facts_from_patient(
                patient
            )

            # =================================================
            # 2. RUN INFERENCE
            # =================================================

            result = engine.run(
                facts
            )

            # =================================================
            # 3. PATIENT INFO
            # =================================================

            symptoms = self.format_symptoms(
                patient.symptoms
            )

            self.patient_info.setText(
                f"<b>Mã BN:</b> {patient.patient_id}"
                f"&nbsp;&nbsp; | &nbsp;&nbsp;"
                f"<b>Họ tên:</b> {patient.name}"
                f"&nbsp;&nbsp; | &nbsp;&nbsp;"
                f"<b>Tuổi:</b> {patient.age}"
                f"&nbsp;&nbsp; | &nbsp;&nbsp;"
                f"<b>Triệu chứng:</b> "
                f"<span style='color:{BLUE};'>{symptoms}</span>"
            )

            # =================================================
            # 4. RENDER FACTS
            # =================================================

            facts_html = ""

            all_facts = result.get(
                "all_facts",
                []
            )

            for fact in all_facts:

                val_str = str(
                    fact.value
                )

                if val_str.lower() == "true":

                    val_badge = (
                        f"<b style='color:{GREEN};'>"
                        f"TRUE"
                        f"</b>"
                    )

                elif val_str.lower() == "false":

                    val_badge = (
                        f"<b style='color:{TEXT_MUTED};'>"
                        f"FALSE"
                        f"</b>"
                    )

                else:

                    val_badge = (
                        f"<b style='color:{BLUE};'>"
                        f"{val_str}"
                        f"</b>"
                    )

                facts_html += (
                    f"<div style='margin-bottom:6px;'>"
                    f"• <b>{fact.key}</b>: "
                    f"{val_badge}"
                    f"</div>"
                )

            if not facts_html:

                facts_html = (
                    f"<span style='color:{TEXT_MUTED};'>"
                    f"Không có Fact nào."
                    f"</span>"
                )

            self.facts_text.setHtml(
                facts_html
            )

            # =================================================
            # 5. RENDER ACTIVATED RULES
            # =================================================

            activated_rules = result.get(
                "activated_rules",
                []
            )

            rules_html = ""

            for rule_id in activated_rules:

                rule = next(
                    (
                        r
                        for r in engine.rules
                        if r.rule_id == rule_id
                    ),
                    None
                )

                if rule:

                    rules_html += (
                        f"<div style='margin-bottom:10px;'>"
                        f"<b style='color:{PURPLE};'>"
                        f"[{rule.rule_id}]"
                        f"</b> "
                        f"{rule.description}"
                        f"</div>"
                    )

            if not rules_html:

                rules_html = (
                    f"<span style='color:{TEXT_MUTED};'>"
                    f"Không có Rule nào được kích hoạt."
                    f"</span>"
                )

            self.rules_text.setHtml(
                rules_html
            )

            # =================================================
            # 6. RESULT
            # =================================================

            risk = str(
                result.get(
                    "risk",
                    "LOW"
                )
            ).upper()

            priority = str(
                result.get(
                    "priority",
                    "LOW"
                )
            ).upper()

            self.update_risk_card(
                risk
            )

            self.update_priority_card(
                priority
            )

            # =================================================
            # 7. REASONING STEPS
            # =================================================

            steps = result.get(
                "reasoning_steps",
                []
            )

            steps_html = ""

            for idx, step in enumerate(
                steps,
                1
            ):

                steps_html += (
                    f"<div style='margin-bottom:8px;'>"
                    f"<b style='color:{BLUE};'>"
                    f"Bước {idx}:</b> "
                    f"{step}"
                    f"</div>"
                )

            if not steps_html:

                steps_html = (
                    f"<span style='color:{TEXT_MUTED};'>"
                    f"Không có bước suy luận nào."
                    f"</span>"
                )

            self.steps_text.setHtml(
                steps_html
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Lỗi AI Reasoning",
                f"Không thể thực hiện suy luận:\n\n{e}"
            )

            print(
                "Reasoning error:",
                repr(e)
            )

    # ========================================================
    # UPDATE RISK
    # ========================================================

    def update_risk_card(self, risk):

        risk = str(risk).upper()

        if risk == "HIGH":

            self.risk_box.set_value(
                "HIGH",
                RED,
                RED_LIGHT,
                RED_BORDER
            )

        elif risk == "MEDIUM":

            self.risk_box.set_value(
                "MEDIUM",
                ORANGE,
                ORANGE_LIGHT,
                ORANGE_BORDER
            )

        else:

            self.risk_box.set_value(
                "LOW",
                GREEN,
                GREEN_LIGHT,
                GREEN_BORDER
            )

    # ========================================================
    # UPDATE PRIORITY
    # ========================================================

    def update_priority_card(self, priority):

        priority = str(
            priority
        ).upper()

        if priority == "CRITICAL":

            self.priority_box.set_value(
                "CRITICAL",
                RED,
                RED_LIGHT,
                RED_BORDER
            )

        elif priority == "HIGH":

            self.priority_box.set_value(
                "HIGH",
                ORANGE,
                ORANGE_LIGHT,
                ORANGE_BORDER
            )

        elif priority == "MEDIUM":

            self.priority_box.set_value(
                "MEDIUM",
                PURPLE,
                PURPLE_LIGHT,
                PURPLE_BORDER
            )

        else:

            self.priority_box.set_value(
                "LOW",
                GREEN,
                GREEN_LIGHT,
                GREEN_BORDER
            )


# ============================================================
# ALIAS
# ============================================================

ReasoningPage = ReasoningView