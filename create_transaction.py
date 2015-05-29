import os
import sys
import numpy as np
import multiprocessing as mp
import pdb
import datetime as dtime

def scanfor(indir, extname):
    files = []
    for rdirs, pdirs, names in os.walk(indir):
        for name in names:
            sname,ext = os.path.splitext(name)
            if 0 == cmp(extname, ext):
                fname = os.path.join(indir, name)
                files.append((sname,fname))
    return files


"""
def load_clustersift(path):
	result = []
	file = open(path,'r')
	for line in file:
		elems = line.strip().split(' ')
#                print elems
		if len(result) < 1:
			result = [float(elems[0]), float(elems[1]), float(elems[2]), float(elems[3]), float(elems[4]), float(elems[5])]
		else:
			result.extend([float(elems[0]), float(elems[1]), float(elems[2]), float(elems[3]), float(elems[4]), float(elems[5])])
	result = np.array(result)
	result.shape = (-1, 6)
	file.close()
	return(result)
"""

def load_clustersift(path):
	result = []
	file = open(path,'r')
	for line in file:
		elems = line.strip().split(' ')
                data = [float(k) for k in elems]
		if len(result) < 1:
			result = [data]
		else:
			result.append(data)
	file.close()
	return(result)



def create_transaction(data, K):
	num = len(data)
	result = []
        """
	for k in range(num):
		mat = np.zeros((9, K))
		f0,x0,y0,s0,a0,c0 = data[k, 0:6]
		for j in range(num):
		#	if j == k:
		#		continue #excluding itself
			f1,x1,y1,s1,a1,c1 = data[j,0:6]
			if np.absolute(x1-x0) >= 1.5 * s0 or np.absolute(y1-y0) >= 1.5 * s0:
                            continue
			if np.absolute(x1-x0) < 0.5 * s0 and np.absolute(y1-y0) < 0.5 * s0:
                            continue #ignore center region 

			dx = np.int32((x1 - x0)/s0)
			dy = np.int32((y1 - y0)/s0)
			dx = np.maximum(dx, -1)
			dx = np.minimum(dx,1)
			dy = np.maximum(dy, -1)
			dx = np.minimum(dy,1)
			pos = (dy + 1) * 3 + dx + 1
			mat[pos, np.int32(c1)] = 1
		feat = []
		for y in range(9):
			for x in range(K):
				if mat[y,x] == 0:
					continue
				feat.append(np.int32(y * K + x))
		feat.append(np.int32(f0))
		result.append(feat)
       
        """
#rotation invariance
	for k in range(num):
		mat = np.zeros((9, K))
		f0,x0,y0,s0,a0 = data[k][0:5]
                c0 = data[k][5:]
		for j in range(num):
			if j == k:
				continue #excluding itself
			f1,x1,y1,s1,a1 = data[j][0:5]
                        c1 = data[j][5:]
			if np.absolute(x1-x0) >= 1.5 * s0 or np.absolute(y1-y0) >= 1.5 * s0:
                            continue
			if np.absolute(x1-x0) < 0.2 * s0 and np.absolute(y1-y0) < 0.2 * s0:
                            continue #ignore center region 
                       
                        pos = a1 - a0
                        if pos < 0:
                            pos += 360
                        if pos > 360:
                            pos -= 360
                        pos = np.int32(pos / 40) #360 / 9 = 40
                        if pos >= 9:
                            pos = 8
                        for c in c1:
                            mat[pos, int(c)-1] = 1
		feat = []
		for y in range(9):
			for x in range(K):
				if mat[y,x] == 0:
					continue
				feat.append(np.int32(y * K + x+1))
		feat.append(np.int32(f0))
		result.append(feat)


	return(result)	

def save_transaction(transactions, filepath):
	file = open(filepath, "w")
	for k in range(len(transactions)):
		item = transactions[k]
		line = ""
		for j in range(len(item)):
			line = line + " "+ str(item[j])
		line = line + "\n"
		file.write(line)	
	file.close()

def entry(files,outdir, K):
        t0 = dtime.datetime.now()
        for k in range(len(files)):
            if (k+1) % 5 == 0:
                fout = open('trans%d.log'%os.getpid(), 'a+')
                t1 = dtime.datetime.now()
                t2 = (t1 - t0).seconds/ 60.0
                line = '%d %d [%f %f]\n' %(k+1, len(files), t2,t2 * len(files) / (k+1))
                fout.write(line)
                fout.close()
            shortname, fullname = files[k]    
            data = load_clustersift(fullname)
            trans = create_transaction(data, K)	
            fullpath = os.path.join(outdir, shortname + ".trasc")
            save_transaction(trans, fullpath)



def do_mt(indir, outdir, K): 
#    pdb.set_trace()
    files = scanfor(indir, '.clustersift')
    tasknum = mp.cpu_count() - 1
    tasksize = int(len(files) / tasknum)
    procs = []
    for k in range(tasknum):
        s0 = k * tasksize
        s1 = s0 + tasksize
        if k+1 == tasknum or s1 > len(files):
            s1 = len(files)
        p = mp.Process(target=entry, args=(files[s0:s1], outdir, K))
        procs.append(p)
        p.start()
    for p in procs:
        p.join()
    print "done"

if __name__ == "__main__":
        indir = sys.argv[1]
	K = int(sys.argv[2])#cluster number
        outdir = sys.argv[3]
        do_mt(indir, outdir, K)

