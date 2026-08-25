import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QStackedWidget, QGridLayout, QScrollArea, QGraphicsDropShadowEffect
)

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ============================================================
# MAU SAC & THEME (EXACT MATCH IMAGE)
# ============================================================
NAVY_BG = "#0B132B"
NAVY_HOVER = "#1C2541"
BLUE_ACCENT = "#1D4ED8"
LIGHT_BG = "#F1F5F9"
CARD_BG = "#FFFFFF"
BORDER_COLOR = "#E2E8F0"

TEXT_PRIMARY = "#0F172A"
TEXT_MUTED = "#64748B"

# Colors for Priorities & Badges
COLOR_CRITICAL = "#EF4444"
COLOR_HIGH = "#F97316"
COLOR_MEDIUM = "#EAB308"
COLOR_LOW = "#22C55E"

APP_STYLE = f"""
QMainWindow {{
    background-color: {LIGHT_BG};
}}

QWidget {{
    font-family: 'Segoe UI', Arial, sans-serif;
    color: {TEXT_PRIMARY};
}}

QTableWidget {{
    background: white;
    border: none;
    font-size: 12px;
}}

QTableWidget::item {{
    padding: 4px;
    border-bottom: 1px solid #F1F5F9;
}}

QHeaderView::section {{
    background-color: transparent;
    color: {TEXT_MUTED};
    border: none;
    border-bottom: 1px solid {BORDER_COLOR};
    padding: 6px;
    font-weight: 600;
    font-size: 11px;
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    border: none;
    background: #E2E8F0;
    width: 6px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: #94A3B8;
    border-radius: 3px;
}}
"""

def make_shadow():
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(12)
    shadow.setColor(QColor(0, 0, 0, 15))
    shadow.setOffset(0, 2)
    return shadow

def make_card():
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER_COLOR};
            border-radius: 10px;
        }}
    """)
    frame.setGraphicsEffect(make_shadow())
    return frame

# ============================================================
# MATPLOTLIB CHARTS (DONUT & LINE)
# ============================================================
class DonutChartCanvas(FigureCanvas):
    def __init__(self):
        fig = Figure(figsize=(3, 3), dpi=100, facecolor='white')
        super().__init__(fig)
        self.ax = fig.add_subplot(111)
        
        sizes = [4.7, 14.1, 35.2, 46.1]
        colors = [COLOR_CRITICAL, COLOR_HIGH, COLOR_MEDIUM, COLOR_LOW]
        
        wedges, _ = self.ax.pie(
            sizes, colors=colors, startangle=90, 
            wedgeprops=dict(width=0.35, edgecolor='white', linewidth=2)
        )
        
        # Center Text
        self.ax.text(0, 0.1, "128", ha='center', va='center', fontsize=16, fontweight='bold', color=TEXT_PRIMARY)
        self.ax.text(0, -0.15, "Tổng", ha='center', va='center', fontsize=11, color=TEXT_MUTED)
        self.ax.axis('equal')
        fig.tight_layout(pad=0)

class LineChartCanvas(FigureCanvas):
    def __init__(self):
        fig = Figure(figsize=(4, 2.2), dpi=100, facecolor='white')
        super().__init__(fig)
        self.ax = fig.add_subplot(111)
        
        dates = ['18/05', '19/05', '20/05', '21/05', '22/05', '23/05', '24/05']
        tong = [40, 60, 55, 53, 52, 68, 62]
        khan_cap = [5, 6, 8, 9, 8, 15, 12]
        da_xu_ly = [20, 32, 38, 39, 36, 48, 48]
        
        self.ax.plot(dates, tong, marker='o', markersize=4, color='#2563EB', label='Tổng bệnh nhân', linewidth=1.5)
        self.ax.plot(dates, khan_cap, marker='o', markersize=4, color='#EF4444', label='Khẩn cấp', linewidth=1.5)
        self.ax.plot(dates, da_xu_ly, marker='o', markersize=4, color='#22C55E', label='Đã xử lý', linewidth=1.5)
        
        self.ax.set_ylim(0, 80)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#CBD5E1')
        self.ax.spines['bottom'].set_color('#CBD5E1')
        
        self.ax.tick_params(axis='both', colors=TEXT_MUTED, labelsize=8)
        self.ax.grid(axis='y', linestyle='--', alpha=0.5, color='#E2E8F0')
        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3, frameon=False, fontsize=8)
        fig.tight_layout(pad=1)

# ============================================================
# COMPONENTS
# ============================================================
class KpiCard(QFrame):
    def __init__(self, icon, title, val, sub, bg_color, icon_color, sub_color=TEXT_MUTED):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
            }}
        """)
        self.setGraphicsEffect(make_shadow())
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        
        icon_box = QLabel(icon)
        icon_box.setFixedSize(40, 40)
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setStyleSheet(f"background-color: {icon_color}; color: white; border-radius: 20px; font-size: 18px;")
        layout.addWidget(icon_box)
        
        v_box = QVBoxLayout()
        v_box.setSpacing(1)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; border: none;")
        lbl_val = QLabel(val)
        lbl_val.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 20px; font-weight: bold; border: none;")
        lbl_sub = QLabel(sub)
        lbl_sub.setStyleSheet(f"color: {sub_color}; font-size: 10px; border: none;")
        
        v_box.addWidget(lbl_title)
        v_box.addWidget(lbl_val)
        v_box.addWidget(lbl_sub)
        
        layout.addLayout(v_box)

