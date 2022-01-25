import cv2
import numpy as np
from abc import ABC, abstractmethod
from filter_parameter_types import *


BorderTypes = ["BORDER_CONSTANT", "BORDER_REPLICATE", "BORDER_REFLECT", "BORDER_WRAP", "BORDER_REFLECT_101", "BORDER_TRANSPARENT", "BORDER_ISOLATED"]
MorphShapes = ["MORPH_RECT", "MORPH_CROSS", "MORPH_ELLIPSE"]
MorphTypes = ["MORPH_OPEN", "MORPH_CLOSE", "MORPH_GRADIENT", "MORPH_TOPHAT", "MORPH_BLACKHAT"]
InterpolationFlags = ["INTER_NEAREST", "INTER_LINEAR", "INTER_CUBIC", "INTER_AREA", "INTER_LANCZOS4", "INTER_NEAREST_EXACT", "INTER_MAX", "WARP_FILL_OUTLIERS", "WARP_INVERSE_MAP"]


class Filter(ABC):

    name = "Filter"
    params = {"active": "Boolean"}

    def __init__(self):
        self.active = True

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
    params = {"active": "Boolean", "channel": "RadioSelect"}

    def __init__(self):
        super().__init__()
        self.channel = RadioSelect(["Red", "Green", "Blue"])

    def apply(self, img):
        if self.active:
            zero = np.zeros_like(img[:,:,0])
            if (self.channel.value == "Red"):
                return np.dstack((zero, zero, img[:,:,2]))
            elif (self.channel.value == "Green"):
                return np.dstack((zero, img[:,:,1], zero))
            else:
                return np.dstack((img[:,:,0], zero, zero))
        else:
            return img


class FilterGammaCorrect(Filter):

    name = "Gamma Correct"
    params = {"active": "Boolean", "gamma": "BoundedDouble"}

    def __init__(self):
        super().__init__()
        self.gamma = BoundedDouble(1, 0, 10)

    def apply(self, img):
        if self.active:
            LUT = np.empty((1, 256), np.uint8)
            for i in range(256):
                LUT[0, i] = np.clip(pow(i/255.0, self.gamma.value) * 255.0, 0, 255)

            return cv2.LUT(img, LUT)
        else:
            return img


class FilterThreshold(Filter):

    name = "Threshold"
    params = {"active": "Boolean", "threshold": "BoundedInteger", "max_value": "BoundedInteger"}

    def __init__(self):
        super().__init__()
        self.threshold = BoundedInteger(0, 0, 255)
        self.max_value = BoundedInteger(255, 0, 255)

    def apply(self, img):
        if self.active:
            return cv2.threshold(img, self.threshold.value, self.max_value.value, cv2.THRESH_BINARY)[1]
        else:
            return img


class FilterThresholdToZero(Filter):

    name = "Threshold to Zero"
    params = {"active": "Boolean", "threshold": "BoundedInteger"}

    def __init__(self):
        super().__init__()
        self.threshold = BoundedInteger(0, 0, 255)

    def apply(self, img):
        if self.active:
            return cv2.threshold(img, self.threshold.value, 255, cv2.THRESH_TOZERO)[1]
        else:
            return img


class FilterThresholdAdaptive(Filter):

    name = "Adaptive Threshold"
    params = {
        "active": "Boolean",
        "max_value": "BoundedInteger",
        "adaptive_method": "RadioSelect",
        "threshold_type": "RadioSelect",
        "block_size": "BoundedInteger",
        "constant": "BoundedInteger"}

    def __init__(self):
        super().__init__()
        self.max_value = BoundedInteger(255, 0, 255)
        self.adaptive_method = RadioSelect(["ADAPTIVE_THRESH_MEAN_C", "ADAPTIVE_THRESH_GAUSSIAN_C"])
        self.threshold_type = RadioSelect(["THRESH_BINARY", "THRESH_BINARY_INV"])
        self.block_size = BoundedInteger(3, 3, 255)
        self.constant = BoundedInteger(0, -64, 64)

    def apply(self, img):
        if self.active:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            parsed_block = self.block_size.value
            if parsed_block != 0 and parsed_block % 2 == 0:
                parsed_block += 1
            filtered_img = cv2.adaptiveThreshold(
                img_gray, 
                self.max_value.value, 
                getattr(cv2, self.adaptive_method.value), 
                getattr(cv2, self.threshold_type.value), 
                parsed_block, 
                self.constant.value
            )
            return cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)
        else:
            return img


class FilterThresholdOtsuGauss(Filter):

    name = "Otsu's Binarization Threshold"
    params = {"active": "Boolean", "max_value": "BoundedInteger"}

    def __init__(self):
        super().__init__()
        self.max_value = BoundedInteger(255, 0, 255)

    def apply(self, img):
        if self.active:
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            filtered_img = cv2.threshold(img_gray, 0, self.max_value.value, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
            return cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)
        else:
            return img


