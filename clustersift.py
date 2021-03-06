import os
import sys
import sklearn.cluster as skcluster
from sklearn.externals import joblib #save/load models
import numpy as np
import pdb
import multiprocessing as mp
import datetime
from multiprocessing import cpu_count
import  gc


def scanfor(indir, extname):
    files = []
    for rdirs, pdirs, names in os.walk(indir):
        for name in names:
            sname,ext = os.path.splitext(name)
            if 0 == cmp(extname, ext):
                fname = os.path.join(indir, name)
                files.append((sname,fname))
    return files

def load_sift(siftfiles,binfo = 1):
    result = []
    attribs = []
#    pdb.set_trace()
    for k in range(len(siftfiles)):
        shortname,fullname = siftfiles[k]
        fin=open(fullname,'r')
        num = 0
        att = []
        for rawline in fin:
            line=rawline.strip().split(' ')
            num = num + 1
            if len(att)  < 1:
                    att = [[line[0], line[1], line[2], line[3], line[4]]]
            else:
                    att.append([line[0], line[1], line[2], line[3], line[4]])
            for idx in range(len(line) - 5):
                     if len(result) < 1:
                         result = [np.float32(line[idx+5])]
                     else:
                         result.append(np.float32(line[idx+5]))
        if len(attribs) < 1:
            attribs = [att]
        else:
            attribs.append(att)
        fin.close()
        if binfo == 1:
            print "load: " + shortname + " " + '%d/%d'%(k+1, len(siftfiles))
    result = np.array(result)
    result.shape = (-1,128)
    print "result " + str(result.shape[0]) + " " + str(result.shape[1]) + "\n"
    return((result,attribs))

def predictNN(model, samples):
    result = []
    centers = model.cluster_centers_
    K = centers.shape[0]
    names = np.array(range(centers.shape[0])) + 1
    for s in range(samples.shape[0]):
        feat = samples[s,:]
        feat = np.tile(feat, (K,1))
        dist = np.mean(np.square(feat - centers),1)
        thresh = dist.min()
        f = dist < thresh * 1.2
        f = list(names[f])
        #pdb.set_trace()
        if len(result) < 1:
            result = [f]
        else:
            result.append(f)
    return result
     
def predict(siftfiles, outdir, modelpath,K):
    samples, attribs = load_sift(siftfiles,0)
    model = joblib.load(modelpath)

    i = 0
    t0 = datetime.datetime.now()
    for idx in range(len(attribs)):
        if 0 == (idx+1) % 20:
            fout = open('cluster_prd_%d.log' %os.getpid(),'a+')
            t1 = datetime.datetime.now()
            t2 = (t1 - t0).seconds / 60.0
            line = '%d %d [%f %f]\n' %(idx+1, len(attribs), t2, t2 * len(attribs) / (idx+1) )
            fout.write(line)
            fout.close()
        fout = open(outdir+siftfiles[idx][0]+".clustersift","w")
        n = len(attribs[idx])
        #labels = model.predict(samples[i:i+n,:])
        labels = predictNN(model, samples[i:i+n, :]) #get all near cluster centers
        i = i + n
        for k in range(n):
            labelnames = ""
#            print labels[k]
            for itm in labels[k]:
                itm = int(itm)
                labelnames = labelnames + str(itm) + ' '
            #pdb.set_trace()
            line = attribs[idx][k][0]+" "+attribs[idx][k][1]+" "+attribs[idx][k][2]+" "+attribs[idx][k][3]+" "+attribs[idx][k][4]+" "+labelnames+ "\n"
            fout.write(line)
        fout.close()
    return

def mt_predict(indir,outdir, modelpath, K): 
    siftfiles = scanfor(indir, '.sift')

    tasknum = cpu_count() - 1
    tasksize = int(len(siftfiles) / tasknum)
    procs = []
    for k in range(tasknum):
        s0 = k * tasksize
        s1 = s0 + tasksize
        if s1 > len(siftfiles) or k + 1 == tasknum:
            s1 = len(siftfiles)
        p = mp.Process(target=predict, args=(siftfiles[s0:s1], outdir, modelpath, K))
        procs.append(p)
        p.start()
    for p in procs:
        p.join()
    #predict(siftfiles, outdir, modelpath, K)
    print "done"
    return


def entry(argv):
    if len(argv) != 6:
        print "error: indir K filestep modelpath outpath"
        return
    rootdir = argv[1]
    K = int(argv[2])
    resample = int(argv[3])
    modelpath = argv[4]
    outdir = argv[5]
    siftfiles = scanfor(rootdir, '.sift')
    samples,attribs = load_sift(siftfiles)
    model = skcluster.KMeans(K,n_jobs=-2,n_init=1)
    model.fit(samples[0::resample,:]) #using a small set to train
    joblib.dump(model, modelpath)
    del samples
    del attribs
    del model
    gc.collect()
    print "train done\n"
    mt_predict(rootdir, outdir, modelpath, K)
    print "predict done!"
    return




if __name__=="__main__":
    entry(sys.argv)


