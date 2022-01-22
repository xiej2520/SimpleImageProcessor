import cv2
from cv2 import getStructuringElement
import numpy as np
from abc import ABC, abstractmethod

def clamp(minvalue, value, maxvalue):
    return max(minvalue, min(value, maxvalue))


class BoundedDouble():

    def __init__(self, value, min, max):
        self._value = value
        self._min = min
        self._max = max

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self._value = clamp(value, self._min, self._max)

    def _get_min(self):
        return self._min

    def _set_min(self, min):
        self._min = min

    def _get_max(self):
        return self._max

    def _set_max(self, max):
        self._max = max

    value = property(_get_value, _set_value)
    min = property(_get_min, _set_min)
    max = property(_get_max, _set_max)


class BoundedInteger(BoundedDouble):

    def __init__(self, value, min, max):
        super().__init__(self, int(value), int(min), int(max))

    def _set_value(self, value):
        super()._set_value(int(value))

    def _set_min(self, min):
        super()._set_min(int(min))

    def _set_max(self, max):
        super()._set_max(int(max))


class RadioSelect():

    def __init__(self, values, default=None):
        if default != None:
            self._value = default
        else:
            self._value = values[0]
        self.settings = dict.fromkeys(values, False)
        self.settings[self._value] = True

    def _set_value(self, value):
        self.settings[self._value] = False
        self.settings[value] = True
        self._value = value

    def _get_value(self):
        return self._value

    value = property(_get_value, _set_value)


BorderTypes = ["BORDER_CONSTANT", "BORDER_REPLICATE", "BORDER_REFLECT", "BORDER_WRAP", "BORDER_REFLECT_101", "BORDER_TRANSPARENT", "BORDER_ISOLATED"]
MorphShapes = ["MORPH_RECT", "MORPH_CROSS", "MORPH_ELLIPSE"]
MorphTypes = ["MORPH_OPEN", "MORPH_CLOSE", "MORPH_GRADIENT", "MORPH_TOPHAT", "MORPH_BLACKHAT"]
InterpolationFlags = ["INTER_NEAREST", "INTER_LINEAR", "INTER_CUBIC", "INTER_AREA", "INTER_LANCZOS4", "INTER_NEAREST_EXACT", "INTER_MAX", "WARP_FILL_OUTLIERS", "WARP_INVERSE_MAP"]


class Filter(ABC):

    name = "Filter"
    args = {"active": "Boolean"}

    def __init__(self):
        self.active = False

    @abstractmethod
    def apply(self, img):
        pass


class FilterInvert(Filter):

    name = "Invert"

    def apply(self, img):
        if self.active:
            return cv2.bitwise_not(img)


class FilterSplitChannel(Filter):

    name = "Split Channel"
    args = {"active": "Boolean", "channel": "RadioSelect"}

    def __init__(self):
        self.channel = RadioSelect(["Red", "Green", "Blue"])

    def apply(self, img):
        if self.active:
            zero = np.zeros_like(img[:,:,0])
            if (self.channel.value == "Red"):
                return np.dstack((zero, zero, img[:,:,2]))
            elif (self.channel.value == "Blue"):
                return np.dstack((zero, img[:,:,1], zero))
            else:
                return np.dstack((img[:,:,0], zero, zero))


class FilterGammaCorrect(Filter):

    name = "Gamma Correct"
    args = {"active": "Boolean", "gamma": "BoundedDouble"}

    def __init__(self):
        self.gamma = BoundedDouble(1, 0, 10)

    def apply(self, img):
        if self.active:
            LUT = np.empty((1, 256), np.uint8)
            for i in range(256):
                LUT[0, i] = np.clip(pow(i/255.0, self.gamma.value) * 255.0, 0, 255)

            return cv2.LUT(img, LUT)


