import os
import sys
import sklearn.cluster as skcluster
import numpy as np
import pdb

def load_sift(rootdir):
    result = []
    filename = [] #file name
    size = [] #sift number in each file
    for roots,dirs,files in os.walk(rootdir):
        for name in files:
            shortname,ext = os.path.splitext(name)
            if 0 == cmp(ext, ".sift"):
                filepath=os.path.join(roots, name)
                fin=open(filepath,'r')
                num = 0
                for rawline in fin:
                    line=rawline.strip().split(' ')
                    num = num + 1
                    for idx in range(len(line) - 5):
                             if len(result) < 1:
                                 result = [np.float32(line[idx+5])]
                             else:
                                 result.append(np.float32(line[idx+5]))
                fin.close()
                if len(size) < 1:
                    size = [num]
                    filename = [name]
                else:
                    size.append(num)
                    filename.append(name)
                print "load: " + shortname + " " + str(len(result)/128.0) + "\n"
    result = np.array(result)
    result.shape = (-1,128)
    print "result " + str(result.shape[0]) + " " + str(result.shape[1]) + "\n"
    return((result,filename,size))

def entry(rootdir, outdir):
    samples, filenames, sizes = load_sift(rootdir)
    print "run clustering\n"
    K = 1000
    cluster=skcluster.AgglomerativeClustering(K)
    cluster=cluster.fit(samples)
    print "clustering done\n"
    i = 0
    for idx in range(len(sizes)):
        fout = open(outdir+filenames[idx]+".cluster","w")
        for k in range(sizes[idx]):
            line = str(cluster.labels_[i]) + "\n"
            i = i + 1
            fout.write(line)
        fout.close()
    return(cluster)
if __name__=="__main__":
    rootdir=os.path.abspath('.') + '/'
    cluster = entry(rootdir+"sift/", "cluster/") 
