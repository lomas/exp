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
    outimg = sys.argv[2]
    K = 512
    clustertree, rules = loadmodel('models/model.pkl', 'rules.txt')
    siftdetect = cv2.SIFT()
    img = cv2.imread(inimg, 0)
    if img is None:
        print "null image"
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
    num = 0
    score = 0
    pdb.set_trace()
    for idx in range(len(trans)):
        key = trans[idx][0:-1]
        key = tuple(key)
        if key in rules.keys():
            nneg = rules[key][0]
            npos = rules[key][1]
            num = num + 1
            s = npos * 1.0 / (npos + nneg)
            if s > score:
                score = s
            if s > 0.7:
                x,y = kp[idx].pt
                x = np.int32(x)
                y = np.int32(y)
                cv2.circle(colorimg, (x,y), 3, (0,0,255))
    cv2.imwrite(outimg, colorimg)
    print("# of key: %d, max score = %f" %(num,score))