class FilterThreshold(Filter):

    name = "Threshold"
    args = {"active": "Boolean", "threshold": BoundedInteger, "max_value": BoundedInteger}

    def __init__(self):
        self.threshold = BoundedInteger(0, 0, 255)
        self.max_value = BoundedInteger(255, 0, 255)

    def apply(self, img):
        if self.active:
            return cv2.threshold(img, self.threshold.value, self.max_value.value, cv2.THRESH_BINARY)[1]


class FilterThresholdToZero(Filter):

    name = "Threshold to Zero"
    args = {"active": "Boolean", "threshold": BoundedInteger}

    def __init__(self):
        self.threshold = BoundedInteger(0, 0, 255)

    def apply(self, img):
        if self.active:
            return cv2.threshold(img, self.threshold.value, cv2.THRESH_TOZERO)[1]


class FilterThresholdAdaptive(Filter):

    name = "Adaptive Threshold"
    args = {
        "active": "Boolean",
        "max_value": "BoundedInteger",
        "adaptive_method": "RadioSelect",
        "threshold_type": "RadioSelect",
        "block_size": "BoundedInteger",
        "constant": "BoundedInteger"}

    def __init__(self):
        self.max_value = BoundedInteger(255, 0, 255)
        self.adaptive_method = RadioSelect(["ADAPTIVE_THRESH_MEAN_C", "ADAPTIVE_THRESH_GAUSSIAN_C"])
        self.threshold_type = RadioSelect(["THRESH_BINARY", "THRESH_BINARY_INV"])
        self.block_size = BoundedInteger(3, 3, 255)
        self.constant = BoundedInteger(0, -255, 255)

    def apply(self, img):
        if self.active:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #am = cv2.ADAPTIVE_THRESH_MEAN_C if self.adaptive_method == "ADAPTIVE_THRES_MEAN_C" else cv2.ADAPTIVE_THRESH_GAUSSIAN_C
            #tt = cv2.THRESH_BINARY if self.threshold_type == "THRESH_BINARY" else cv2.THRESH_BINARY_INV
            filtered_img = cv2.adaptiveThreshold(
                img_gray, 
                self.max_value.value, 
                getattr(cv2, self.adaptive_method.value), 
                getattr(cv2, self.threshold_type.value), 
                self.block_size.value, 
                self.constant.value
            )
            return cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)


class FilterThresholdOtsuGauss(Filter):

    name = "Otsu's Binarization Threshold"
    args = {"active": "Boolean", "max_value": "BoundedInteger"}

    def __init__(self):
        self.max_value = BoundedInteger(255, 0, 255)

    def apply(self, img):
        if self.active:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            filtered_img = cv2.threshold(img_gray, 0, self.max_value.value, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
            return cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)


class FilterBoxBlur(Filter):

    name = "Box Blur"
    args = {"active": "Boolean", "kernel_width": "BoundedInteger", "kernel_height": "BoundedInteger", "border_type": "RadioSelect"}

    def __init__(self):
        self.kernel_width = BoundedInteger(3, 1, 255)
        self.kernel_height = BoundedInteger(3, 1, 255)
        self.border_type = RadioSelect(BorderTypes, "BORDER_DEFAULT")

    def apply(self, img):
        if self.active:
            return cv2.blur(img, (self.kernel_width.value, self.kernel_height.value), borderType=getattr(cv2, self.border_type.value))


class FilterMedianBlur(Filter):

    name = "Median Blur"
    args = {"active": "Boolean", "kernel_width": "BoundedInteger", "kernel_height": "BoundedInteger"}

    def __init__(self):
        self.kernel_width = BoundedInteger(3, 1, 255)
        self.kernel_height = BoundedInteger(3, 1, 255)

    def apply(self, img):
        if self.active:
            return cv2.medianBlur(img, (
                self.kernel_width.value + (1 if self.kernel_width.value & 2 == 0 else 0), 
                self.kernel_height.value+ (1 if self.kernel_height.value & 2 == 0 else 0)
            ))


