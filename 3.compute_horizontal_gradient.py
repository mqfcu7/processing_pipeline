import cv2
import os
import numpy as np

def compute_horizontal_gradient(img):
    rows, columns, channels = img.shape
    gradient = img[0:rows, 0:columns - 1]
    img_shift = img.copy()
    img_shift[1:rows, 0:columns - 1] = img[0:rows - 1, 1:columns]
    gradient = np.absolute(np.subtract(img_shift, img))
    return gradient
    
    img_shift = img.copy()
    img_shift[0:rows, 0:columns - 1] = img[0:rows, 1:columns]
    gradient = np.maximum(
        gradient, np.absolute(np.subtract(img_shift, img)))
    
    img_shift = img.copy()
    img_shift[0:rows - 1, 0:columns - 1] = img[1:rows, 1:columns]
    gradient = np.maximum(
        gradient, np.absolute(np.subtract(img_shift, img)))
    gradient = np.maximum(255, np.minimum(0, gradient)).astype(np.uint8)
    return gradient

def main():
    src_dir = 'detect_car_roi'
    dst_dir = 'compute_horizontal_gradient'

    files = os.listdir(src_dir)
    for f in files:
        img = cv2.imread(os.path.join(src_dir, f))
        gradient = compute_horizontal_gradient(img)
        cv2.imwrite(os.path.join(dst_dir, f), gradient)

if __name__ == '__main__':
    main()
