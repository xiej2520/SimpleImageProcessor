
import numpy as np
import cv2
from filter_wrapper import Filter_Wrapper


class MainController():

    def __init__(self):

        # pointers for calling methods
        self.image_path_label = None
        self.image_renderer = None
        self.filter_editor = None

        # data
        self.file_path = ""
        # Holds the cv2 image which is converted to QPixmap when displayed
        self.base_image = None
        # starts pointing to base
        self.filtered_image = self.base_image

        self.current_filters = []


    def reload_file(self):
        self.image_renderer.load_image(cv2.imread(self.file_path))
        self.image_path_label.setText("File: " + self.file_path)
        self.image_renderer.apply_filters(self.current_filters)


    def write_file(self, save_path):
        extension = save_path.split('.')[-1]
        if extension == 'pgm':
            cv2.imwrite(save_path, cv2.cvtColor(self.filtered_image, cv2.COLOR_RGB2GRAY))
        elif extension == 'png':
            cv2.imwrite(save_path, self.filtered_image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        else:
            cv2.imwrite(save_path, self.filtered_image)


    def add_filter(self, filter_name):
        if filter_name == "GAMMA_CORRECT" or "THRESHOLD" or "THRESHOLD_TOZERO":
            args = [self.filter_editor.spinbox.value()]
        else:
            args = []
        self.current_filters.append(Filter_Wrapper(filter_name, args))
        self.filter_editor.filters_list.addItem(filter_name)
        self.filter_editor.filters_list.setCurrentRow(len(self.current_filters)-1)
        self.image_renderer.apply_filters(self.current_filters)


    def remove_filter(self):
        index = self.filter_editor.filters_list.currentRow()
        if index >= 0:
            self.current_filters.pop(index)
            self.filter_editor.filters_list.takeItem(index)
            index -= 1
            if index >= 0 and len(self.current_filters[index].args) > 0:
                self.filter_editor.slider.setValue(self.current_filters[index].args[0])
            self.image_renderer.apply_filters(self.current_filters)


    def move_filter_up(self):
        index = self.filter_editor.filters_list.currentRow()
        print("UP")
        print(index)
        if index > 0:
            self.current_filters[index-1], self.current_filters[index] = self.current_filters[index], self.current_filters[index-1]
            self.filter_editor.filters_list.insertItem(index-1, self.filter_editor.filters_list.takeItem(index))
            self.filter_editor.filters_list.setCurrentRow(index-1)
            self.image_renderer.apply_filters(self.current_filters)


    def move_filter_down(self):
        index = self.filter_editor.filters_list.currentRow()
        print("DOWN")
        print(index)
        if index < len(self.current_filters)-1:
            self.current_filters[index], self.current_filters[index+1] = self.current_filters[index+1], self.current_filters[index]
            self.filter_editor.filters_list.insertItem(index+1, self.filter_editor.filters_list.takeItem(index))
            self.filter_editor.filters_list.setCurrentRow(index+1)
            self.image_renderer.apply_filters(self.current_filters)


    def update_argument_value(self):
        if self.filter_editor.filters_list.count() > 0:
            index = self.filter_editor.filters_list.currentRow()
            if len(self.current_filters[index].args) == 0:
                self.current_filters[index].args.append(0)
            self.current_filters[index].args[0] = self.filter_editor.spinbox.value()
            self.image_renderer.apply_filters(self.current_filters)