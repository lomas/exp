import os
import sys
import itertools
import pdb

class tapriori:
    def __init__(self, dataDict , minsupport=0.2, minconfidence = 0.8):
        self.data = dataDict
        self.minsup = minsupport
        self.minconf = minconfidence

    def check_subset_freq(self, candi, prevfqits):
        subsets = itertools.combinations(candi, len(candi) - 1)
        for each in subsets:
            each = list(each)
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
        for key in L.keys():
            if L[key] >= t:
                fqits.append([key])
        print "# of freq_1 " + str(len(fqits))
        return fqits
    


    def get_next_freqitems(self, prevfqits):
        L = []
        prevsize = len(prevfqits[0])
        for its1 in prevfqits:
            for its2 in prevfqits:
                mergable = 1
                for k in range(prevsize - 1):
                    if its1[k] != its2[k]:
                        mergable = 0
                        break
                if mergable == 0:
                    continue
                if its1[prevsize - 1] >= its2[prevsize - 1]:
                    continue
                candi = its1 + [its2[prevsize - 1]]

                if self.check_subset_freq(candi, prevfqits) == False:
                    continue
                L.append(candi)

        fqdict = {}
        for key in self.data.keys():
            for each in L:
                if set(each) <= set(self.data[key]): #subset of input items
                    if tuple(each) in fqdict:
                        fqdict[tuple(each)] += 1 #key should not be list. tuple is ok
                    else:
                        fqdict[tuple(each)] = 1
        t = self.minsup * len(self.data)
        L = []
        for key in fqdict.keys():
            if fqdict[key] >= t:
                L.append(list(key))
        
        return L
       
    def run(self):
        prevfqits = self.get_freqitems_1()
        result = []
        while prevfqits != []:
            result += prevfqits
            #pdb.set_trace()
            prevfqits = self.get_next_freqitems(prevfqits)
        return result 

def do_stat(dataDict, fs, freqItems):
    result = {}
    for item in freqItems:
        result[tuple(item)] = [0,0]
    for key in dataDict.keys():
        item = tuple(dataDict[key])
        f = fs[key]
        if item in result:
            result[item][f] += 1
    return result

def example():
    data = {'a':[1,2,5],'b':[2,4],'c':[2,3],'d':[1,2,4],'e':[1,3],'f':[2,3],'g':[1,3],'h':[1,2,3,5],'i':[1,2,3]}
    inst = tapriori(dataDict = data)
    print inst.run()

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
                    transc = [int(k) for k in items]
                    result[nextkey] = transc[0:-1] #ignore the last item
                    flags[nextkey] = transc[-1]
                    nextkey += 1
                fin.close()
                print shortname + ' ' + str(nextkey)
    return result, flags

if __name__=="__main__":
    rootdir = os.path.abspath('.') + '\\'
    data,flags = load_transc(rootdir + 'transc\\')
    #pdb.set_trace()
    inst = tapriori(dataDict = data, minsupport=0.002, minconfidence=0.2)
    items = inst.run()
    print "# of item with minimum support = " + str(len(items))
    result = do_stat(data, flags, items)
    for key in result.keys():
        print str(key) + " " + str(result[key]) 
