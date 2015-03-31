import cv2
import numpy as np
import sys
import os

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
                x0 = np.int64(w/4)
                x1 = np.int64(w*3/4)
                y0 = np.int64(h/4)
                y1 = np.int64(h*3/4)
                img = img[y0:y1, x0:x1]
                img = np.float32(img)
#color moment
                m0 = np.sum(img) / img.size
                h,w = img.shape
                m1 = 0
                m2 = 0
                for y in range(h):
                    for x in range(w):
                        v = img[y,x] - m0
                        m1 = m1 + v * v
                        m2 = m2 + v * v * v
                m1 = m1 / img.size
                m2 = m2 / img.size
                m1 = np.sqrt(m1)
           
                flag = 1     
                if m2 < 0:
                    flag = -1
                m2 = flag * m2
                m2 = np.power(m2,0.33333)
                m2 = flag * m2
                print("extract: %s" %filename)
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

if __name__ == "__main__":
    main_entry("d:\\tmp\\pos\\")
