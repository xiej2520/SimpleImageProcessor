from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QSlider
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtCore import Qt
import filters
from opencv_processing import *


app = QApplication([])
win = QMainWindow()

class Main(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Main, self).__init__(*args, **kwargs)
        self.setWindowTitle("Simple Image Processor")
        
        self.central_widget = QWidget(self)    
        self.setCentralWidget(self.central_widget)

        self.vbox = QVBoxLayout()
        self.central_widget.setLayout(self.vbox)

        self.file_select_button = QPushButton("Select Image")
        self.file_select_button.clicked.connect(self.select_file)

        self.image_path_label = QLabel("File: ")

        self.loadedImageBox = QLabel()
        self.loadedImageBox.setMaximumWidth(1920)
        self.loadedImageBox.setMaximumHeight(1080)
        self.loadedImage = QPixmap(1920, 1080)
        self.loadedImage.fill(QColor(200, 50, 230))
        self.loadedImageBox.setPixmap(self.loadedImage)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(255)
        self.slider.valueChanged[int].connect(self.slider_move)



        self.vbox.addWidget(self.file_select_button)
        self.vbox.addWidget(self.image_path_label)
        self.vbox.addWidget(self.loadedImageBox)
        self.vbox.addWidget(self.slider)


    def select_file(self):
        self.image_path_label.setText("File: " + QFileDialog.getOpenFileName()[0])
        self.loadedImage = convert_cv_qt(cv2.imread(self.image_path_label.text()[6:]))
        self.loadedImageBox.setPixmap(self.loadedImage)

    def slider_move(self):
        print(self.slider.value())
        self.loadedImage = convert_cv_qt(filters.threshold(cv2.imread(self.image_path_label.text()[6:]), self.slider.value()))
        self.loadedImageBox.setPixmap(self.loadedImage)