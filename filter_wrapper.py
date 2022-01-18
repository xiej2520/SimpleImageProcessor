from filters import Filters

class Filter_Wrapper():

    def __init__(self, name, args):
        self.name = name
        self.args = args
    
    def apply(self, img):
        if (self.name == "INVERT"):
            return Filters.invert(img)
        elif (self.name == "SPLIT_CHANNEL"):
            return Filters.split_channel(img, self.args[0])
        elif (self.name == "THRESHOLD"):
            return Filters.threshold(img, self.args[0])
        elif (self.name == "THRESHOLD_TO_ZERO"):
            return Filters.threshold_tozero(img, self.args[0])
        elif (self.name == "THRESHOLD_ADAPTIVE"):
            return Filters.adaptive_threshold(img)
        elif (self.name == "THRESHOLD_OTSU_GAUSS"):
            return Filters.threshold_otsu_gaussian(img)
        elif (self.name == "GAMMA_CORRECT"):
            return Filters.gamma_correct(img, self.args[0])
        elif (self.name == "BOX_BLUR"):
            return Filters.box_blur(img, self.args[0])
        elif (self.name == "MEDIAN_BLUR"):
            return Filters.median_blur(img, self.args[0])
        elif (self.name == "GAUSSIAN_BLUR"):
            return Filters.gaussian_blur(img, self.args[0])
        elif (self.name == "EROSION"):
            return Filters.erosion(img, self.args[0])
        elif (self.name == "DILATION"):
            return Filters.dilation(img, self.args[0])
        elif (self.name == "OPENING"):
            return Filters.opening(img, self.args[0])
        elif (self.name == "CLOSING"):
            return Filters.closing(img, self.args[0])
        elif (self.name == "GRADIENT"):
            return Filters.gradient(img, self.args[0])
        elif (self.name == "ROTATE"):
            return Filters.rotate(img, self.args[0])
        elif (self.name == "AFFINE"):
            return Filters.affine(img, self.args[0])
        elif (self.name == "PERSPECTIVE"):
            return Filters.perspective(img, self.args[0])
        elif (self.name == "SHARPEN"):
            return Filters.sharpen(img)
        elif (self.name == "EDGE_DETECT"):
            return Filters.edge_detect(img)
        elif (self.name == "EMBOSS"):
            return Filters.emboss(img)
        elif (self.name == "SOBEL"):
            return Filters.sobel(img)
        elif (self.name == "CONVOLVE"):
            return Filters.convolve(img, self.args[0])
