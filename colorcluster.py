import cv2
import numpy as np
import sys
import os
import pdb

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

#gray moment
                m0,m1,m2 = extract_moment(img)


                img = np.float32(img)
#texture
                dx = cv2.Sobel(img, cv2.CV_32F, 1,0)
                dy = cv2.Sobel(img, cv2.CV_32F, 0,1)
#                dx = np.absolute(dx)
#                dy = np.absolute(dy)
                img = (dx+dy)/2
#color moment
                m3,m4,m5 = extract_moment(img)
                print("extract: %s (%.2f %.2f %.2f %.2f %.2f %.2f)\n" %(filename, m0, m1,m2,m3,m4,m5))
                if not info:
                    info = [m0,m1,m2,m3,m4,m5]
                    path_list = [filepath]
                else:
                    info.extend([m0,m1,m2,m3,m4,m5])
                    path_list.append(filepath)
    if info:
        info = np.array(info)
        info = info.reshape((-1,6))
        info = np.float32(info)
    return((path_list, info))


def knn(image_info, centers, centers_weight):
    nei = 2
    PrPos = np.zeros((image_info.shape[0], 1))
    for idx in range(image_info.shape[0]):
        info = image_info[idx,:]
        info = np.tile(info, (centers.shape[0], 1))
        dist = (info - centers) * (info - centers)
        dist = np.sum(dist, 1)
        sortidx = np.argsort(dist)
        dist = dist[sortidx[0:nei]]
        dist = 1 - dist / np.sum(dist)
        w = centers_weight[sortidx[0:nei]]
        #pdb.set_trace()
        PrPos[idx] = np.sum(w * dist) / np.sum(dist)
    return(PrPos) 


def calc_hitrate(cluster_pos, kmeanlabel, reallabel):

    testlabel = np.zeros(reallabel.shape)
    for idx in range(cluster_pos.size):
        if cluster_pos[idx] > 0.5:
            j = (kmeanlabel == idx)
            testlabel[j] = 1


    testlabel = np.int32(testlabel)
    reallabel = np.int32(reallabel)
    hitrate = np.sum(testlabel == reallabel) / np.float64(reallabel.size)
    return((testlabel, hitrate))


def classify_it(kmeanlabel, cluster_num, posneg):
    cluster_pos = np.zeros((cluster_num, 1))
    cluster_size = np.zeros((cluster_num, 1))
    for idx in range(kmeanlabel.size):
        kl = kmeanlabel[idx,0]
        cluster_size[kl,0] = cluster_size[kl, 0] + 1
        cluster_pos[kl, 0] = cluster_pos[kl, 0] + posneg[idx]
    cluster_pos = cluster_pos / cluster_size 


    testlabel, hitrate = calc_hitrate(cluster_pos, kmeanlabel, posneg)
    return((cluster_pos, testlabel, hitrate))

def normalize(data):
    for k in range(data.shape[1]):
        v = data[:,k]
        m0 = v.min()
        m1 = v.max()
    #    pdb.set_trace()
        v = (v - m0) / (m1 - m0)
        data[:,k] = v
    return(data)

def main_entry(pos_dir, neg_dir):
    pos_path_list, pos_info = extract_color_info(pos_dir)
    neg_path_list, neg_info = extract_color_info(neg_dir)



    cluster_num = 200
    term_crit = (cv2.TERM_CRITERIA_EPS,30,0.1)
    posflag = [1 for k in range(pos_info.shape[0])]
    negflag = [0 for k in range(neg_info.shape[0])]
    posflag.extend(negflag)
    posneg = np.array(posflag)
    posneg.shape = (posneg.size, 1)
    image_info = np.vstack((pos_info, neg_info))
    pos_path_list.extend(neg_path_list)
    path_list = pos_path_list

    #image_info = normalize(image_info)

    ret,kmeanlabel0,centers0 = cv2.kmeans(image_info[:,0:3], cluster_num, term_crit, 10, 0)
#    pdb.set_trace()
    posrate0, label0, hitrate0 = classify_it(kmeanlabel0, cluster_num, posneg)


    ret,kmeanlabel1,centers1 = cv2.kmeans(image_info[:,3:6], cluster_num, term_crit, 10, 0)
    posrate1, label1, hitrate1 = classify_it(kmeanlabel1, cluster_num, posneg)

   
    hitrate2 = 0 
    for k in range(posneg.size):
        l0 = kmeanlabel0[k,0]
        l1 = kmeanlabel1[k,0]
        w = (posrate0[l0,0] + posrate1[l1,0])/2
        if w > 0.5:
            l = 1
        else:
            l = 0
        if np.int64(l) == np.int64(posneg[k,0]):
            hitrate2 = hitrate2 + 1
    hitrate2 = hitrate2 / np.float64(posneg.size)
        

    if 1:
        try:
            f = open('d:\\tmp\\centers.txt','w')
            for row in range(centers1.shape[0]):
                s = "%ff, %ff, %ff, %ff,\n" %(centers1[row,0], centers1[row,1], centers1[row,2], posrate1[row,0])
                f.write(s)
            f.close()
        except Exception, e:
            print Exception, ":", e


    print hitrate0
    print hitrate1
    print hitrate2


if __name__ == "__main__":
    main_entry("d:\\tmp\\drv\\pos\\", "d:\\tmp\\drv\\neg\\")
