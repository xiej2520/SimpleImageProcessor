# Simple Image Processor
Simple image processor program that allows the user to apply multiple filters to an image sequentially, and edit them on the fly. 
The program contains many basic filters provided by OpenCV, packaged in a plain GUI interface for the user to try.


## Tools used
* Python 3.8.12
* PyQt
* opencv-python

# Installing
1. Clone the repo
```sh
git clone https://github.com/xiej2520/SimpleImageProcessor.git
```
2. Install necessary python libraries if needed:

        pip install pyqt5
        pip install numpy
        pip install opencv-python

# Demo
### Gamma correction and thresholding to improve scan legibility
![thresh_demo](https://user-images.githubusercontent.com/16630834/151078551-083901d6-1b90-414a-93db-2e6659319aa1.gif)
### Morphological gradient
![morph_demo](https://user-images.githubusercontent.com/16630834/151078944-5d9ea7a0-5ab2-438e-9914-a9e621ef4ced.gif)

# Todo:
* General code refactor and cleanup.
* Better copy/paste functionality
* Increase processing speed of filters, cache image at user edit.
* New widgets for editing matrix-type arguments for filters.

###
![gaussblur+extremeoutline png](https://user-images.githubusercontent.com/16630834/151079028-2375f59f-3d82-402b-98f1-cbf0eb3714be.png)
Gaussian blur and extreme outline convolution (zoom in!)
