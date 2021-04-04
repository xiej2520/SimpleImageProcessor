from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtCore import Qt, QPoint
import cv2
from filters import *
from opencv_processing import *
import random


class ImageRenderer(QScrollArea):

    def __init__(self):
        super(QScrollArea, self).__init__()

        self.image_area = QLabel()
        self.image_area.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored);
        self.image_area.setScaledContents(True)


        self.setWidget(self.image_area)

        # Holds the cv2 image which is converted to QPixmap when displayed
        self.base_image = np.zeros((1080, 1920, 3), np.uint8)
        self.base_image[:] = [[int(i/1920 * 255)] * 3 for i in range(0, 1920)]

        # starts pointing to base
        self.filtered_image = self.base_image
        self.image_area.setPixmap(convert_cv_qt(self.filtered_image))

        self.scale_factor = 1
        self.image_area.resize(self.base_image.shape[1], self.base_image.shape[0])

        self.mouse_pos = QPoint(0, 0)
        self.setMouseTracking(True)
        self.image_area.setMouseTracking(True)


    def load_image(self, img):
        self.base_image = img
        self.filtered_image = self.base_image
        self.scale_factor = 1
        self.image_area.resize(self.filtered_image.shape[1], self.filtered_image.shape[0])
        self.image_area.setPixmap(convert_cv_qt(self.filtered_image))
    

    def apply_filters(self, t):
        self.filtered_image = threshold(self.base_image, t)
        self.image_area.setPixmap(convert_cv_qt(self.filtered_image))


    def scale_image(self, factor):
        # scales image by scaling the image label
        self.scale_factor *= factor
        self.image_area.resize(self.scale_factor * self.filtered_image.shape[1], self.scale_factor * self.filtered_image.shape[0])
        # shifts scrollbars to keep image pixel under the mouse fixed
        self.horizontalScrollBar().setValue((self.horizontalScrollBar().value()+self.mouse_pos.x()) * factor - self.mouse_pos.x())
        self.verticalScrollBar().setValue((self.verticalScrollBar().value()+self.mouse_pos.y()) * factor - self.mouse_pos.y())

    """
    def mousePressEvent(self, mouse_event):
        if mouse_event.button() == Qt.MidButton:
            self.setCursor(Qt.OpenHandCursor)
    """

    def mouseMoveEvent(self, mouse_event):
        if mouse_event.buttons() == Qt.MidButton:
            self.setCursor(Qt.OpenHandCursor)
            x = self.horizontalScrollBar().value()
            y = self.verticalScrollBar().value()

            delta = mouse_event.localPos() - self.mouse_pos

            self.horizontalScrollBar().setValue(int(x - delta.x()))
            self.verticalScrollBar().setValue(int(y - delta.y()))

        
        self.mouse_pos = mouse_event.localPos()


    # zoom in/out on ctrl+mouse wheel
    def wheelEvent(self, wheel_event):

        zoom_factor = 1.25

        if wheel_event.modifiers() == Qt.ControlModifier:
            # FLOATING POINT ERRORS
            if wheel_event.angleDelta().y() > 0 and self.scale_factor < zoom_factor ** 3:
                self.scale_image(zoom_factor)

            elif wheel_event.angleDelta().y() < 0 and self.scale_factor > (1/zoom_factor ** 3):
                self.scale_image(1/zoom_factor)
            print(self.scale_factor)

        else:
            return super().wheelEvent(wheel_event)
