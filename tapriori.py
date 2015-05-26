import os
import sys
import itertools
import pdb
import pickle
from multiprocessing import Process,cpu_count
import datetime
#the key of dict of data and L is confused!!!

def mt_fqits_get_freq(data, L, outpath):
     fqdict = {}
#     print outpath + " " + str(len(L))
     prg = 0 
     t0 = datetime.datetime.now()
     for key in data.keys():
        #pdb.set_trace()
        prg += 1
        if len(data) > 10000 and 0 == prg%1000:
            t1 = datetime.datetime.now()
            t = (t1 - t0).seconds / 60.0
            est = t * len(data) / prg
            logfile = open('tapriori%d.log' %(os.getpid()),'a+')
            line = '%f = %d/%d [%f, %f]\n' %(prg * 1.0 / len(data), prg, len(data), t, est)
            logfile.write(line)
            logfile.close()

        for each in L:
            if set(each) <= set(data[key]): #subset of input items
                if tuple(each) in fqdict:
                    fqdict[tuple(each)] += 1 #key should not be list. tuple is ok
                else:
                    fqdict[tuple(each)] = 1
     fout = open(outpath, 'w')
     pickle.dump(fqdict, fout)
     fout.close()


class tapriori:
    def __init__(self, dataDict , minsupport=0.2, minconfidence = 0.8):
        self.data = dataDict
        self.minsup = minsupport
        self.minconf = minconfidence

    def check_subset_freq(self, candi, prevfqits):
        subsets = itertools.combinations(candi, len(candi) - 1)
        for each in subsets:
            each = list(each)
#            pdb.set_trace()
            if each not in prevfqits:
                return False
        return True
    
    def get_freqitems_1(self):
        L={}
        for key in self.data.keys():
            for item in self.data[key]:
                if item in L:
                    L[item] += 1
                else:
                    L[item] = 1
        fqits = [] #freq items 
#        pdb.set_trace()
        t = len(self.data) * self.minsup
        print "total of transc = " + str(len(self.data))
        print "min sup ratio = " + str(self.minsup)
        print "min sup number = " + str(t)
        #pdb.set_trace()
        for key in L.keys():
            if L[key] >= t:
                fqits.append([key])
        print "# of freq_1 " + str(len(fqits))
        #for k in range(len(fqits)):
        #    print ' ' + str(k) + ' ' + str(fqits[k])
        return fqits
    


    def get_next_freqitems(self, prevfqits):
#        pdb.set_trace()
        L = []
        prevsize = len(prevfqits[0])
        for its1 in prevfqits:
            for its2 in prevfqits:
        #        pdb.set_trace()
                mergable = 1
                for k in range(prevsize - 1):
                    if its1[k] != its2[k]:
                        mergable = 0
                        break
                if mergable == 0:
                    continue
                if its1[prevsize - 1] >= its2[prevsize - 1]:
                    continue

                candi = list(its1) + [its2[prevsize - 1]]

                if self.check_subset_freq(candi, prevfqits) == False:
                    continue

#                pdb.set_trace()
                L.append(candi)

        print "next fqits: step 1"
        if 0:
            fqdict = {}
            num = 1
            for key in self.data.keys():
                if 0 == num%500:
                    print("progress : %.5f\r" %(num*1.0/len(self.data))),
                num = num + 1
                #pdb.set_trace()
                for each in L:
                    if set(each) <= set(self.data[key]): #subset of input items
                        if tuple(each) in fqdict:
                            fqdict[tuple(each)] += 1 #key should not be list. tuple is ok
                        else:
                            fqdict[tuple(each)] = 1
        else:
            plist = []
            cpunum = cpu_count() - 1
            step = int(len(L)/cpunum)
            for k in range(cpunum):
                n0 = k * step
                n1 = n0 + step
                if n1 > len(L):
                    n1 = len(L)
                if k == cpunum and n1 != len(L):
                    n1 = len(L)
                outpath = "mt%d.txt"%(k)
