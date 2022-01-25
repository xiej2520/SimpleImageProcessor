from PyQt5.QtWidgets import QWidget, QListWidget, QComboBox, QSlider, QPushButton, QHBoxLayout, QVBoxLayout, QSpinBox, QLabel, QGridLayout, QDoubleSpinBox, QCheckBox
from PyQt5.QtCore import Qt, QCoreApplication, QEvent, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from filters import filter_classes

class FilterEditor(QWidget):
    
    def __init__(self, controller):
        super(QWidget, self).__init__()

        self.main_controller = controller
        self.main_controller.filter_editor = self

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.filters_list = QListWidget()
        self.filters_list.itemClicked.connect(self.filter_item_clicked)
        self.prev_index = -1

        self.filters_select = QComboBox()
        for filter in filter_classes:
            self.filters_select.addItem(filter.name)
        self.filters_select.setMaxVisibleItems(20)

        self.add_filter_button = QPushButton()
        self.add_filter_button.setText("Add Filter")
        self.add_filter_button.clicked.connect(lambda: self.main_controller.add_filter(
            filter_classes[self.filters_select.currentIndex()]))
        self.remove_filter_button = QPushButton()
        self.remove_filter_button.setText("Remove Filter")
        self.remove_filter_button.clicked.connect(self.main_controller.remove_filter)
        self.up_button = QPushButton()
        self.up_button.setText("Move Up")
        self.up_button.clicked.connect(self.main_controller.move_filter_up)
        self.down_button = QPushButton()
        self.down_button.setText("Move Down")
        self.down_button.clicked.connect(self.main_controller.move_filter_down)

        self.config_panel = ConfigPanel()

        self.config_panel.paramChanged.connect(
            lambda str1, str2: 
            self.main_controller.update_argument_value(
                self.filters_list.currentRow(), str1, str2
            ) 
        )

        self.layout.addWidget(self.remove_filter_button)
        self.layout.addWidget(self.up_button)
        self.layout.addWidget(self.down_button)
        self.layout.addWidget(self.filters_list)
        self.layout.addWidget(self.config_panel)
        self.layout.addWidget(self.filters_select)
        self.layout.addWidget(self.add_filter_button)


    def filter_item_clicked(self):
        index = self.filters_list.currentRow()
        # unclick item if it is already clicked
        if index == self.prev_index:
            self.filters_list.clearSelection()
            self.filters_list.setCurrentRow(-1)
            self.prev_index = -1
            self.config_panel.remove_all_configs()
        else:
            self.prev_index = index
            # load filter's config widgets
            self.config_panel.load_filter_config(self.main_controller.current_filters[index])


class ConfigPanel(QWidget):

    paramChanged = pyqtSignal(str, str)

    def __init__(self):
        super(QWidget, self).__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def load_filter_config(self, filter):
        self.remove_all_configs()

        for param, param_type in filter.params.items():
            if param_type == "BoundedInteger":
                param_editor = BoundedIntegerEditor(param, getattr(filter, param))
                self.layout.addWidget(param_editor)
                param_editor.valueChanged.connect(lambda value, p=param: self.paramChanged.emit(p, str(value)))
            elif param_type == "BoundedDouble":
                param_editor = BoundedDoubleEditor(param, getattr(filter, param))
                self.layout.addWidget(param_editor)
                param_editor.valueChanged.connect(lambda value, p=param: self.paramChanged.emit(p, str(value)))
            elif param_type == "RadioSelect":
                param_editor = RadioSelectEditor(param, getattr(filter, param))
                self.layout.addWidget(param_editor)
                param_editor.valueChanged.connect(lambda value, p=param: self.paramChanged.emit(p, value))
            elif param_type == "Boolean":
                param_editor = BooleanEditor(param, getattr(filter, param))
                self.layout.addWidget(param_editor)
                param_editor.valueChanged.connect(lambda value, p=param: self.paramChanged.emit(p, value))


    def remove_all_configs(self):
        if self.layout != None:
            while self.layout.count():
                item = self.layout.takeAt(0)
                widget = item.widget()
                if widget != None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())


