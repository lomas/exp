import cv2
import numpy as np
import sys
import os


def extract_moment(img):
    img = np.float32(img)
    m0 = np.sum(img) / img.size
    h,w = img.shape
    offset = [m0 for i in range(h*w)]
    offset = np.array(offset)
    offset.shape = (h,w)
    img = img - offset
    img2 = img * img
    m1 = np.sum(img2) / img.size
    m1 = np.sqrt(m1)
    img3 = img2 * img
    m2 = np.sum(img3) / img.size
    if m2 < 0:
        m2 = -m2 
    m2 = np.power(m2,  0.33333)
    return((m0,m1,m2))       

def extract_color_info(img_dir):
    info = []
    path_list = []
    for root,subdir,files in os.walk(img_dir):
        for filename in files:
            shortname,ext = os.path.splitext(filename)
            if cmp(ext, '.jpg') == 0:
                filepath = os.path.join(img_dir,filename)
                img = cv2.imread(filepath,0)
                h,w = img.shape
#crop image
                x0 = np.int64(w*0.3)
                x1 = np.int64(w*0.7)
                y0 = np.int64(h * 0.4)
                y1 = np.int64(h * 0.6)

                img = img[y0:y1, x0:x1]
                img = np.float32(img)
#texture
                dx = cv2.Sobel(img, cv2.CV_32F, 1,0)
                dy = cv2.Sobel(img, cv2.CV_32F, 0,1)
#                dx = np.absolute(dx)
#                dy = np.absolute(dy)
                img = (dx+dy)/2
#color moment
                m0,m1,m2 = extract_moment(img)
                print("extract: %s (%.2f %.2f %.2f)" %(filename,m0,m1,m2))
                if not info:
                    info = [m0,m1,m2]
                    path_list = [filepath]
                else:
                    info.append(m0)
                    info.append(m1)
                    info.append(m2)
                    path_list.append(filepath)
    if info:
        info = np.array(info)
        info = info.reshape((-1,3))
        info = np.float32(info)
    return((path_list, info))

def main_entry(img_dir):
    path_list, image_info = extract_color_info(img_dir)
    term_crit = (cv2.TERM_CRITERIA_EPS,30,0.1)
    ret,bestLabel,centers = cv2.kmeans(image_info, 2, term_crit, 10, 0)
    for idx in range(image_info.shape[0]):
        img = cv2.imread(path_list[idx],0)
        filepath = "d:\\tmp\\colorcluster\\%d_%d.jpg" %(idx,bestLabel[idx])
        cv2.imwrite(filepath, img)
    print centers
if __name__ == "__main__":
    main_entry("d:\\tmp\\pos\\")