class FilterGaussianBlur(Filter):

    name = "Gaussian Blur"
    args = {
        "active": "Boolean", 
        "kernel_width": "BoundedInteger", 
        "kernel_height": "BoundedInteger", 
        "sigma_x": "BoundedDouble", 
        "sigma_y": "BoundedDouble", 
        "border_type": "RadioSelect"
    }

    def __init__(self):
        self.kernel_width = BoundedInteger(3, 0, 255)
        self.kernel_height = BoundedInteger(3, 0, 255)
        self.sigma_x = BoundedDouble(0, 0, 5)
        self.sigma_y = BoundedDouble(0, 0, 5)
        valid_border_types = BorderTypes.copy().remove("BORDER_WRAP")
        self.border_type = RadioSelect(valid_border_types, "BORDER_DEFAULT")

    def apply(self, img):
        if self.active:
            parsed_kw = self.kernel_width.value
            parsed_kh = self.kernel_height.value
            if self.kernel_width.value != 0 and self.kernel_width.value % 2 == 0:
                parsed_kw += 1
            if self.kernel_height.value != 0 and self.kernel_height.value % 2 == 0:
                parsed_kh += 1
            return cv2.GaussianBlur(img, (parsed_kw, parsed_kh), self.sigma_x.value, self.sigma_y.value, self.border_type.value)


class FilterErode(Filter):

    name = "Erode"
    args = {
        "active": "Boolean", 
        "kernel_type": "RadioSelect", 
        "kernel_width": "BoundedInteger", 
        "kernel_height": "BoundedInteger", 
        "iterations": "BoundedInteger", 
        "border_type": "RadioSelect", 
        "border_value": "BoundedInteger"
        }

    def __init__(self):
        self.kernel_type = RadioSelect(MorphShapes)
        self.kernel_width = BoundedInteger(3, 1, 255)
        self.kernel_height = BoundedInteger(3, 1, 255)
        self.iterations = BoundedInteger(1, 1, 255)
        valid_border_types = BorderTypes.copy().remove("BORDER_WRAP")
        self.border_type = RadioSelect(valid_border_types, "BORDER_CONSTANT")
        self.border_value = cv2.morphologyDefaultBorderValue()

    def apply(self, img):
        if self.active:
            kernel = cv2.getStructuringElement(
                getattr(cv2, self.kernel_type.value), 
                (self.kernel_width.value, self.kernel_height.value)
            )
            return cv2.erode(img, kernel, 
                iterations=self.iterations.value, 
                borderType=getattr(cv2.self.border_type.value), 
                borderValue=self.border_value.value
            )


class FilterDilate(FilterErode):

    name = "Dilate"

    def __init__(self):
        super().__init__()

    def apply(self, img):
        if self.active:
            kernel = cv2.getStructuringElement(
                getattr(cv2, self.kernel_type.value), 
                (self.kernel_width.value, self.kernel_height.value)
            )
            return cv2.dilate(img, kernel, 
                iterations=self.iterations.value, 
                borderType=getattr(cv2.self.border_type.value), 
                borderValue=self.border_value.value
            )


class FilterMorphologyEx(FilterErode):

    name = "Morphological Transformation"
    super().args["operation"] = "RadioSelect"

    def __init__(self):
        super().init__()
        self.operation = RadioSelect(MorphTypes)

    def apply(self, img):
        if self.active:
            kernel = cv2.getStructuringElement(
                getattr(cv2, self.kernel_type.value), 
                (self.kernel_width.value, self.kernel_height.value)
            )
            return cv2.morphologyEx(
                img, 
                getattr(cv2, self.operation.value), 
                kernel, 
                iterations=self.iterations.value, 
                borderType=getattr(cv2.self.border_type.value), 
                borderValue=self.border_value.value
            )


