import os
import sys
import numpy as np
import pickle
import pdb
import gc
import cv2

def load_data(filepath):
    result = []
    num = 0
    fin = open(filepath,'r')
    for line in fin:
        strdata = line.strip().split(' ')
        fltdata = [float(k) for k in strdata]
        result.extend(fltdata)
        num += 1
    fin.close()
    data = np.array(result)
    del result
    gc.collect()
    data.shape = (num,-1)
    return data

def train(imgpath, featpath, outpath):
    imgdata = load_data(imgpath)
    featdata = load_data(featpath)
    featdims = featdata.shape[1]
    imgdims = imgdata.shape[1]
    data = np.hstack((imgdata, featdata))
    del imgdata
    del featdata
#    gc.collect()
    m = np.mean(data, 0)
    data = data - np.tile(m,(data.shape[0],1))
    cov = data.T.dot(data)
    del data
    gc.collect()
    covxf = cov[imgdims:,0:imgdims]
#    pdb.set_trace()
    print cov.shape
    cov = cov + 0.0001 * np.eye(cov.shape[0])
    mcov = np.mat(cov)
    del cov
    gc.collect()
    covinv = mcov.I
    print "inv is done!"
    del mcov
    gc.collect()
    covinv = np.array(covinv)
    covinvff = covinv[imgdims:, imgdims:]
    del covinv
    gc.collect()
    fout = open(outpath, 'w')
    mx = m[0:imgdims]
    mf = m[imgdims:]
    result = {"mx":mx, "mf":mf, "covxf":covxf, "covinvff":covinvff}
    del mx
    del mf
    del covxf
    del covinvff
    gc.collect()
    pickle.dump(result,fout)
    fout.close()


def test(imgpath, featpath, modelpath, outdir):
    feats = load_data(featpath)
    imgs = load_data(imgpath)
    fin = open(modelpath, 'r')
    model = pickle.load(fin)
    fin.close()
#    w = 128
#    h = 64

    w = 64
    h = 32
    print "load done!"
    for k in range(feats.shape[0]):
        #print str(k) + "/" + str(feats.shape[0])
        sys.stdout.write('.')
        if 0 == (k+1)%50:
            print str(k) + "/" + str(feats.shape[0])
        onefeat = feats[k,:]
        oneimg = imgs[k,:]
        #pdb.set_trace()
        t = onefeat - model['mf']
        t = model['covinvff'].dot(t)
        t = t.dot(model['covxf'])
        t = t + model['mx']
        t.shape = (h,w)
        m0 = t.min()
        m1 = t.max()
        img = np.zeros((h,w), dtype=np.uint8)
        for y in range(h):
            for x in range(w):
                v = t[y,x]
                v = (v - m0) * 255 / (m1 - m0)
                v = np.minimum(v, 255)
                v = np.maximum(v,  0)
                img[y,x] = v 
        filepath = outdir + str(k) + '_rebuild.jpg'
        cv2.imwrite(filepath, img)
        
        oneimg.shape = (h,w)
        for y in range(h):
            for x in range(w):
                v = oneimg[y,x]
                v = np.minimum(v, 255)
                v = np.maximum(v,  0)
                img[y,x] = v 
        filepath = outdir + str(k) + '_src.jpg'
        cv2.imwrite(filepath, img)
    print " "
        
 
if __name__ == "__main__":
    localdir = os.path.abspath('.') + '/'
    if len(sys.argv) == 2:
        if 0 == cmp(sys.argv[1], "-train"): 
            train(localdir+"train-img.txt", localdir+"train-feat.txt", localdir+"invfeat.model")
        elif 0 == cmp(sys.argv[1], "-test"):
            test(localdir+"test-img.txt", localdir+"test-feat.txt",localdir+"invfeat.model", localdir+"out/")
    else:
        print "-train or -test?"
