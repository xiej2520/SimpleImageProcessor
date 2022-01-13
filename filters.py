import cv2
import numpy as np

class Filters():
    @staticmethod
    def gamma_correct(img, gamma_in):
        # gamma_in is 0-255
        # transform 0-127 to 0-1, 128-255 to 1-128
        if gamma_in < 128:
            gamma = 1 / (128-gamma_in)
        else:
            gamma = gamma_in-127

        outImg = np.zeros(img.shape, img.dtype)

        # lookup table
        LUT = []

        for i in range(256):
            # transform 0-255 to 0-16
            LUT.append(((i / 255.0) ** (1 / ((gamma+1)/16))) * 255)

        LUT = np.array(LUT,dtype=np.uint8)
        outImg = LUT[img]

        return outImg


    @staticmethod
    def threshold(img, threshold):
        return cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)[1]


    @staticmethod
    def threshold_tozero(img, threshold):
        return cv2.threshold(img, threshold, 255, cv2.THRESH_TOZERO)[1]


    @staticmethod
    def adaptive_threshold(img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        filtered_img = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2) # block size, constant
        return cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)


    @staticmethod
    def threshold_otsu_gaussian(img):
        # Otsu's thresholding after Gaussian filtering
        img_blur = cv2.GaussianBlur(img, (5,5),0)
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        filtered_img = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        return cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)