
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget
)

# main.py nằm ở ROOT của project.
PROJECT_ROOT = Path(__file__).resolve().parent
if not (PROJECT_ROOT / "database").exists() and (PROJECT_ROOT.parent / "database").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.database import Database
from database.repository import PatientRepository
from gui.dashboard import DashboardContent
from gui.patient_view import PatientView
from gui.queue_view import QueueView
from gui.schedule_view import ScheduleView
from gui.reasoning_view import ReasoningView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Hospital Decision Support System")
        self.setMinimumSize(1100, 700)
        self.resize(1366, 800)

        self.db_path = PROJECT_ROOT / "hospital.db"
        self.database = Database(str(self.db_path))
        self.database.create_tables()

        self.patient_repository = PatientRepository(str(self.db_path))
        self.page_widgets = []

        self.build_ui()

    def build_ui(self):
        central = QWidget()
        central.setStyleSheet("background:#F4F7FC;")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self.create_sidebar())

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        right.addWidget(self.create_header())

        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background:#F4F7FC;")
        right.addWidget(self.pages, 1)

        root.addLayout(right, 1)

        self.create_pages()

    # ========================================================
    # SIDEBAR
    # ========================================================

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(225)
        sidebar.setStyleSheet("background:#101B36;")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 18)
        layout.setSpacing(7)

        brand = QHBoxLayout()
        brand.setSpacing(10)

        logo = QLabel("+")
        logo.setFixedSize(42, 42)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(
            "background:#397EF6;color:white;border-radius:10px;"
            "font-size:25px;font-weight:bold;"
        )

        texts = QVBoxLayout()
        texts.setSpacing(0)

        name = QLabel("AI HOSPITAL")
        name.setFont(QFont("Segoe UI", 12, QFont.Bold))
        name.setStyleSheet("color:white;")

        sub = QLabel("Decision Support System")
        sub.setStyleSheet("color:#91A0BD;font-size:8px;")

        texts.addWidget(name)
        texts.addWidget(sub)

        brand.addWidget(logo)
        brand.addLayout(texts)

        layout.addLayout(brand)
        layout.addSpacing(22)

        title = QLabel("MAIN MENU")
        title.setStyleSheet(
            "color:#71809B;font-size:9px;font-weight:bold;padding:5px;"
        )
        layout.addWidget(title)

        self.nav = []

        self.add_nav(layout, "Dashboard", 0)
        self.add_nav(layout, "Patients", 1)
        self.add_nav(layout, "Priority Queue", 2)
        self.add_nav(layout, "Schedule", 3)
        self.add_nav(layout, "AI Reasoning", 4)

        layout.addStretch()

        online = QLabel("●  System Online")
        online.setStyleSheet(
            "background:#182746;color:#BFD0EA;"
            "border:1px solid #293A60;border-radius:8px;"
            "padding:10px;font-size:9px;font-weight:bold;"
        )
        layout.addWidget(online)

        return sidebar

    def add_nav(self, layout, text, index):
        button = QPushButton(text)
        button.setFixedHeight(44)
        button.setCheckable(True)
        button.setCursor(Qt.PointingHandCursor)

        button.setStyleSheet("""
            QPushButton {
                background:transparent;
                color:#AAB7CE;
                border:none;
                border-radius:8px;
                text-align:left;
                padding-left:15px;
                font-size:11px;
                font-weight:600;
            }
            QPushButton:hover {
                background:#1A2A4D;
                color:white;
            }
            QPushButton:checked {
                background:#397EF6;
                color:white;
            }
        """)

        button.clicked.connect(
            lambda checked=False, i=index, b=button:
            self.switch_page(i, b)
        )

        layout.addWidget(button)
        self.nav.append(button)

    # ========================================================
    # HEADER
    # ========================================================

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(72)
        header.setStyleSheet(
            "background:white;border-bottom:1px solid #E1E6EF;"
        )

        layout = QHBoxLayout(header)
        layout.setContentsMargins(25, 12, 25, 12)

        title = QLabel("AI Hospital Decision Support")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color:#172033;")

        layout.addWidget(title)
        layout.addStretch()

        badge = QLabel("AI Clinical Support")
        badge.setStyleSheet(
            "color:#397EF6;background:#EEF4FF;"
            "border-radius:8px;padding:9px 14px;"
            "font-size:10px;font-weight:bold;"
        )
        layout.addWidget(badge)

        return header

    # ========================================================
    # CREATE PAGES
    # ========================================================

    def create_pages(self):
        configs = [
            (DashboardContent, "Dashboard"),
            (PatientView, "Patients"),
            (QueueView, "Priority Queue"),
            (ScheduleView, "Schedule"),
            (ReasoningView, "AI Reasoning"),
        ]

        for cls, title in configs:
            try:
                # IMPORTANT:
                # ReasoningView hiện tại tự tạo repository của nó.
                # Không truyền PatientRepository vào ReasoningView.
                if cls is PatientView:
                    page = cls(self.patient_repository)
                else:
                    page = cls()

                self.page_widgets.append(page)
                self.pages.addWidget(page)

                # Dashboard -> other pages
                if isinstance(page, DashboardContent):
                    if hasattr(page, "navigate_requested"):
                        page.navigate_requested.connect(
                            self.navigate_from_dashboard
                        )

                # Patient changed -> refresh everything
                if isinstance(page, PatientView):
                    if hasattr(page, "patient_added"):
                        page.patient_added.connect(
                            self.refresh_pages
                        )

            except Exception as e:
                print(f"Cannot load {title}: {e}")

                error = QLabel(
                    f"Unable to load {title}\n\n{e}"
                )
                error.setAlignment(Qt.AlignCenter)
                error.setStyleSheet(
                    "background:white;color:#D9364F;"
                    "font-size:14px;padding:30px;"
                )

                self.page_widgets.append(error)
                self.pages.addWidget(error)

        self.switch_page(0, self.nav[0])

    # ========================================================
    # DASHBOARD NAVIGATION
    # ========================================================

    def navigate_from_dashboard(self, index):
        if index < 0 or index >= self.pages.count():
            return

        if index < len(self.nav):
            self.switch_page(index, self.nav[index])
        else:
            self.switch_page(index)

    # ========================================================
    # PAGE SWITCHING
    # ========================================================

    def switch_page(self, index, button=None):
        if index < 0 or index >= self.pages.count():
            return

        self.pages.setCurrentIndex(index)

        for b in self.nav:
            b.setChecked(False)

        if button is not None:
            button.setChecked(True)

        page = self.pages.currentWidget()

        # Include ALL refresh methods used by the project.
        for method in (
            "load_data",
            "load_patients",
            "load_queue",
            "load_appointments",
        ):
            if hasattr(page, method):
                try:
                    getattr(page, method)()
                except Exception as e:
                    print(f"Refresh error on {method}: {e}")
                break

    # ========================================================
    # GLOBAL REFRESH
    # ========================================================

    def refresh_pages(self):
        """
        Patient add/delete changes the DB.
        Refresh every page that exposes a refresh method.
        """
        for page in self.page_widgets:
            for method in (
                "load_data",
                "load_patients",
                "load_queue",
                "load_appointments",
            ):
                if hasattr(page, method):
                    try:
                        getattr(page, method)()
                    except Exception as e:
                        print(
                            f"Page refresh error "
                            f"({method}): {e}"
                        )
                    break

    # ========================================================
    # RUN
    # ========================================================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(
        "AI Hospital Decision Support System"
    )

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
