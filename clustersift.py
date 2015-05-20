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
    attribs = []
    for roots,dirs,files in os.walk(rootdir):
        for name in files:
            shortname,ext = os.path.splitext(name)
            if 0 == cmp(ext, ".sift"):
                filepath=os.path.join(roots, name)
                fin=open(filepath,'r')
                num = 0
                skip = 0
                for rawline in fin:
                    line=rawline.strip().split(' ')

                    skip = skip + 1
                    if 0 != skip % 4:
                        continue

                    num = num + 1
		    if len(attribs)  < 1:
			    attribs = [line[0], line[1], line[2], line[3], line[4]]
		    else:
			    attribs.extend([line[0], line[1], line[2], line[3], line[4]])
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
    return((result,filename,size,attribs))

def entry(rootdir, outdir):
    samples, filenames, sizes, attribs = load_sift(rootdir)
    print "run clustering\n"
    K = 2048
    #connectivity = kneighbors_graph(samples, n_neighbors=10, include_self=True
    #model=skcluster.AgglomerativeClustering(K, connectivity=connectivity )
    #model=model.fit(samples)
    model = skcluster.KMeans(K,n_jobs=-1,n_init=3)
    model.fit(samples)
    joblib.dump(model, 'models/model.pkl')
    print "clustering done\n"

    ypred = model.predict(samples[0,:])
    print "predict " + str(ypred)
    i = 0
    for idx in range(len(sizes)):
        fout = open(outdir+filenames[idx]+".clustersift","w")
        for k in range(sizes[idx]):
            line = attribs[i*5] + " " + attribs[i*5+1] + " " + attribs[i*5+2] +" "+ attribs[i*5+3] +" "+ attribs[i*5+4] +" "+ str(model.labels_[i]) + "\n"
            i = i + 1
            fout.write(line)
        fout.close()
    return(model)
if __name__=="__main__":
    rootdir=os.path.abspath('.') + '/'
    cluster = entry(rootdir+"sift/", "cluster/") 
