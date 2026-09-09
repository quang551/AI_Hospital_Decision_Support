import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from database.database import Database
from database.repository import (
    PatientRepository,
    DoctorRepository,
    RoomRepository,
    AppointmentRepository,
)

from gui.main_window import MainWindow


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "hospital.db"


# ============================================================
# INITIALIZE SYSTEM
# ============================================================

def initialize_system():
    """
    Khởi tạo các thành phần chính của hệ thống:
    - SQLite Database
    - Repository
    - AI / Knowledge Base
    - Scheduler
    """

    print("=" * 60)
    print("AI HOSPITAL DECISION SUPPORT SYSTEM")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. DATABASE
    # --------------------------------------------------------

    database = Database(str(DB_PATH))
    database.create_tables()

    print("[MAIN] SQLite database initialized.")

    # --------------------------------------------------------
    # 2. REPOSITORIES
    # --------------------------------------------------------

    patient_repository = PatientRepository(str(DB_PATH))
    doctor_repository = DoctorRepository(str(DB_PATH))
    room_repository = RoomRepository(str(DB_PATH))
    appointment_repository = AppointmentRepository(str(DB_PATH))

    print("[MAIN] Repositories initialized.")

    # --------------------------------------------------------
    # 3. SYSTEM COMPONENTS
    # --------------------------------------------------------
    #
    # Knowledge Base, Forward Chaining và Scheduler
    # hiện đã được các thành viên khác xây dựng.
    #
    # Các GUI View sẽ sử dụng những module này khi cần.
    #
    # Không viết lại logic AI / Scheduler ở main.py.
    #

    print("[MAIN] AI / Knowledge Base modules ready.")
    print("[MAIN] Scheduling modules ready.")

    return {
        "database": database,
        "patient_repository": patient_repository,
        "doctor_repository": doctor_repository,
        "room_repository": room_repository,
        "appointment_repository": appointment_repository,
    }


# ============================================================
# MAIN APPLICATION
# ============================================================

def main():

    # --------------------------------------------------------
    # 1. Initialize system
    # --------------------------------------------------------

    system = initialize_system()

    # --------------------------------------------------------
    # 2. Create PySide6 application
    # --------------------------------------------------------

    app = QApplication(sys.argv)

    app.setApplicationName(
        "AI Hospital Decision Support System"
    )

    app.setStyle("Fusion")

    # --------------------------------------------------------
    # 3. Create Main Window
    # --------------------------------------------------------

    window = MainWindow()
    window.show()

    print("[MAIN] GUI started successfully.")

    # --------------------------------------------------------
    # 4. Start application event loop
    # --------------------------------------------------------

    sys.exit(app.exec())


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()