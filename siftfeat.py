import cv2
import os
import sys
import numpy as np
import pdb


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
def parse_pos(rootdir,outdir):
    siftfeat = cv2.SIFT()
    num = 1
    for roordir,pdirs,files in os.walk(rootdir):
	    for name in files:
		    shortname,ext = os.path.splitext(name)
		    if 0 == cmp(ext, '.jpg'):
			    print("[%d][%s]" %(num, name))
			    num = num + 1
			    imgpath = os.path.join(rootdir,name)
			    scriptpath = os.path.join(rootdir,script_filename(shortname))
			    img = cv2.imread(imgpath,0)
			    script=load_script(scriptpath)
			    kp = siftfeat.detect(img)
			    kp,des = siftfeat.compute(img,kp)
			    save_sift(outdir+name+".sift",script,kp,des)

if __name__ == "__main__":
    rootdir = os.path.abspath('.') + '/pos/'
    parse_pos(rootdir,'sift/')  
  
  