class BoundedIntegerEditor(QWidget):

    valueChanged = pyqtSignal(int)

    def __init__(self, label, BI):
        super(QWidget, self).__init__()

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label)
        self.spinbox = QSpinBox()
        
        self.spinbox.setMinimum(BI.min)
        self.spinbox.setMaximum(BI.max)
        self.spinbox.setValue(BI.value)
        self.spinbox.setSingleStep(BI.step)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(BI.min)
        self.slider.setMaximum(BI.max)
        self.slider.setTickInterval(BI.step)
        self.slider.setSingleStep(BI.step)
        self.slider.setValue(BI.value)
        self.spinbox.editingFinished.connect(self.spinbox_change)
        self.slider.valueChanged.connect(self.slider_move)

        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.spinbox, 0, 1)
        self.layout.addWidget(self.slider, 1, 0, 1, 2)

    def verifySpinbox(self):
        # ensures that spinbox value is an integer multiple of steps above minimum
        min = self.spinbox.minimum()
        val = self.spinbox.value()
        step = self.spinbox.singleStep()
        if (val - min) % step != 0:
            # sets value to closest step below input value
            self.spinbox.setValue(min + step * int((val - min) / step))

    def slider_move(self):
        self.spinbox.setValue(self.slider.value())
        # will fire off spinbox event
        keyEvent = QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.NoModifier)
        QCoreApplication.postEvent(self.spinbox, keyEvent)

    def spinbox_change(self):
        self.verifySpinbox()
        self.slider.setValue(self.spinbox.value())
        self.valueChanged.emit(self.spinbox.value())


class BoundedDoubleEditor(QWidget):

    valueChanged = pyqtSignal(float)

    def __init__(self, label, BD):
        super(QWidget, self).__init__()

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label)
        self.spinbox = QDoubleSpinBox()
        
        self.spinbox.setMinimum(BD.min)
        self.spinbox.setMaximum(BD.max)
        self.spinbox.setValue(BD.value)
        self.spinbox.setSingleStep(BD.step)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(BD.min * 100)
        self.slider.setMaximum(BD.max * 100)
        self.slider.setSingleStep(BD.step)
        self.slider.setTickInterval(BD.step)
        self.slider.setValue(BD.value * 100)
        self.spinbox.editingFinished.connect(self.spinbox_change)
        self.slider.valueChanged.connect(self.slider_move)

        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.spinbox, 0, 1)
        self.layout.addWidget(self.slider, 1, 0, 1, 2)

    def verifySpinbox(self):
        # ensures that spinbox value is an integer multiple of steps above minimum
        min = self.spinbox.minimum()
        val = self.spinbox.value()
        step = self.spinbox.singleStep()
        if (val - min) % step != 0:
            # sets value to closest step below input value
            self.spinbox.setValue(min + step * int((val - min) / step))

    def slider_move(self):
        self.spinbox.setValue(self.slider.value() / 100)
        # will fire off spinbox event
        keyEvent = QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.NoModifier)
        QCoreApplication.postEvent(self.spinbox, keyEvent)

    def spinbox_change(self):
        self.verifySpinbox()
        self.slider.setValue(self.spinbox.value() * 100)
        self.valueChanged.emit(self.spinbox.value())


class RadioSelectEditor(QWidget):

    valueChanged = pyqtSignal(str)

    def __init__(self, label, RS):
        super(QWidget, self).__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label)
        self.select_box = QComboBox()
        for option in RS.settings.keys():
            self.select_box.addItem(option)
        self.select_box.setCurrentIndex(list(RS.settings).index(RS.value))

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.select_box)

        self.select_box.currentIndexChanged.connect(lambda index: self.valueChanged.emit(list(RS.settings.keys())[index]))


class BooleanEditor(QWidget):

    valueChanged = pyqtSignal(str)

    def __init__(self, label, Bool):
        super(QWidget, self).__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label)
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(Bool)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.checkbox)

        # checkbox emits 0 for unchecked, 2 for checked
        self.checkbox.stateChanged.connect(lambda value: self.valueChanged.emit(str(value)))