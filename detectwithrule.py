import os
import sys
import cv2
import numpy as np
import sklearn.cluster as skcluster
from sklearn.externals import joblib
import pdb
import pickle 
import create_transaction

def loadmodel(cluster_dir, rulepath):
    clustertree = joblib.load(cluster_dir)
    fin = open(rulepath, 'r')
    rules = pickle.load(fin)
    fin.close()   
    return clustertree, rules
    
if __name__ == "__main__":
    inimg = sys.argv[1]
    K = int(sys.argv[2])
    thresh = float(sys.argv[3])
    clustermodelpath = sys.argv[4]
    rulefile = sys.argv[5]
    outimg = sys.argv[6]
    clustertree, rules = loadmodel(clustermodelpath, rulefile)
    siftdetect = cv2.SIFT()
    img = cv2.imread(inimg, 0)
    if img is None:
        print "error: null image !!!!!!!!!"
    kp = siftdetect.detect(img)
    kp,des = siftdetect.compute(img, kp)
    data = np.zeros((len(kp),6))
    for idxkp in range(len(kp)):
        f = -1
        x,y = kp[idxkp].pt
        scale = kp[idxkp].size
        angle = kp[idxkp].angle
        data[idxkp,0] = f
        data[idxkp,1] = x
        data[idxkp,2] = y
        data[idxkp,3] = scale
        data[idxkp,4] = angle
        feat = des[idxkp, :]
        data[idxkp,5] = clustertree.predict(feat)
    trans = create_transaction.create_transaction(data, K)
    colorimg = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
    print("# of kp: %d, # of trans: %d" %(len(kp), len(trans)))
    num1 = 0
    num2 = 0
    score = 0
   # pdb.set_trace()
    for idx in range(len(trans)):
        key = trans[idx][0:-1]
        key = tuple(key)
        if key in rules.keys():
            nneg = rules[key][0]
            npos = rules[key][1]
            num1 = num1 + 1
            s = npos * 1.0 / (npos + nneg)
            if s > score:
                score = s
            x,y = kp[idx].pt
            radius = int(kp[idx].size)
            if radius < 2:
                radius = 2
            x = np.int32(x)
            y = np.int32(y)
            if s > thresh:
                num2 = num2 + 1
                red = int(150 + s * 100)
                cv2.circle(colorimg, (x,y), radius, (0,0,red),2)
            else:
                cv2.circle(colorimg, (x,y), radius, (0,255,0),2)

    cv2.imwrite(outimg, colorimg)
    print("# of key: %d, max score = %f, # of pos key = %d" %(num1,score, num2))

