import sys
import os
import cv2

def main(imgdir, imgpath, featpath):
    imgfile = open(imgpath, 'w')
    featfile = open(featpath, 'w')
    for root, rdirs, names in os.walk(imgdir):
        for name in names:
            shortname,ext = os.path.splitext(name)
            if 0 == cmp(ext, '.jpg'):
                print shortname
                fullpath = os.path.join(root, name)
                img = cv2.imread(fullpath, 0)
                img = cv2.resize(img, (64,32))
                dx = cv2.Sobel(img, cv2.CV_32FC1,1,0)
                dy = cv2.Sobel(img, cv2.CV_32FC1,0,1)
                grad = (dx + dy) / 2
                featline = ""
                imgline = ""
                for y in range(img.shape[0]):
                    for x in range(img.shape[1]):
                        i = img[y,x]
                        f = grad[y,x]
                        featline = featline + str(f) + ' '              
                        imgline = imgline + str(i) + ' '      
                imgline = imgline + '\n'
                featline = featline + '\n'
                imgfile.write(imgline)
                featfile.write(featline)    
    imgfile.close()
    featfile.close()
    
    
if __name__ == "__main__":
    main('img/', 'i.txt', 'f.txt') 
