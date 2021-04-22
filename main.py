from PyQt5.QtWidgets import QApplication

def run():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()


if __name__ == '__main__':

    import sys
    from main_window import MainWindow
    sys.exit(run())