class WarpRotate(Filter):

    name = "Rotate"
    args = {"active": "Boolean", "theta": "BoundedDouble"}

    def __init__(self):
        self.theta = BoundedDouble(0, -360, 360)

    def apply(self, img):
        if self.active:
            rows, cols, channels = img.shape
            mat = cv2.getRotationMatrix2D(((cols-1)/2.0, (rows-1)/2.0), self.theta.value, 1)
            return cv2.warpAffine(img, mat, (cols,rows))


class WarpAffine(Filter):

    name = "Affine"
    args = {
        "active": "Boolean", 
        "M11": "BoundedDouble", 
        "M12": "BoundedDouble", 
        "M13": "BoundedDouble", 
        "M21": "BoundedDouble", 
        "M22": "BoundedDouble", 
        "M23": "BoundedDouble", 
        "flags": "RadioSelect",
        "border_mode": "RadioSelect",
        "border_value": "BoundedDouble"
        }

    def __init__(self):
        self.M11 = BoundedDouble(0, -1024, 1024)
        self.M12 = BoundedDouble(0, -1024, 1024)
        self.M13 = BoundedDouble(0, -1024, 1024)
        self.M21 = BoundedDouble(0, -1024, 1024)
        self.M22 = BoundedDouble(0, -1024, 1024)
        self.M23 = BoundedDouble(0, -1024, 1024)
        self.flags = RadioSelect(InterpolationFlags, "INTER_LINEAR")
        self.border_mode = RadioSelect(BorderTypes, "BORDER_CONSTANT")
        self.border_value = BoundedInteger(0, 0, 255)

    def apply(self, img):
        if self.active:
            rows, cols, channels = img.shape
            mat = [[self.M11.value, self.M12.value, self.M13.value], [self.M21.value, self.M22.value, self.M23.value]]
            return cv2.warpAffine(img, mat, (cols, rows), 
                getattr(cv2, self.flags.value), 
                getattr(cv2, self.border_mode.value), 
                getattr(cv2, self.border_value.value)
            )


class WarpPerspective(Filter):

    name = "Perspective"
    args = {
        "active": "Boolean", 
        "M11": "BoundedDouble", 
        "M12": "BoundedDouble", 
        "M13": "BoundedDouble", 
        "M21": "BoundedDouble", 
        "M22": "BoundedDouble", 
        "M23": "BoundedDouble", 
        "M31": "BoundedDouble", 
        "M32": "BoundedDouble", 
        "M33": "BoundedDouble", 
        "flags": "RadioSelect",
        "border_mode": "RadioSelect",
        "border_value": "BoundedDouble"
        }

    def __init__(self):
        self.M11 = BoundedDouble(0, -1024, 1024)
        self.M12 = BoundedDouble(0, -1024, 1024)
        self.M13 = BoundedDouble(0, -1024, 1024)
        self.M21 = BoundedDouble(0, -1024, 1024)
        self.M22 = BoundedDouble(0, -1024, 1024)
        self.M23 = BoundedDouble(0, -1024, 1024)
        self.M31 = BoundedDouble(0, -1024, 1024)
        self.M32 = BoundedDouble(0, -1024, 1024)
        self.M33 = BoundedDouble(0, -1024, 1024)
        self.flags = RadioSelect(InterpolationFlags, "INTER_LINEAR")
        self.border_mode = RadioSelect(BorderTypes, "BORDER_CONSTANT")
        self.border_value = BoundedInteger(0, 0, 255)

    def apply(self, img):
        if self.active:
            rows, cols, channels = img.shape
            mat = [
                [self.M11.value, self.M12.value, self.M13.value], 
                [self.M21.value, self.M22.value, self.M23.value], 
                [self.M31.value, self.M32.value, self.M33.value]
            ]
            return cv2.warpAffine(img, mat, (cols, rows), 
                getattr(cv2, self.flags.value), 
                getattr(cv2, self.border_mode.value), 
                getattr(cv2, self.border_value.value)
            )


