import sys

from PySide6.QtWidgets import QApplication
from chris_naylor_sys import NeylorEngine
from main_window import EspressoExpertApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EspressoExpertApp(engine=NeylorEngine("lab_3/espresso_db.json"))
    window.show()
    sys.exit(app.exec())
