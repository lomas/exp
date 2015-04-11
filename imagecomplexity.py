import os
import cv2
import numpy as np
import sys
import pdb


#image complexity measure by GLCM


def calc_glcm(gray,levelnum,dx,dy):
    glcm = np.zeros((levelnum, levelnum))
    h,w = gray.shape
    for y in range(h):
        if y + dy < 0 or y + dy >= h:
            continue;
        for x in range(w):
            if x + dx < 0 or x + dx >= w:
                continue
            a = gray[y,x]
            b = gray[y+dy,x+dx]
            glcm[a,b] = glcm[a,b] + 1
    glcm = glcm / glcm.sum()
    return(glcm)

def setgraylevel(gray, levelnum):
    m0 = gray.min()
    m1 = gray.max() #normalized by [m0,m1] not [0,255]
    rate = 1.0 * (levelnum - 1) / (m1 - m0)
    newgray = np.int64((gray * 1.0 - m0) * rate)
    return(newgray)


#angular second moment
def calc_energy(glcm):
    tmp = glcm * glcm;
    return(np.sum(tmp))    

def calc_diff(glcm):
    h,w = glcm.shape
    result = 0
    for y in range(h):
        for x in range(w):
            result = result + (x - y) * (x - y) * glcm[y,x]
    return(result)

def calc_entropy(glcm):
    h,w = glcm.shape
    idx = glcm < 0.00000001
    glcm[idx] = 1
    log = np.log2(glcm)
    glcm[idx] = 0
    for y in range(h):
        for x in range(w):
            if str(log[y,x]) == "-inf":
                log[y,x] = 0
    result = np.sum(glcm * log * (-1))
    return(result) 

#inverse differential moment
def calc_idm(glcm):
    h,w = glcm.shape
    result = 0
    for y in range(h):
        for x in range(w):
            result = result + glcm[y,x] / (1 + (x - y) * (x - y))
    return(result) 

#along x or y to calculate the feature    
def calc_correlation(glcm):
    h,w = glcm.shape
#    pdb.set_trace()
    px = np.sum(glcm,0)
    mx = np.sum(px * np.array(range(w)))
    vx = (np.array(range(w)) - mx)
    vx = np.sum(vx * vx * px)
    result = 0
    for y in range(h):
        for x in range(w):
             result = result + (y + 1) * (x + 1) * glcm[y,x]    
    result = (result - mx * mx) / (vx * vx)
    return(result)
    
def calc_edgerate(gray):
    gx = cv2.Sobel(gray, cv2.CV_32F, 1,0)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0,1)
    grad = np.abs(gx) + np.abs(gy)
    t = 20
    num = np.sum(grad > t)
    h,w = gray.shape
    result = num * 1.0 / (h * w)
    return(result) 
   

def complexity_measure(filepath, dx, dy):
    levelnum = 8
    measure = np.zeros((1,5)) #entroy, edgerate, diff, correlation, energy
    weight = np.array([1,1,1,-1,-1])
    img = cv2.imread(filepath,0)
    if img.size:
        gray = setgraylevel(img, levelnum)
        glcm = calc_glcm(gray,levelnum, dx,dy)
        measure[0,0] = calc_entropy(glcm)   
        measure[0,1] = calc_edgerate(img)
        measure[0,2] = calc_diff(glcm)
        measure[0,3] = calc_correlation(glcm)
        measure[0,4] = calc_energy(glcm)
    measure = measure * weight
    result = np.sum(measure)
    return((measure, result)) 


if __name__=="__main__":
    measure, result = complexity_measure('d:\\tmp\\t.jpg', 1, 4) 
    print measure
    print result 
 
  