class FilterBoxBlur(Filter):

    name = "Box Blur"
    params = {"active": "Boolean", "kernel_width": "BoundedInteger", "kernel_height": "BoundedInteger", "border_type": "RadioSelect"}

    def __init__(self):
        super().__init__()
        self.kernel_width = BoundedInteger(3, 1, 255)
        self.kernel_height = BoundedInteger(3, 1, 255)
        valid_border_types = BorderTypes.copy()
        valid_border_types.remove("BORDER_WRAP")
        valid_border_types.remove("BORDER_TRANSPARENT")
        self.border_type = RadioSelect(valid_border_types, "BORDER_DEFAULT")

    def apply(self, img):
        if self.active:
            return cv2.blur(img, (self.kernel_width.value, self.kernel_height.value), borderType=getattr(cv2, self.border_type.value))
        else:
            return img


class FilterMedianBlur(Filter):

    name = "Median Blur"
    params = {"active": "Boolean", "ksize": "BoundedInteger"}

    def __init__(self):
        super().__init__()
        self.ksize = BoundedInteger(3, 1, 255)

    def apply(self, img):
        if self.active:
            return cv2.medianBlur(img, 
                (self.ksize.value + (1 if self.ksize.value % 2 == 0 else 0)), 
            )
        else:
            return img


class FilterGaussianBlur(Filter):

    name = "Gaussian Blur"
    params = {
        "active": "Boolean", 
        "kernel_width": "BoundedInteger", 
        "kernel_height": "BoundedInteger", 
        "sigma_x": "BoundedDouble", 
        "sigma_y": "BoundedDouble", 
        "border_type": "RadioSelect"
    }

    def __init__(self):
        super().__init__()
        self.kernel_width = BoundedInteger(3, 0, 255)
        self.kernel_height = BoundedInteger(3, 0, 255)
        self.sigma_x = BoundedDouble(0, 0, 63)
        self.sigma_y = BoundedDouble(0, 0, 63)
        valid_border_types = BorderTypes.copy()
        valid_border_types.remove("BORDER_WRAP")
        valid_border_types.remove("BORDER_TRANSPARENT")
        self.border_type = RadioSelect(valid_border_types, "BORDER_DEFAULT")

    def apply(self, img):
        if self.active:
            parsed_kw = self.kernel_width.value
            parsed_kh = self.kernel_height.value
            if self.kernel_width.value != 0 and self.kernel_width.value % 2 == 0:
                parsed_kw += 1
            if self.kernel_height.value != 0 and self.kernel_height.value % 2 == 0:
                parsed_kh += 1
            return cv2.GaussianBlur(img, (parsed_kw, parsed_kh), self.sigma_x.value, self.sigma_y.value, getattr(cv2, self.border_type.value))
        else:
            return img


class FilterErode(Filter):

    name = "Erode"
    params = {
        "active": "Boolean", 
        "kernel_type": "RadioSelect", 
        "kernel_width": "BoundedInteger", 
        "kernel_height": "BoundedInteger", 
        "iterations": "BoundedInteger", 
        "border_type": "RadioSelect"
        }

    def __init__(self):
        super().__init__()
        self.kernel_type = RadioSelect(MorphShapes)
        self.kernel_width = BoundedInteger(3, 1, 255)
        self.kernel_height = BoundedInteger(3, 1, 255)
        self.iterations = BoundedInteger(1, 1, 255)
        valid_border_types = BorderTypes.copy()
        valid_border_types.remove("BORDER_WRAP")
        self.border_type = RadioSelect(valid_border_types, "BORDER_CONSTANT")

    def apply(self, img):
        if self.active:
            kernel = cv2.getStructuringElement(
                getattr(cv2, self.kernel_type.value), 
                (self.kernel_width.value, self.kernel_height.value)
            )
            return cv2.erode(img, kernel, 
                iterations=self.iterations.value, 
                borderType=getattr(cv2, self.border_type.value)
            )
        else:
            return img


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
                borderType=getattr(cv2, self.border_type.value)
            )
        else:
            return img


class FilterMorphologyEx(FilterErode):

    name = "Morphological Transformation"
    params = FilterErode.params.copy()
    params["operation"] = "RadioSelect"

    def __init__(self):
        super().__init__()
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
                borderType=getattr(cv2, self.border_type.value)
            )
        else:
            return img


class WarpRotate(Filter):

    name = "Rotate"
    params = {"active": "Boolean", "theta": "BoundedDouble"}

    def __init__(self):
        super().__init__()
        self.theta = BoundedDouble(0, -360, 360)

    def apply(self, img):
        if self.active:
            rows, cols, channels = img.shape
            mat = cv2.getRotationMatrix2D(((cols-1)/2.0, (rows-1)/2.0), self.theta.value, 1)
            return cv2.warpAffine(img, mat, (cols,rows))
        else:
            return img