def make_badge(text, color, bg):
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(f"""
        background-color: {bg};
        color: {color};
        font-weight: bold;
        font-size: 10px;
        border-radius: 4px;
        padding: 2px 6px;
    """)
    return lbl

# ============================================================
# MAIN DASHBOARD VIEW
# ============================================================
class DashboardContent(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 20)
        main_layout.setSpacing(15)

        # 1. TOP TITLE BAR
        top_bar = QHBoxLayout()
        
        title_box = QVBoxLayout()
        t1 = QLabel("Tổng quan hệ thống")
        t1.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {TEXT_PRIMARY};")
        t2 = QLabel("Bệnh viện AI - Hỗ trợ quyết định và xếp lịch thông minh")
        t2.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED};")
        title_box.addWidget(t1)
        title_box.addWidget(t2)
        top_bar.addLayout(title_box)
        top_bar.addStretch()

        # Action items (bell, date, profile)
        btn_bell = QPushButton("🔔")
        btn_bell.setFixedSize(36, 36)
        btn_bell.setStyleSheet("background: #FEE2E2; color: #EF4444; border-radius: 18px; font-size: 14px; border: none;")
        
        date_box = QFrame()
        date_box.setStyleSheet(f"background: white; border: 1px solid {BORDER_COLOR}; border-radius: 8px; padding: 2px 8px;")
        d_layout = QHBoxLayout(date_box)
        d_layout.setContentsMargins(4, 2, 4, 2)
        d_layout.addWidget(QLabel("📅"))
        date_text = QVBoxLayout()
        date_text.setSpacing(0)
        date_text.addWidget(QLabel("24/05/2025", styleSheet="font-size:11px; font-weight:bold;"))
        date_text.addWidget(QLabel("09:30 AM", styleSheet="font-size:9px; color:#64748B;"))
        d_layout.addLayout(date_text)

        user_box = QHBoxLayout()
        avatar = QLabel("👤")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet("background: #DBEAFE; color: #1D4ED8; border-radius: 18px; font-size: 16px;")
        u_info = QVBoxLayout()
        u_info.setSpacing(0)
        u_info.addWidget(QLabel("Admin", styleSheet="font-size:12px; font-weight:bold;"))
        u_info.addWidget(QLabel("Administrator ∨", styleSheet="font-size:10px; color:#64748B;"))
        u_info.addWidget(QLabel("● Online", styleSheet="font-size:9px; color:#22C55E;"))
        user_box.addWidget(avatar)
        user_box.addLayout(u_info)

        top_bar.addWidget(btn_bell)
        top_bar.addSpacing(10)
        top_bar.addWidget(date_box)
        top_bar.addSpacing(10)
        top_bar.addLayout(user_box)

        main_layout.addLayout(top_bar)

        # 2. KPI CARDS
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(12)
        kpi_grid.addWidget(KpiCard("👥", "Tổng bệnh nhân", "128", "↑ 12% so với hôm qua", "#EFF6FF", "#3B82F6", "#22C55E"), 0, 0)
        kpi_grid.addWidget(KpiCard("🕒", "Đang chờ", "24", "↑ 5% so với hôm qua", "#F0FDF4", "#22C55E", "#22C55E"), 0, 1)
        kpi_grid.addWidget(KpiCard("⚠️", "Khẩn cấp (Critical)", "6", "↑ 2 ca mới", "#FEF2F2", "#EF4444", "#EF4444"), 0, 2)
        kpi_grid.addWidget(KpiCard("🩺", "Bác sĩ khả dụng", "18 / 28", "Đang làm việc", "#FAF5FF", "#A855F7"), 0, 3)
        kpi_grid.addWidget(KpiCard("🚪", "Phòng khả dụng", "15 / 30", "Còn trống", "#FFF7ED", "#F97316"), 0, 4)
        main_layout.addLayout(kpi_grid)

        # 3. MIDDLE ROW (Queue & Donut)
        mid_row = QHBoxLayout()
        mid_row.setSpacing(12)

        # Queue Card
        queue_card = make_card()
        q_layout = QVBoxLayout(queue_card)
        q_layout.setContentsMargins(16, 12, 16, 12)
        q_layout.addWidget(QLabel("Danh sách ưu tiên (Priority Queue)", styleSheet="font-weight:bold; font-size:13px; border:none;"))
        
        q_table = QTableWidget(5, 6)
        q_table.setHorizontalHeaderLabels(["ID", "Bệnh nhân", "Mức ưu tiên", "Điểm ưu tiên", "Thời gian vào", "Trạng thái"])
        q_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        q_table.verticalHeader().setVisible(False)
        q_table.setFixedHeight(170)

        data_q = [
            ("P001", "Nguyễn Văn An", "CRITICAL", COLOR_CRITICAL, "#FEE2E2", "95", "09:15 AM", "Đang chờ"),
            ("P002", "Trần Thị Bình", "HIGH", COLOR_HIGH, "#FFEDD5", "80", "09:20 AM", "Đang chờ"),
            ("P003", "Lê Văn Cường", "HIGH", COLOR_HIGH, "#FFEDD5", "75", "09:25 AM", "Đang chờ"),
            ("P004", "Phạm Thị Dung", "MEDIUM", COLOR_MEDIUM, "#FEF08A", "50", "09:30 AM", "Đang chờ"),
            ("P005", "Hoàng Văn Em", "LOW", COLOR_LOW, "#DCFCE7", "30", "09:35 AM", "Đang chờ"),
        ]

        for r, row in enumerate(data_q):
            q_table.setItem(r, 0, QTableWidgetItem(row[0]))
            q_table.setItem(r, 1, QTableWidgetItem(row[1]))
            q_table.setCellWidget(r, 2, make_badge(row[2], row[3], row[4]))
            q_table.setItem(r, 3, QTableWidgetItem(row[5]))
            q_table.setItem(r, 4, QTableWidgetItem(row[6]))
            q_table.setCellWidget(r, 5, make_badge(row[7], COLOR_HIGH, "#FFEDD5"))

        q_layout.addWidget(q_table)
        btn_q_more = QPushButton("Xem toàn bộ →")
        btn_q_more.setStyleSheet("color:#2563EB; font-weight:bold; border:none; background:transparent; font-size:11px;")
        q_layout.addWidget(btn_q_more, alignment=Qt.AlignRight)
        
        mid_row.addWidget(queue_card, 65)

        # Priority Distribution Card
        dist_card = make_card()
        d_card_layout = QVBoxLayout(dist_card)
        d_card_layout.setContentsMargins(16, 12, 16, 12)
        d_card_layout.addWidget(QLabel("Phân bố mức ưu tiên", styleSheet="font-weight:bold; font-size:13px; border:none;"))
        
        donut_content = QHBoxLayout()
        donut_content.addWidget(DonutChartCanvas(), 50)
        
        legend_layout = QVBoxLayout()
        legend_layout.setAlignment(Qt.AlignCenter)
        legend_items = [
            ("● Critical (6)", "4.7%", COLOR_CRITICAL),
            ("● High (18)", "14.1%", COLOR_HIGH),
            ("● Medium (45)", "35.2%", COLOR_MEDIUM),
            ("● Low (59)", "46.1%", COLOR_LOW),
        ]
        for name, pct, color in legend_items:
            item_row = QHBoxLayout()
            lbl_n = QLabel(name)
            lbl_n.setStyleSheet(f"color:{color}; font-weight:bold; font-size:11px; border:none;")
            lbl_p = QLabel(pct)
            lbl_p.setStyleSheet(f"color:{TEXT_MUTED}; font-size:11px; border:none;")
            item_row.addWidget(lbl_n)
            item_row.addStretch()
            item_row.addWidget(lbl_p)
            legend_layout.addLayout(item_row)

        donut_content.addLayout(legend_layout, 50)
        d_card_layout.addLayout(donut_content)
        mid_row.addWidget(dist_card, 35)

        main_layout.addLayout(mid_row)

        # 4. BOTTOM ROW (Schedule, Line Chart, Recent Activity)
        bot_row = QHBoxLayout()
        bot_row.setSpacing(12)

        # Today's Schedule
        sched_card = make_card()
        sc_layout = QVBoxLayout(sched_card)
        sc_layout.setContentsMargins(16, 12, 16, 12)
        sc_layout.addWidget(QLabel("Lịch hẹn hôm nay", styleSheet="font-weight:bold; font-size:13px; border:none;"))
        
        s_table = QTableWidget(5, 5)
        s_table.setHorizontalHeaderLabels(["Thời gian", "Bệnh nhân", "Bác sĩ", "Phòng", "Trạng thái"])
        s_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        s_table.verticalHeader().setVisible(False)
        s_table.setFixedHeight(170)

        data_s = [
            ("10:00 AM", "Nguyễn Văn An", "BS. Trần Minh", "P.101", "Đã xác nhận", COLOR_LOW, "#DCFCE7"),
            ("10:30 AM", "Trần Thị Bình", "BS. Lê Phương", "P.102", "Đã xác nhận", COLOR_LOW, "#DCFCE7"),
            ("11:00 AM", "Lê Văn Cường", "BS. Phạm Hùng", "P.103", "Chờ khám", COLOR_HIGH, "#FFEDD5"),
            ("11:30 AM", "Phạm Thị Dung", "BS. Nguyễn Mai", "P.104", "Chờ khám", COLOR_HIGH, "#FFEDD5"),
            ("13:00 PM", "Hoàng Văn Em", "BS. Trần Minh", "P.105", "Đã xác nhận", COLOR_LOW, "#DCFCE7"),
        ]
        for r, row in enumerate(data_s):
            s_table.setItem(r, 0, QTableWidgetItem(row[0]))
            s_table.setItem(r, 1, QTableWidgetItem(row[1]))
            s_table.setItem(r, 2, QTableWidgetItem(row[2]))
            s_table.setItem(r, 3, QTableWidgetItem(row[3]))
            s_table.setCellWidget(r, 4, make_badge(row[4], row[5], row[6]))

        sc_layout.addWidget(s_table)
        btn_s_more = QPushButton("Xem lịch chi tiết →")
        btn_s_more.setStyleSheet("color:#2563EB; font-weight:bold; border:none; background:transparent; font-size:11px;")
        sc_layout.addWidget(btn_s_more, alignment=Qt.AlignRight)
        bot_row.addWidget(sched_card, 38)

        # Daily Stats (Line Chart)
        chart_card = make_card()
        cc_layout = QVBoxLayout(chart_card)
        cc_layout.setContentsMargins(16, 12, 16, 12)
        cc_layout.addWidget(QLabel("Thống kê theo ngày (7 ngày qua)", styleSheet="font-weight:bold; font-size:13px; border:none;"))
        cc_layout.addWidget(LineChartCanvas())
        bot_row.addWidget(chart_card, 34)

        # Recent Activity
        act_card = make_card()
        ac_layout = QVBoxLayout(act_card)
        ac_layout.setContentsMargins(16, 12, 16, 12)
        ac_layout.addWidget(QLabel("Hoạt động gần đây", styleSheet="font-weight:bold; font-size:13px; border:none;"))
        
        act_list = QVBoxLayout()
        act_list.setSpacing(10)

        activities = [
            ("➕", "#22C55E", "Thêm bệnh nhân mới: Nguyễn Văn F", "09:25 AM - Admin"),
            ("📅", "#F97316", "Lịch hẹn mới: Trần Thị G - P.106", "09:20 AM - Hệ thống"),
            ("⚠️", "#EF4444", "Bệnh nhân khẩn cấp: Lê Văn H", "09:15 AM - AI System"),
            ("✓", "#2563EB", "Hoàn thành khám: Phạm Thị I", "09:10 AM - BS. Trần Minh"),
        ]

        for icon, col, t1, t2 in activities:
            row = QHBoxLayout()
            ic = QLabel(icon)
            ic.setFixedSize(28, 28)
            ic.setAlignment(Qt.AlignCenter)
            ic.setStyleSheet(f"background-color:{col}; color:white; border-radius:14px; font-size:12px; border:none;")
            
            txt_b = QVBoxLayout()
            txt_b.setSpacing(0)
            lbl1 = QLabel(t1)
            lbl1.setStyleSheet("font-size:11px; font-weight:bold; border:none;")
            lbl2 = QLabel(t2)
            lbl2.setStyleSheet(f"font-size:9px; color:{TEXT_MUTED}; border:none;")
            txt_b.addWidget(lbl1)
            txt_b.addWidget(lbl2)
            
            row.addWidget(ic)
            row.addLayout(txt_b)
            act_list.addLayout(row)

        ac_layout.addLayout(act_list)
        btn_ac_more = QPushButton("Xem tất cả hoạt động →")
        btn_ac_more.setStyleSheet("color:#2563EB; font-weight:bold; border:none; background:transparent; font-size:11px;")
        ac_layout.addWidget(btn_ac_more, alignment=Qt.AlignRight)
        bot_row.addWidget(act_card, 28)

        main_layout.addLayout(bot_row)

