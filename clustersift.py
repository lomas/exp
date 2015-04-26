import os
import sys
import sklearn.cluster as skcluster
from sklearn.neighbors import kneighbors_graph #using connectivity to avoid memory error in clustring
from sklearn.externals import joblib #save/load models
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
    connectivity = kneighbors_graph(samples, n_neighbors=10)
    cluster_tree=skcluster.AgglomerativeClustering(K, connectivity=connectivity)
    cluster_tree=cluster_tree.fit(samples)
    joblib.dump(cluster_tree, 'models/cluster_tree.pkl')
    print "clustering done\n"
    i = 0
    for idx in range(len(sizes)):
        fout = open(outdir+filenames[idx]+".cluster_tree","w")
        for k in range(sizes[idx]):
            line = str(cluster_tree.labels_[i]) + "\n"
            i = i + 1
            fout.write(line)
        fout.close()
    return(cluster_tree)
if __name__=="__main__":
    rootdir=os.path.abspath('.') + '/'
    cluster = entry(rootdir+"sift/", "cluster/") 
