#import numpy as np
#import matplotlib as ml
#import matplotlib.pyplot as plt
#from pylab import *
import os
from numpy import *

## THis file path is for a text file containing RR interval data recorded from bluetooth HRM
f = "C:/.........../rrFile.txt"

# Reads text file data and stores it in an array
def ReadData():
    with open(f, 'r') as myfile:
        rawdata = myfile.readlines()
        hrvlets = []
    myfile.close()
    if rawdata != []:
        rawdata = rawdata[0].split(',')

    for ele in range (0,round(len(rawdata)/2)):
        #Something is wrong with this chunk, probably don't need try/except
        try:
            if rawdata[2*ele] != ('0.00' or " ") and float(rawdata[2*ele]) < 2000:
                hrvlets.insert(0,[rawdata[2*ele],rawdata[2*ele + 1]])
                hrvlets[0][0] = float(hrvlets[0][0])
        except:
            pass
            #print (rawdata[2*ele])
    return hrvlets

def embed(data, dim):
    n = len(data)
    l = n-dim+1
    embedded = zeros(l, dtype=object)
    for i in range (0, l):
        temp = zeros(dim)
        for j in range (0, dim):
            temp[j] = data[i+j]
        embedded[i] = temp
    return embedded
#Test function used for Fitgra Metric 
def pls(a):
    c = a
    n = len(c)
    def recurse(x):
        j = x+1
        b = c[x]
        while j < n:
            if b > c[j]:
                c[x] = c[j]
                c[j] = b
                b = c[x]
                j+=1
            else: j+=1
    for i in range(0, 5):
        recurse(i)
    return c[0:5]
    
### Class containing first available metrics
class RRMetrics():
    
    def BPM(data,n):          ####BMP
        try:
            return (60000/int(float(data[0][0])))
        except:
            return []


    def RMSSD(data,n):           #RMSSD
        sig = 0
        if len(data) >= n:
            for i in range(0, n-1):
                i1= int(float(data[i+1][0]))
                i2= int(float(data[i][0]))
                sig += (i1 - i2) ** 2
            return (sig/(n-1)) ** (0.5)
        else:
            return 0

    def pNNx(data,n):
        x = 17 #Manually adjust
        count = 0
        if len(data)>=n:
            for i in range (0,n-1):
                if abs(data[i][0] - data[i+1][0]) > x :
                    count += 1
            return (count*100/(n-1))
        else:
            print('Insufficient data. Only ' + str(len(data)) +' data points available.')
            for i in range (0,len(data)-1):
                if abs(data[i][0] - data[i+1][0]) > x :
                    count += 1
            return (count *100/(len(data) - 1))         

    def sdNN(data,n):
        avg = RRMetrics.meanNN(data,n)
        sig = 0
        if len(data)>=n:
            for i in range(0,n):
                sig += (float(data[i][0]) - avg) ** 2
            return (sig / n) ** 0.5
        else:
            print('Insufficient data. Only ' + str(len(data)) +' data points available.')
            for i in range(1,len(data)):
                sig += (float(data[i][0]) - avg) ** 2
            return(sig / len(data)) ** 0.5       
        
        
    def meanNN(data,n):
        total = 0
        if len(data)>=n:
            for i in range(0,n):
                total += float(data[i][0])
            return (total / n)
        else:
            print('Insufficient data. Only ' + str(len(data)) +' data points available.')
            for i in range(0,len(data)):
                total += float(data[i][0])
            return(total/len(data))

            return 0


    
#    def getFitgra(roughdata, n):
#        data = []
#        for point in roughdata:
#            data.append(point[0])
#
#        
#        emDim = 9
#        neighbours = 5
#        tau = 1
#        steps = 1
#        l = n-emDim+1                         #l=n-emDim+1
#        lamda = zeros(l-1)
#        avg = 0
#
#        
#        def avgNN(a, index):
#            fixedPoint = a[index]       #pop POP
#            a1 = delete(a, index)
#            deez = zeros(l-2)           #nuts
#            for m in range (0, l-2):
#                dis = 0
#                for t in range (0, emDim):
#                    dis += (fixedPoint[t] - a1[m][t]) ** 2
#                deez[m] = dis ** 0.5
#            orderedNN = pls(deez)
#            return orderedNN.mean()
#        
#        if len(data) < neighbours+2:
#            return null
#        else:                           #number of embedding vectors, each of length 9
#            emVectors = zeros(l, dtype=object)
#            emVectors = embed(data, emDim)
#            base = emVectors[0:l-1]            #length n-9 = |emVectors|-1
#            step = emVectors[1:l]              #length n-9 = |emVectors|-1
#
#            for k in range (0, l-1):           #generate time series of growth rates
#                dStep = avgNN(step, k)
#                dBase = avgNN(base, k)
#                lamda[k] = log(dStep/dBase)                
#
#        return lamda.mean() * 100
#
#    def getApEn(roughdata, n):
#        data = []
#        for point in roughdata:
#            data.append(point[0])
#            
#        dim = 2
#        data = data[0:n]
#        rrEmbed = embed(data, dim)
#        rrEmbed1 = embed(data, dim+1)
#        tolerance = 0.2 * std(data)
#        l = len(rrEmbed)             # = n-dim+1
#        l1 = len(rrEmbed1)           # = n-dim
#
#        def getPhi(a, L, emLen):
#            C = zeros(L)             #list of (normalized) cardinalities of sets containing sufficiently "close" vectors
#            P = 0
#            
#            for j in range (0, L):
#                u_j = a[j]
#                Cj = 0
#                for i in range (0, L):
#                    dist = zeros(emLen)
#                    for k in range (0, emLen):
#                        dist[k] = abs(u_j[k] - a[i][k])
#                    if max(dist) <= tolerance:
#                        Cj += 1 / L
#                C[j] = Cj
#            for i in range (0, L):
#                P += log(C[i]) / L
#                
#            return P 
#
#        Phi = getPhi(rrEmbed, l, dim)
#        Phi1 = getPhi (rrEmbed1, l1, dim+1)
#        
#        return (Phi - Phi1)*10
#        
#    def GetRecurrance(data, e):
#        return 0
#
#    
#    def Poincare(data):
#        PM = []
#        for i in range(0,len(data)-1):
#            PM.append([float(data[i][0]),float(data[i+1][0])])
#        return PM

