import cv2
import os
import sys
import numpy as np

def entry(gray):
    siftfeat = cv2.SIFT()
    kp = siftfeat.detect(img)
    kp,des = siftfeat.compute(img,kp)
    return(kp, des)

if __name__ == "__main__":
    img = cv2.imread('d:\\tmp\\motor.jpg',0)
    color = cv2.cvtColor(img, cv2.cv.CV_GRAY2BGR)
    kp,des = entry(img)
    for idx in range(len(kp)):
        x,y = kp[idx].pt
        size = kp[idx].size
        angle = kp[idx].angle
        print str(idx) + " pt[" + str(x) + "," + str(y) + "]," + str(size) + "," + str(angle)
        x = np.int32(x)
        y = np.int32(y)
        cv2.circle(color, (x,y), 3, (255,0,0))
    cv2.imwrite('d:\\tmp\\result.jpg', color)
