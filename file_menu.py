from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QMessageBox
from quit_dialog import QuitDialog

import cv2


class FileMenu(QMenu):
    
    def __init__(self, parent, main_controller):
        super(QMenu, self).__init__(parent)
        self.main_controller = main_controller

        self.setTitle("&File")

        self.open_action = QAction("&Open", self)
        self.save_action = QAction("&Save", self)
        self.quit_action = QAction("Quit", self)

        self.open_action.triggered.connect(self.select_file)
        self.save_action.triggered.connect(self.save_file)
        self.quit_action.triggered.connect(self.open_quit_dialog)

        self.addAction(self.open_action)
        self.addAction(self.save_action)
        self.addAction(self.quit_action)


    def select_file(self):
        try:
            filters = "Image files (*.bmp *.dib *.jpeg *.jpg *.jpe *.jp2 *.png *.pgm *.ppm *.sr *.ras *tiff *.tif)"
            file_path = QFileDialog.getOpenFileName(self, "Open Image", '', filters)[0]
            self.main_controller.file_path = file_path
            self.main_controller.reload_file()
        except:
            error_message = QMessageBox()
            error_message.setWindowTitle("Error")
            error_message.setText("Error: file " + file_path +  " failed to open")
            error_message.exec()


    def save_file(self):
        try:
            save_window = QFileDialog()
            save_window.setDefaultSuffix('.png')
            save_window.setWindowTitle("Save Image")
            filters = "Image files (*.bmp *.dib *.jpeg *.jpg *.jpe *.jp2 *.png *.pgm *.ppm *.sr *.ras *tiff *.tif)"
            save_window.setNameFilter(filters)
            save_window.setAcceptMode(QFileDialog.AcceptSave)
    
            save_window.exec()
            # No file selected
            if len(save_window.selectedFiles()) == 0:
                return 0
            self.main_controller.write_file(save_window.selectedFiles()[0])

        except:
            error_message = QMessageBox()
            error_message.setWindowTitle("Error")
            error_message.setText("Error: file failed to save")
            error_message.exec()


    def open_quit_dialog(self):
        quit_dialog = QuitDialog(self)
        quit_dialog.open()
