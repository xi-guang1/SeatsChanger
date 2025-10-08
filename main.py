import sys
from PyQt5.QtWidgets import QApplication
from main_window import MWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MWindow()
    window.show()
    sys.exit(app.exec_())