class WarpPolar(Filter):

    name = "Warp Polar"
    args = {"active": "Boolean", "max_radius": "BoundedInteger", "flags": "RadioSelect", "POLAR_LOG": "Boolean", "INVERSE_MAP": "Boolean"}

    def __init__(self):
        self.max_radius = BoundedInteger(1, 0, 255)
        self.flags = RadioSelect(InterpolationFlags)
        self.POLAR_LOG = False
        self.INVERSE_MAP = False

    def apply(self, img):
        if self.active:
            flag = self.flags.value
            if self.POLAR_LOG:
                flag += cv2.WARP_POLAR_LOG
            if self.INVERSE_MAP:
                flag += cv2.WARP_INVERSE_MAP
            rows, cols, channels = img.shape
            return cv2.warpPolar(img, (cols, rows), ((cols-1)/2.0, (rows-1)/2.0), self.max_radius.value, flag)

class FilterConvolvePresets(Filter):

    name = "Convolve Presets"
    args = {"active": "Boolean", "preset": "RadioSelect"}

    def __init__(self):
        self.preset = RadioSelect(["SHARPEN", "EDGE_DETECT", "EMBOSS", "SOBEL"])
        valid_border_types = BorderTypes.copy().remove("BORDER_WRAP")
        self.border_type = RadioSelect(valid_border_types, "BORDER_DEFAULT")

    def apply(self, img):
        if self.preset.value == "SHARPEN":
            kernel = np.array([
                [0, -1, 0],
                [-1, 5, -1],
                [0, -1, 0]
                ])
        elif self.preset.value == "EDGE_DETECT":
            kernel = np.array([
                [-1, -1, -1],
                [-1, 8, -1],
                [-1, -1, -1]
                ])
        elif self.preset.value == "EMBOSS":
            kernel = np.array([
            [-2, -1, 0],
            [-1, 1, 1],
            [0, 1, 2]
            ])
        elif self.preset.value == "SOBEL":
            kernel = np.array([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
            ])

        return cv2.fitler2D(img, -1, kernel, borderType=self.border_type.value)


class FilterConvolve(Filter):

    name = "Convolve"
    args = {
        "active": "Boolean", 
        "M11": "BoundedDouble", 
        "M12": "BoundedDouble", 
        "M13": "BoundedDouble", 
        "M21": "BoundedDouble", 
        "M22": "BoundedDouble", 
        "M23": "BoundedDouble", 
        "M31": "BoundedDouble", 
        "M32": "BoundedDouble", 
        "M33": "BoundedDouble",
        "anchor_x": "BoundedInteger",
        "anchor_y": "BoundedInteger",
        "delta": "BoundedInteger",
        "border_type": "RadioSelect"
        }

    def __init__(self):
        self.M11 = BoundedDouble(0, -10, 10)
        self.M12 = BoundedDouble(0, -10, 10)
        self.M13 = BoundedDouble(0, -10, 10)
        self.M21 = BoundedDouble(0, -10, 10)
        self.M22 = BoundedDouble(1, -10, 10)
        self.M23 = BoundedDouble(0, -10, 10)
        self.M31 = BoundedDouble(0, -10, 10)
        self.M32 = BoundedDouble(0, -10, 10)
        self.M33 = BoundedDouble(0, -10, 10)
        self.anchor_x = BoundedInteger(-1, -1, 3)
        self.anchor_y = BoundedInteger(-1, -1, 3)
        self.delta = BoundedInteger(0, -255, 255)
        valid_border_types = BorderTypes.copy().remove("BORDER_WRAP")
        self.border_type = RadioSelect(valid_border_types, "BORDER_DEFAULT")

    def apply(self, img):
        kernel = [[self.M11.value, self.M12.value, self.M13.value], [self.M21.value, self.M22.value, self.M23.value], [self.M31.value, self.M32.value, self.M33.value]]
        return cv2.fitler2D(img, -1, kernel, (self.anchor_x.value, self.anchor_y.value), self.delta.value, self.border_type.value)