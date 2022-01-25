from PyQt5.QtWidgets import QApplication, QLabel, QSizePolicy, QScrollArea, QAction, QMenu
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QPoint
import numpy as np

from opencv_processing import convert_cv_qt


class ImageRenderer(QScrollArea):

    def __init__(self, main_controller):
        super(QScrollArea, self).__init__()
        self.main_controller = main_controller
        main_controller.image_renderer = self

        self.image_area = QLabel()
        self.image_area.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored);
        self.image_area.setScaledContents(False)

        self.setWidget(self.image_area)

        # startup gradient image displayed
        self.main_controller.base_image = np.zeros((1080, 1920, 3), np.uint8)
        self.main_controller.base_image[:] = [[int(i/1920 * 255)] * 3 for i in range(0, 1920)]
        self.main_controller.filtered_image = self.main_controller.base_image

        self.image_area.setPixmap(convert_cv_qt(self.main_controller.filtered_image))

        self.scale_factor = 1
        self.image_area.resize(self.main_controller.base_image.shape[1], self.main_controller.base_image.shape[0])

        self.mouse_pos = QPoint(0, 0)
        # need both scroll area and image label tracking for panning
        self.setMouseTracking(True)
        self.image_area.setMouseTracking(True)


    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        copy_action = QAction("&Copy", self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        context_menu.addAction(copy_action)
        context_menu.popup(QCursor.pos())


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
        rows, cols, channels = self.main_controller.filtered_image.shape
        self.image_area.setPixmap(convert_cv_qt(self.main_controller.filtered_image).scaled(cols*self.scale_factor, rows*self.scale_factor, Qt.IgnoreAspectRatio, Qt.FastTransformation))

    def scale_image(self, factor):
        # scales image, then resizes image label to get correct scrollbars
        # uses a ton of memory to hold scaled image, rework later
        self.scale_factor *= factor
        rows, cols, channels = self.main_controller.filtered_image.shape
        self.image_area.setPixmap(convert_cv_qt(self.main_controller.filtered_image).scaled(cols*self.scale_factor, rows*self.scale_factor, Qt.IgnoreAspectRatio, Qt.FastTransformation))
        self.image_area.resize(cols*self.scale_factor, rows*self.scale_factor)
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

        else:
            return super().wheelEvent(wheel_event)


    def copy_to_clipboard(self):
        QApplication.clipboard().setPixmap(convert_cv_qt(self.main_controller.filtered_image))