# ============================================================
# MAIN WINDOW & SIDEBAR
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hospital AI Decision Support")
        self.resize(1340, 780)
        self.setStyleSheet(APP_STYLE)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. SIDEBAR (NAVY)
        sidebar = QFrame()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(f"background-color: {NAVY_BG}; border: none;")
        
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(12, 16, 12, 12)
        sb_layout.setSpacing(4)

        # Brand Header
        brand = QHBoxLayout()
        logo = QLabel("✚")
        logo.setStyleSheet("background: #2563EB; color: white; border-radius: 6px; font-size: 16px; font-weight: bold; padding: 4px 8px;")
        
        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        t_title = QLabel("Hospital AI")
        t_title.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        t_sub = QLabel("Decision Support")
        t_sub.setStyleSheet("color: #94A3B8; font-size: 9px;")
        brand_text.addWidget(t_title)
        brand_text.addWidget(t_sub)
        
        brand.addWidget(logo)
        brand.addLayout(brand_text)
        sb_layout.addLayout(brand)
        sb_layout.addSpacing(16)

        # Menu Items
        menu_items = [
            ("Dashboard", "🔷", True),
            ("Patients", "👥", False),
            ("Priority Queue", "⚡", False),
            ("Schedule", "📅", False),
            ("AI Reasoning", "🧠", False),
            ("Doctors", "🩺", False),
            ("Rooms", "🚪", False),
            ("Reports", "📊", False),
            ("Settings", "⚙️", False),
        ]

        for text, icon, active in menu_items:
            btn = QPushButton(f"  {icon}   {text}")
            btn.setFixedHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            if active:
                btn.setStyleSheet(f"background-color: {BLUE_ACCENT}; color: white; font-weight: bold; border-radius: 6px; text-align: left; padding-left: 12px; font-size: 12px;")
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        color: #94A3B8; font-weight: 500; border-radius: 6px; text-align: left; padding-left: 12px; font-size: 12px; background: transparent;
                    }}
                    QPushButton:hover {{
                        background-color: {NAVY_HOVER}; color: white;
                    }}
                """)
            sb_layout.addWidget(btn)

        sb_layout.addStretch()

        # Dark Mode Switcher Frame
        dark_box = QFrame()
        dark_box.setStyleSheet(f"background-color: {NAVY_HOVER}; border-radius: 8px;")
        dk_layout = QHBoxLayout(dark_box)
        dk_layout.setContentsMargins(10, 6, 10, 6)
        dk_layout.addWidget(QLabel("🌙  Dark Mode", styleSheet="color: white; font-size: 11px; font-weight: 500;"))
        dk_layout.addStretch()
        
        toggle = QLabel("●  ")
        toggle.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        toggle.setStyleSheet("background: #475569; color: white; border-radius: 10px; font-size: 12px; min-width: 32px;")
        dk_layout.addWidget(toggle)
        
        sb_layout.addWidget(dark_box)

        # Sidebar Footer
        lbl_copy = QLabel("© 2025 Hospital AI Decision Support System")
        lbl_copy.setStyleSheet("color: #64748B; font-size: 8px; margin-top: 6px;")
        lbl_copy.setWordWrap(True)
        sb_layout.addWidget(lbl_copy)

        layout.addWidget(sidebar)

        # 2. MAIN CONTENT AREA (Scrollable)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(DashboardContent())
        
        main_content_wrapper = QVBoxLayout()
        main_content_wrapper.setContentsMargins(0, 0, 0, 0)
        main_content_wrapper.setSpacing(0)
        main_content_wrapper.addWidget(scroll_area)

        # Bottom System Status Bar
        bot_bar = QFrame()
        bot_bar.setFixedHeight(24)
        bot_bar.setStyleSheet(f"background-color: {NAVY_BG}; border: none;")
        bb_layout = QHBoxLayout(bot_bar)
        bb_layout.setContentsMargins(15, 0, 15, 0)
        
        lbl_ver = QLabel("Phiên bản 1.0.0")
        lbl_ver.setStyleSheet("color: #64748B; font-size: 9px;")
        lbl_stat = QLabel("● Kết nối cơ sở dữ liệu: Online")
        lbl_stat.setStyleSheet("color: #22C55E; font-size: 9px;")
        
        bb_layout.addWidget(lbl_ver)
        bb_layout.addStretch()
        bb_layout.addWidget(lbl_stat)

        main_content_wrapper.addWidget(bot_bar)

        content_widget = QWidget()
        content_widget.setLayout(main_content_wrapper)
        layout.addWidget(content_widget)

        self.setCentralWidget(container)

# ============================================================
# RUN APPLICATION
# ============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())