from PyQt5.QtWidgets import QApplication, QComboBox, QDialog, QListWidget, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QFileDialog, QSlider, QMessageBox, QMenuBar, QMenu, QAction
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtCore import QSize, Qt

from image_renderer import ImageRenderer
import filters
import cv2
from quit_dialog import QuitDialog
from opencv_processing import convert_cv_qt


app = QApplication([])
win = QMainWindow()

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Simple Image Processor")
        
        self.central_widget = QWidget(self)    
        self.setCentralWidget(self.central_widget)
        self.outer_layout = QHBoxLayout()
        self.filters_layout = QVBoxLayout()
        self.image_layout = QVBoxLayout()
        self.central_widget.setLayout(self.outer_layout)


        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.file_menu = QMenu("&File", self)
        self.menu_bar.addMenu(self.file_menu)

        self.open_action = QAction("&Open", self)
        self.save_action = QAction("&Save", self)
        self.quit_action = QAction("Quit", self)

        self.open_action.triggered.connect(self.select_file)
        self.save_action.triggered.connect(self.save_file)
        self.quit_action.triggered.connect(self.open_quit_dialog)

        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.quit_action)


        self.image_path_label = QLabel("File: ")

        self.image_box = ImageRenderer()


        self.filters_list = QListWidget()
        self.filters_select = QComboBox()
        self.filters_select.addItems(["Threshold", "GammaCorrect"])



        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(255)
        self.slider.valueChanged[int].connect(self.slider_move)

        self.image_layout.addWidget(self.image_path_label)
        self.image_layout.addWidget(self.image_box)
        self.filters_layout.addWidget(self.filters_list)
        self.filters_layout.addWidget(self.filters_select)
        self.filters_layout.addWidget(self.slider)
    

        self.outer_layout.addLayout(self.filters_layout, 1)
        self.outer_layout.addLayout(self.image_layout, 3)



    def select_file(self):
        try:
            filters = "Image files (*.bmp *.dib *.jpeg *.jpg *.jpe *.jp2 *.png *.pgm *.ppm *.sr *.ras *tiff *.tif)"
            file = QFileDialog.getOpenFileName(self, "Open Image", '', filters)[0]
            self.image_box.load_image(cv2.imread(file))
            self.image_path_label.setText("File: " + file)
        except:
            error_message = QMessageBox()
            error_message.setWindowTitle("Error")
            error_message.setText("Error: file " + file +  " failed to open")
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
            file = save_window.selectedFiles()[0]

            extension = file.split('.')[-1]
            if extension == 'pgm':
                cv2.imwrite(file, cv2.cvtColor(self.image_box.filtered_image, cv2.COLOR_RGB2GRAY))
            elif extension == 'png':
                cv2.imwrite(file, self.image_box.filtered_image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
            else:
                cv2.imwrite(file, self.image_box.filtered_image)

        except:
            error_message = QMessageBox()
            error_message.setWindowTitle("Error")
            error_message.setText("Error: file " + file + " failed to save")
            error_message.exec()
    

    def open_quit_dialog(self):
        quit_dialog = QuitDialog(self)
        quit_dialog.open()



    def slider_move(self):
        print(self.slider.value())
        self.image_box.apply_filters(self.slider.value())
