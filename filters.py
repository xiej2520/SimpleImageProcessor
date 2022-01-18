import cv2
import numpy as np

class Filters():

    @staticmethod
    def invert(img):
        return cv2.bitwise_not(img)

    @staticmethod
    def split_channel(img, x):
        zero = np.zeros_like(img[:,:,0])
        if x < 86:
            return np.dstack((zero, zero, img[:,:,2]))
        elif x < 172:
            return np.dstack((zero, img[:,:,1], zero))
        else:
            return np.dstack((img[:,:,0], zero, zero))


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
        filtered_img = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, 2) # block size, constant
        return cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)


    @staticmethod
    def threshold_otsu_gaussian(img):
        # Otsu's thresholding after Gaussian filtering
        img_blur = cv2.GaussianBlur(img, (5,5),0)
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        filtered_img = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        return cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)


    @staticmethod
    def box_blur(img, ksize):
        if ksize == 0:
            ksize += 1
        return cv2.blur(img, (ksize, ksize))


    @staticmethod
    def median_blur(img, ksize):
        if ksize % 2 == 0:
            ksize += 1
        return cv2.medianBlur(img, ksize)


    @staticmethod
    def gaussian_blur(img, ksize):
        if ksize % 2 == 0:
            ksize += 1
        return cv2.GaussianBlur(img, (ksize, ksize), 0)


    @staticmethod
    def erosion(img, iterations):
        kernel = np.ones((5,5), np.uint8)
        return cv2.erode(img, kernel, iterations=iterations)


    @staticmethod
    def dilation(img, iterations):
        kernel = np.ones((5,5), np.uint8)
        return cv2.dilate(img, kernel, iterations=iterations)


    def opening(img, iterations):
        kernel = np.ones((5,5), np.uint8)
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel, iterations=iterations)


    def closing(img, iterations):
        kernel = np.ones((5,5), np.uint8)
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel, iterations=iterations)


    def gradient(img, iterations):
        kernel = np.ones((5,5), np.uint8)
        return cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel, iterations=iterations)


    def rotate(img, theta):
        rows, cols, channels = img.shape
        # cols-1 and rows-1 are the coordinate limits.
        mat = cv2.getRotationMatrix2D(((cols-1)/2.0, (rows-1)/2.0), theta, 1)
        return cv2.warpAffine(img, mat, (cols,rows))


    def affine(img, x):
        rows, cols, ch = img.shape
        # points in original image
        pts1 = np.float32([[50,50],[200,50],[50,200]])
        # points in affine transform
        pts2 = np.float32([[10,100],[200,x],[100,250]])
        mat = cv2.getAffineTransform(pts1,pts2)
        return cv2.warpAffine(img, mat, (cols,rows))


    def perspective(img, x):
        rows, cols, ch = img.shape
        # points in original image, 3 noncolinear
        pts1 = np.float32([[56,65],[368,x],[28,387],[389,390]])
        pts2 = np.float32([[0,0],[300,0],[0,300],[300,300]])
        mat = cv2.getPerspectiveTransform(pts1,pts2)
        return  cv2.warpPerspective(img, mat, (cols,rows))


    def sharpen(img):
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
            ])
        return cv2.filter2D(img, -1, kernel)


    def edge_detect(img):
        kernel = np.array([
            [-1, -1, -1],
            [-1, 8, -1],
            [-1, -1, -1]
            ])
        return cv2.filter2D(img, -1, kernel)


    def emboss(img):
        kernel = np.array([
        [-2, -1, 0],
        [-1, 1, 1],
        [0, 1, 2]
        ])
        return cv2.filter2D(img, -1, kernel)


    def sobel(img):
        kernel = np.array([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
        ])
        return cv2.filter2D(img, -1, kernel)

    def convolve(img, x):
        kernel = np.array([
            [0, x, 0],
            [x, -4*x, x],
            [0, x, 0]
        ])
        return cv2.filter2D(img, -1, kernel)