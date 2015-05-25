import cv2
import os
import sys
import numpy as np
import pdb,datetime
from multiprocessing import cpu_count, Process

#get script file name from image name
def script_filename(shortname):
	return(shortname+"_entires.groundtruth")	

def load_script(scriptpath):
	result=[]
	fin = open(scriptpath, 'r')
	for rawline in fin:
		line = rawline.strip().split(' ')
		newline = []
		for elem in line:
			if len(elem) == 0:
				continue
			if len(newline) == 0:
				newline = [elem]
			else:
				newline.append(elem)
		x0 = np.int32(np.float32(newline[0]))
		y0 = np.int32(np.float32(newline[1]))
		x1 = np.int32(np.float32(newline[2]))
		y1 = np.int32(np.float32(newline[3]))
		if len(result) < 1:
			result = [x0,y0,x1,y1]
		else:
			result.extend([x0,x0,x1,y1])
	fin.close()
	result = np.array(result)
	result.shape = (-1,4)
	return(result)

def save_sift(outpath,script, kp, des):
	fout = open(outpath,'w')
	#pdb.set_trace()
	for idx in range(len(kp)):
		x,y = kp[idx].pt
		posneg = 0
		for k in range(script.shape[0]):
			x0,y0,x1,y1 = script[k,:]
			if x >= x0 and x <= x1 and y >= y0 and y <= y1:
				posneg = 1
				break
		scale = kp[idx].size
		angle = kp[idx].angle
		line = str(posneg) + " " + str(x) + " " + str(y) + " " + str(scale) + " " + str(angle) + " "
		for k in range(des.shape[1]):
			line = line + str(des[idx,k]) + " "
		line = line + '\n'
		fout.write(line)
	fout.close()


def run(jpgfiles,outdir,mode):
    siftfeat = cv2.SIFT()
    jpgnum = len(jpgfiles)
    t0 = datetime.datetime.now()
    for k in range(jpgnum):
        shortname, fullname = jpgfiles[k]
        if 0 == (1+k)%20:
            fout = open('siftfeat_%d.log'%(os.getpid()),'a+')
            t1 = datetime.datetime.now()
            t2 = (t1 - t0).seconds/60.0
            line = '%d,%d,%f,%f\n' %(k+1, jpgnum, t2, t2 * jpgnum / (k+1))
            fout.write(line)
            fout.close()
        img = cv2.imread(fullname,0)
        if 0 == cmp(mode,'pos'):
            script = np.array([0,0,img.shape[1],img.shape[0]])
        else:
            script = np.array([-1,-1,-1,-1])
        script.shape = (1,4)
        kp = siftfeat.detect(img)
        kp,des = siftfeat.compute(img,kp)
        save_sift(outdir+shortname+".sift",script,kp,des)

def scanforjpg(rootdir):
    result = []
    for rdirs, pdirs,names in os.walk(rootdir):
        for name in names:
            sname,ext = os.path.splitext(name)
            if 0 == cmp(ext, '.jpg'):
                fname = os.path.join(rootdir, name)
                result.append((sname,fname))
    return result 

def entry(argv):
    if len(argv) != 4:
        print "error input"
        return
    indir = argv[1]
    outdir=argv[2]
    mode=argv[3]

    jpgfiles = scanforjpg(indir)
    if len(jpgfiles) < 1:
        print "no jpg found"
        return
    tasknum = cpu_count() - 1
    tasksize = int(len(jpgfiles) / tasknum)
    procs = []
    for k in range(tasknum):
        s0 = k * tasksize
        s1 = s0 + tasksize
        if s1 > len(jpgfiles) or k + 1 == tasknum:
            s1 = len(jpgfiles)
        p = Process(target=run, args=(jpgfiles[s0:s1],outdir, mode))
        procs.append(p)
        p.start()
    for p in procs:
        p.join()
    print "siftfeat done!"

if __name__ == "__main__":
    "[indir] [outdir] [pos/neg]"
    entry(sys.argv) 
  
