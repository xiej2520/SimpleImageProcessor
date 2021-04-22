from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QPushButton
from PyQt5 import QtCore


class QuitDialog(QDialog):
    def __init__(self, parent):
        super(QuitDialog, self).__init__(parent)

        self.setWindowTitle("Quit?")

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)

        self.layout = QHBoxLayout()

        save_button = QPushButton("Save")
        no_save_button = QPushButton("Don't Save")
        cancel_button = QPushButton("Cancel")

        save_button.clicked.connect(self.parent().save_file)
        save_button.clicked.connect(QApplication.exit)
        no_save_button.clicked.connect(QApplication.exit)
        cancel_button.clicked.connect(self.close)

        self.layout.addWidget(save_button)
        self.layout.addWidget(no_save_button)
        self.layout.addWidget(cancel_button)
        self.setLayout(self.layout)