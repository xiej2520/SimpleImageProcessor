import cv2
import numpy as np


def gamma_correct(img, gamma):
    outImg = np.zeros(img.shape, img.dtype)

    # lookup table
    LUT = []

    for i in range(256):
        LUT.append(((i / 255.0) ** (1 / gamma)) * 255)

    LUT = np.array(LUT,dtype=np.uint8)
    outImg = LUT[img]

    return outImg


def threshold(img, threshold):
	return cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)[1]
    

def threshold_tozero(img, threshold):
	return cv2.threshold(img, threshold, 255, cv2.THRESH_TOZERO)[1]

def adaptive_threshold(img, threshold):
    return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2) # block size, constant

def threshold_otsu_gaussian(img):
    # Otsu's thresholding after Gaussian filtering
    blur = cv2.GaussianBlur(img, (5,5),0)
    return cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]