class WarpAffine(Filter):

    name = "Affine"
    params = {
        "active": "Boolean", 
        "M11": "BoundedDouble", 
        "M12": "BoundedDouble", 
        "M13": "BoundedDouble", 
        "M21": "BoundedDouble", 
        "M22": "BoundedDouble", 
        "M23": "BoundedDouble", 
        "flags": "RadioSelect",
        "border_mode": "RadioSelect"
        }

    def __init__(self):
        super().__init__()
        self.M11 = BoundedDouble(1, -10, 10)
        self.M12 = BoundedDouble(0, -10, 10)
        self.M13 = BoundedDouble(0, -10, 10)
        self.M21 = BoundedDouble(0, -10, 10)
        self.M22 = BoundedDouble(1, -10, 10)
        self.M23 = BoundedDouble(0, -10, 10)
        self.flags = RadioSelect(InterpolationFlags, "INTER_LINEAR")
        self.border_mode = RadioSelect(BorderTypes, "BORDER_CONSTANT")

    def apply(self, img):
        if self.active:
            rows, cols, channels = img.shape
            mat = np.float32([[self.M11.value, self.M12.value, self.M13.value], [self.M21.value, self.M22.value, self.M23.value]])
            return cv2.warpAffine(img, mat, (cols, rows), 
                getattr(cv2, self.flags.value), 
                getattr(cv2, self.border_mode.value)
            )
        else:
            return img

class WarpPerspective(Filter):

    name = "Perspective"
    params = {
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
        "border_mode": "RadioSelect"
        }

    def __init__(self):
        super().__init__()
        self.M11 = BoundedDouble(1, -10, 10)
        self.M12 = BoundedDouble(0, -10, 10)
        self.M13 = BoundedDouble(0, -10, 10)
        self.M21 = BoundedDouble(0, -10, 10)
        self.M22 = BoundedDouble(1, -10, 10)
        self.M23 = BoundedDouble(0, -10, 10)
        self.M31 = BoundedDouble(0, -10, 10)
        self.M32 = BoundedDouble(0, -10, 10)
        self.M33 = BoundedDouble(1, -10, 10)
        self.flags = RadioSelect(InterpolationFlags, "INTER_LINEAR")
        self.border_mode = RadioSelect(BorderTypes, "BORDER_CONSTANT")
        self.border_value = BoundedInteger(0, 0, 255)

    def apply(self, img):
        if self.active:
            rows, cols, channels = img.shape
            mat = np.float32([
                [self.M11.value, self.M12.value, self.M13.value], 
                [self.M21.value, self.M22.value, self.M23.value], 
                [self.M31.value, self.M32.value, self.M33.value]
            ])
            return cv2.warpPerspective(img, mat, (cols, rows), 
                getattr(cv2, self.flags.value), 
                getattr(cv2, self.border_mode.value)
            )
        else:
            return img

class WarpPolar(Filter):

    name = "Warp Polar"
    params = {"active": "Boolean", "max_radius": "BoundedInteger", "flags": "RadioSelect", "POLAR_LOG": "Boolean", "INVERSE_MAP": "Boolean"}

    def __init__(self):
        super().__init__()
        self.max_radius = BoundedInteger(1, 0, 4096)
        valid_flags = InterpolationFlags.copy()
        valid_flags.remove("INTER_NEAREST_EXACT")
        valid_flags.remove("INTER_MAX")
        self.flags = RadioSelect(valid_flags)
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
            return cv2.warpPolar(img, (cols, rows), ((cols-1)/2.0, (rows-1)/2.0), self.max_radius.value, getattr(cv2, flag))
        else:
            return img


class FilterConvolvePresets(Filter):

    name = "Convolve Presets"
    params = {"active": "Boolean", "preset": "RadioSelect"}

    def __init__(self):
        super().__init__()
        self.preset = RadioSelect(["SHARPEN", "EDGE_DETECT", "EMBOSS", "SOBEL"])
        valid_border_types = BorderTypes.copy()
        valid_border_types.remove("BORDER_WRAP")
        self.border_type = RadioSelect(valid_border_types, "BORDER_DEFAULT")

    def apply(self, img):
        if self.active:
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

            return cv2.filter2D(img, -1, kernel, borderType=getattr(cv2, self.border_type.value))
        else:
            return img


class FilterConvolve(Filter):

    name = "Convolve"
    params = {
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
        super().__init__()
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
        valid_border_types = BorderTypes.copy()
        valid_border_types.remove("BORDER_WRAP")
        valid_border_types.remove("BORDER_TRANSPARENT")
        self.border_type = RadioSelect(valid_border_types, "BORDER_DEFAULT")

    def apply(self, img):
        if self.active:
            kernel = np.float32([[self.M11.value, self.M12.value, self.M13.value], [self.M21.value, self.M22.value, self.M23.value], [self.M31.value, self.M32.value, self.M33.value]])
            return cv2.filter2D(img, -1, kernel, anchor=(self.anchor_x.value, self.anchor_y.value), delta=self.delta.value, borderType=getattr(cv2, self.border_type.value))
        else:
            return img


filter_classes = [
    FilterInvert, 
    FilterSplitChannel,
    FilterGammaCorrect,
    FilterThreshold,
    FilterThresholdToZero,
    FilterThresholdAdaptive,
    FilterThresholdOtsuGauss,
    FilterBoxBlur,
    FilterMedianBlur,
    FilterGaussianBlur,
    FilterErode,
    FilterDilate,
    FilterMorphologyEx,
    WarpRotate,
    WarpAffine,
    WarpPerspective,
    WarpPolar,
    FilterConvolvePresets,
    FilterConvolve,
]