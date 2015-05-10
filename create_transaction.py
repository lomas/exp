import os
import sys
import numpy as np

def load_clustersift(path):
	result = []
	file = open(path,'r')
	for line in file:
		elems = line.strip().split(' ')
		if len(result) < 1:
			result = [float(elems[0]), float(elems[1]), float(elems[2]), float(elems[3]), float(elems[4]), float(elems[5])]
		else:
			result.extend([float(elems[0]), float(elems[1]), float(elems[2]), float(elems[3]), float(elems[4]), float(elems[5])])
	result = np.array(result)
	result.shape = (-1, 6)
	file.close()
	return(result)

def create_transaction(data, K):
	num = data.shape[0]
	result = []
	for k in range(num):
		mat = np.zeros((9, K))
		f0,x0,y0,s0,a0,c0 = data[k, 0:6]
		for j in range(num):
		#	if j == k:
		#		continue #excluding itself
			f1,x1,y1,s1,a1,c1 = data[j,0:6]
			if np.absolute(x1-x0) >= 1.5 * s0 or np.absolute(y1-y0) >= 1.5 * s0:
				continue
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

def entry(rootdir,outdir, K):
	for absdir, reldir, names in os.walk(rootdir):
		for name in names:
			shortname,ext = os.path.splitext(name)
			if 0 == cmp(ext, ".clustersift"):
				print name
				fullpath = os.path.join(absdir, name)
				data = load_clustersift(fullpath)
				trans = create_transaction(data, K)	
				fullpath = os.path.join(outdir, name + ".trasc")
				save_transaction(trans, fullpath)
if __name__ == "__main__":
	K = 512 #cluster number
	rootdir = os.path.abspath('.') + '/'
	entry(rootdir + 'cluster/', rootdir + 'transc/', K)	
