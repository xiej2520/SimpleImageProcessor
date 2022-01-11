from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtCore import Qt, QPoint
import numpy as np
import random

import cv2
import filters
from opencv_processing import convert_cv_qt


class ImageRenderer(QScrollArea):

    def __init__(self, main_controller):
        super(QScrollArea, self).__init__()
        self.main_controller = main_controller
        main_controller.image_renderer = self

        self.image_area = QLabel()
        self.image_area.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored);
        self.image_area.setScaledContents(True)

        self.setWidget(self.image_area)

        self.image_area.setPixmap(convert_cv_qt(self.main_controller.filtered_image))

        self.scale_factor = 1
        self.image_area.resize(self.main_controller.base_image.shape[1], self.main_controller.base_image.shape[0])

        self.mouse_pos = QPoint(0, 0)
        # need both scroll area and image label tracking for panning
        self.setMouseTracking(True)
        self.image_area.setMouseTracking(True)


    def load_image(self, img):
        self.main_controller.base_image = img
        self.main_controller.filtered_image = self.main_controller.base_image
        self.scale_factor = 1
        self.image_area.resize(self.main_controller.filtered_image.shape[1], self.main_controller.filtered_image.shape[0])
        self.image_area.setPixmap(convert_cv_qt(self.main_controller.filtered_image))


    def apply_filters(self, filters_list):
        self.main_controller.filtered_image = self.main_controller.base_image
        for filter in filters_list:
            self.main_controller.filtered_image = filter.apply(self.main_controller.filtered_image)
        self.image_area.setPixmap(convert_cv_qt(self.main_controller.filtered_image))

    def scale_image(self, factor):
        # scales image by scaling the image label
        self.scale_factor *= factor
        self.image_area.resize(self.scale_factor * self.main_controller.filtered_image.shape[1], self.scale_factor * self.main_controller.filtered_image.shape[0])
        # shifts scrollbars to keep image pixel under the mouse fixed
        self.horizontalScrollBar().setValue((self.horizontalScrollBar().value()+self.mouse_pos.x()) * factor - self.mouse_pos.x())
        self.verticalScrollBar().setValue((self.verticalScrollBar().value()+self.mouse_pos.y()) * factor - self.mouse_pos.y())


    def mouseMoveEvent(self, mouse_event):
        if mouse_event.buttons() == Qt.MidButton:
            self.setCursor(Qt.OpenHandCursor)
            x = self.horizontalScrollBar().value()
            y = self.verticalScrollBar().value()

            delta = mouse_event.localPos() - self.mouse_pos

            self.horizontalScrollBar().setValue(int(x - delta.x()))
            self.verticalScrollBar().setValue(int(y - delta.y()))
        else:
            self.setCursor(Qt.ArrowCursor)
        
        self.mouse_pos = mouse_event.localPos()


    # zoom in/out on ctrl+mouse wheel
    def wheelEvent(self, wheel_event):

        zoom_factor = 1.25

        if wheel_event.modifiers() == Qt.ControlModifier:
            # FLOATING POINT ERRORS
            if wheel_event.angleDelta().y() > 0 and self.scale_factor < zoom_factor ** 4:
                self.scale_image(zoom_factor)

            elif wheel_event.angleDelta().y() < 0 and self.scale_factor > (1/zoom_factor ** 4):
                self.scale_image(1/zoom_factor)
            print(self.scale_factor)

        else:
            return super().wheelEvent(wheel_event)
