from PyQt5.QtWidgets import QWidget, QListWidget, QComboBox, QSlider, QPushButton, QVBoxLayout, QSpinBox
from PyQt5.QtCore import Qt
from functools import partial

class FilterEditor(QWidget):
    
    def __init__(self, controller):
        super(QWidget, self).__init__()

        self.main_controller = controller
        self.main_controller.filter_editor = self

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.filters_list = QListWidget()
        self.filters_list.itemClicked.connect(self.filter_item_clicked)
        self.prev_index = -1

        filters_select = QComboBox()
        filters_select.addItems(["INVERT", "SPLIT_CHANNEL", "THRESHOLD", "THRESHOLD_TO_ZERO", "THRESHOLD_ADAPTIVE", "THRESHOLD_OTSU_GAUSS", "GAMMA_CORRECT", 
        "BOX_BLUR", "MEDIAN_BLUR", "GAUSSIAN_BLUR", "EROSION", "DILATION", "OPENING", "CLOSING", "GRADIENT", "ROTATE", "AFFINE", "PERSPECTIVE", "SHARPEN", "EDGE_DETECT", "EMBOSS", "SOBEL", "CONVOLVE"])
        filters_select.setMaxVisibleItems(20)

        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(0)
        self.spinbox.setMaximum(255)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(255)
        self.slider.setSingleStep(1)
        self.spinbox.valueChanged.connect(self.spinbox_change)
        self.slider.valueChanged.connect(self.slider_move)

        add_filter_button = QPushButton()
        add_filter_button.setText("Add Filter")
        add_filter_button.clicked.connect(lambda: self.main_controller.add_filter(filters_select.currentText()))
        remove_filter_button = QPushButton()
        remove_filter_button.setText("Remove Filter")
        remove_filter_button.clicked.connect(self.main_controller.remove_filter)
        up_button = QPushButton()
        up_button.setText("Move Up")
        up_button.clicked.connect(self.main_controller.move_filter_up)
        down_button = QPushButton()
        down_button.setText("Move Down")
        down_button.clicked.connect(self.main_controller.move_filter_down)

        layout.addWidget(remove_filter_button)
        layout.addWidget(up_button)
        layout.addWidget(down_button)
        layout.addWidget(self.filters_list)
        layout.addWidget(filters_select)
        layout.addWidget(self.spinbox)
        layout.addWidget(self.slider)
        layout.addWidget(add_filter_button)


    def filter_item_clicked(self, item):
        index = self.filters_list.currentRow()
        if index == self.prev_index:
            self.filters_list.clearSelection()
            self.filters_list.setCurrentRow(-1)
            self.prev_index = -1
        else:
            self.prev_index = index
        if len(self.main_controller.current_filters[index].args) > 0:
            self.slider.setValue(self.main_controller.current_filters[index].args[0])


    def slider_move(self):
        self.spinbox.setValue(self.slider.value()) # will fire off spinbox event


    def spinbox_change(self):
        self.slider.setValue(self.spinbox.value())
        self.main_controller.update_argument_value()
        #print(self.spinbox.value())
