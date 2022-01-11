from filters import Filters

class Filter_Wrapper():

    def __init__(self, name, args):
        self.name = name
        self.args = args
    
    def apply(self, img):
        if (self.name == "THRESHOLD"):
            return Filters.threshold(img, self.args[0])
        elif (self.name == "THRESHOLD_TO_ZERO"):
            return Filters.threshold_tozero(img, self.args[0])
        elif (self.name == "THRESHOLD_ADAPTIVE"):
            return Filters.adaptive_threshold(img)
        elif (self.name == "THRESHOLD_OTSU_GAUSS"):
            return Filters.threshold_otsu_gaussian(img)
        elif (self.name == "GAMMA_CORRECT"):
            return Filters.gamma_correct(img, self.args[0])

