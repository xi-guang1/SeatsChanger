import sys
from PyQt5.QtWidgets import QApplication
from main_window import SeatingChartWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SeatingChartWindow()
    window.show()
    sys.exit(app.exec_())