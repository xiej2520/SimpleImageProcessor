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
        main_controller = controller
        self.setWindowTitle("Simple Image Processor")
        
        central_widget = QWidget(self)    
        self.setCentralWidget(central_widget)
        outer_layout = QHBoxLayout()
        image_layout = QVBoxLayout()
        central_widget.setLayout(outer_layout)

        menu_bar = QMenuBar(self)
        file_menu = FileMenu(self, main_controller)
        menu_bar.addMenu(file_menu)
        self.setMenuBar(menu_bar)

        image_path_label = QLabel("File: ")
        image_box = ImageRenderer(main_controller)
        main_controller.image_path_label = image_path_label

        filter_editor = FilterEditor(main_controller)
        filter_editor.setMaximumWidth(200)
        outer_layout.addWidget(filter_editor, 1)

        image_layout.addWidget(image_path_label)
        image_layout.addWidget(image_box)
    

        outer_layout.addLayout(image_layout, 4)
