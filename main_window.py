from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QSlider, QMessageBox
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtCore import Qt

from image_renderer import *
import filters
from opencv_processing import *


app = QApplication([])
win = QMainWindow()

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Simple Image Processor")
        
        self.central_widget = QWidget(self)    
        self.setCentralWidget(self.central_widget)

        self.vbox = QVBoxLayout()
        self.central_widget.setLayout(self.vbox)

        self.file_select_button = QPushButton("Select Image")
        self.file_select_button.clicked.connect(self.select_file)

        self.file_save_button = QPushButton("Save Image")
        self.file_save_button.clicked.connect(self.save_file)

        self.image_path_label = QLabel("File: ")

        self.image_box = ImageRenderer()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(255)
        self.slider.valueChanged[int].connect(self.slider_move)



        self.vbox.addWidget(self.file_select_button)
        self.vbox.addWidget(self.file_save_button)
        self.vbox.addWidget(self.image_path_label)
        self.vbox.addWidget(self.image_box)
        self.vbox.addWidget(self.slider)


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
        


    def slider_move(self):
        print(self.slider.value())
        self.image_box.apply_filters(self.slider.value())
