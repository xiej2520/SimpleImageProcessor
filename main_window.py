from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QListWidget, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QFileDialog, QSlider, QMessageBox, QMenuBar, QMenu, QAction
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtCore import QSize, Qt

from image_renderer import ImageRenderer
from file_menu import FileMenu
from filter_editor import FilterEditor


app = QApplication([])
win = QMainWindow()

class MainWindow(QMainWindow):

    def __init__(self, controller, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.main_controller = controller
        self.setWindowTitle("Simple Image Processor")
        
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.outer_layout = QHBoxLayout()
        self.image_layout = QVBoxLayout()
        self.central_widget.setLayout(self.outer_layout)

        self.menu_bar = QMenuBar(self)
        self.file_menu = FileMenu(self, self.main_controller)
        self.menu_bar.addMenu(self.file_menu)
        self.setMenuBar(self.menu_bar)

        self.image_path_label = QLabel("File: ")
        self.image_box = ImageRenderer(self.main_controller)
        self.main_controller.image_path_label = self.image_path_label

        self.filter_editor = FilterEditor(self.main_controller)
        self.filter_editor.setMaximumWidth(200)
        self.outer_layout.addWidget(self.filter_editor, 1)

        self.image_layout.addWidget(self.image_path_label)
        self.image_layout.addWidget(self.image_box)

        self.outer_layout.addLayout(self.image_layout, 4)

    def closeEvent(self, event):
        self.filter_editor = 0
        self.file_menu.open_quit_dialog()
        # needed to keep program open for dialog to work
        event.ignore()
