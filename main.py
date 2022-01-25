import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from main_controller import MainController

def run():
    app = QApplication(sys.argv)

    controller = MainController()
    window = MainWindow(controller)
    window.show()

    app.exec_()


if __name__ == '__main__':

    sys.exit(run())