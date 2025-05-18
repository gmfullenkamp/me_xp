import sys
from PyQt5.QtWidgets import QApplication
from ui.dashboard import MeXPApp, set_dark_mode

if __name__ == "__main__":
    app = QApplication(sys.argv)
    set_dark_mode(app)
    window = MeXPApp()
    window.resize(800, 1000)
    window.show()
    sys.exit(app.exec_())
