import cv2
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


def convert_cv_qt(cv_img):
    """Convert from an opencv image to QPixmap"""
    height, width, channels = cv_img.shape
    bytes_per_line = channels * width
    qimg = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
    return QPixmap.fromImage(qimg)