#                print "main " + " " + str(n0) + " " + str(n1) + " " + str(len(L))
                p = Process(target = mt_fqits_get_freq, args = (self.data, L[n0:n1], outpath))
                plist.append(p)
                p.start()
            for p in plist:
                p.join()

            fqdict = {}
            for k in range(cpunum):
                fin = open('mt%d.txt'%(k), 'r')
                d = pickle.load(fin)
                fin.close()
                for key in d.keys():
                    if key in fqdict:
                        fqdict[key] += d[key]
                    else:
                        fqdict[key] = d[key]
        print ''
        print "get fqits: step 2"
        t = self.minsup * len(self.data)
        L = []
        maxsup = 0
        for key in fqdict.keys():
            if fqdict[key] > maxsup:
                maxsup = fqdict[key]
            if fqdict[key] >= t:
                L.append(list(key))
        print "max sup = " + str(maxsup) 
        
        return L
       
    def run(self):
        prevfqits = self.get_freqitems_1()
        result = []
        round = 1
        while prevfqits != []:
            result += prevfqits
            #pdb.set_trace()
            prevfqits = self.get_next_freqitems(prevfqits)
            round = round + 1
            print "round " + str(round) + "=============="
            print prevfqits
        return result 

def do_stat(dataDict, fs, freqItems):
    result = {}
    for item in freqItems:
        result[tuple(item)] = [0,0]
#    pdb.set_trace()
    for key in result.keys():
        for k in dataDict.keys():
            if set(key) <= set(dataDict[k]):
                result[key][fs[k]] += 1

#    for key in dataDict.keys():
#        item = tuple(dataDict[key])
#        f = fs[key]
#        if item in result:
#            result[item][f] += 1
    return result

def example():
    data = {'a':[1,2,5],'b':[2,4],'c':[2,3],'d':[1,2,4],'e':[1,3],'f':[2,3],'g':[1,3],'h':[1,2,3,5],'i':[1,2,3]}
    inst = tapriori(dataDict = data)
    print inst.run()

def balance_transc(result, flags):

    nums = [0,0] 
    for key in flags.keys():
        nums[flags[key]] += 1
   
     
    if nums[0] > nums[1]:
        n0 = nums[1]
        n1 = nums[0]
    else:
        n0 = nums[0]
        n1 = nums[1]
    if n0 * 100 > n1 * 90:
        return result, flags

    newresult = {}
    newflags = {}
   

    nums = [0,0]
    for key in flags.keys():
        c = flags[key]
        nums[c] += 1
        if nums[c] < n0:
            newflags[key] = c
            newresult[key] = result[key]

    return newresult,newflags 


               

def load_transc(rootdir):
    result = {}
    flags = {}
    nextkey = 0
    for root, pdirs, names in os.walk(rootdir):
        for name in names:
            shortname,ext = os.path.splitext(name)
            if 0 == cmp(ext, ".trasc"):
                fullpath = os.path.join(root, name)
                fin = open(fullpath, 'r')
                for line in fin:
                    items = line.strip().split(' ')
                    if len(items) < 2:
                        continue
                    transc = [int(k) for k in items]
                    result[nextkey] = tuple(transc[0:-1]) #ignore the last item
                    flags[nextkey] = transc[-1]
                    nextkey += 1
                fin.close()
                print shortname + ' ' + str(nextkey)
    print "# raw transc " + str(len(flags))
    result,flags = balance_transc(result,flags)
    print "# balance transc " + str(len(flags))
    return result, flags

if __name__=="__main__":
    indir = sys.argv[1]
    sup = float(sys.argv[2])
    conf = float(sys.argv[3])
    rulefile = sys.argv[4]

    data,flags = load_transc(indir)
    #pdb.set_trace()
    print "# of transc = " + str(len(data))
    inst = tapriori(dataDict = data, minsupport=sup, minconfidence=conf)
    items = inst.run()
    print "# of item with minimum support = " + str(len(items))
    result = do_stat(data, flags, items)
    fout = open(rulefile, 'w')
    pickle.dump(result, fout)
    fout.close()
    print "key -> [neg, pos]"
    for key in result.keys():
        pos = result[key][1]
        neg = result[key][0]
        print str(key) + "->" + str(result[key]) + "->" + str(pos * 1.0 / (pos + neg))
