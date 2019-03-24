import gui
import sys
from PyQt5.QtWidgets import QApplication
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = gui.MyWindow()
    myWindow.show()
    sys.exit(app.exec_())