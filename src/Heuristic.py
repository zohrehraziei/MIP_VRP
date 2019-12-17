# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 11:22:44 2019

@author: zohre
"""

"""
Porgrammer Zohreh Raziei: zohrehraziei@gmail.com
vehicle Routing Problem with using Greedy Heuristic

        
"""
import math
import random
import networkx
from gurobipy import *



def distance(x1,y1,x2,y2):
    """distance: euclidean distance between (x1,y1) and (x2,y2)"""
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)


def read_data():
    import xlrd
    file_loc=".\\dist.xlsx"
    wkb=xlrd.open_workbook(file_loc)
    dat_mat = []
    nrow = 0
    for sht in range(2): #Three sheets: 0:c[i,j] 1:q[j], 2:vlu[j]
        sheet=wkb.sheet_by_index(sht)
        _matrix=[]
        nrow = 0
        for row in range (sheet.nrows):
            _row = []
            nrow += 1
            for col in range (sheet.ncols):
                _row.append(sheet.cell_value(row,col))
            _matrix.append(_row)    
        dat_mat.append(_matrix)
    
    V = range(1,nrow+1)
    c,q,x,y = {},{},{},{}
    Q = 350
   # q = {}
    for i in V:
        q[i] = dat_mat[1][i-1][0]
        x[i] = dat_mat[0][i-1][0]
        y[i] = dat_mat[0][i-1][1]
    for i in V:
        for j in V:
            if j > i:
                c[i,j] = distance(x[i],y[i],x[j],y[j])
            
#        for j in V:
#            if j > i:
#                c[i,j] = dat_mat[0][i-1][j-1]
          
    return V,c,q,Q


def heuristic_greedy(V,c,m,q,Q):
    demands = list(q.values())
    nodes = list(q.keys())
    measure = [demands[i-1]*(0.1/(c[(1,int(i))] if i != 1 and c[(1,int(i))] != 0 else 10000)) for i in nodes]
    veh_set = []   
    obj = 0
    
    while len(demands) > 0:
        n1 = measure.index(max(measure))
        if len(nodes) > 1:
            veh = [nodes[n1]]
            obj += c[(1,nodes[n1])]
            C = Q - q[nodes[n1] - 1]
            measure.remove(measure[n1])
            nodes.remove(nodes[n1])
            while C > 0:
                ls = [c[(min(veh[-1],int(i)),max(veh[-1],int(i)))] for i in nodes if int(i) != 1]
                ls2 = [int(i) for i in nodes if int(i) != 1]
                if len(ls)>0:
                    n1 = int(ls2[ls.index(min(ls))]) 
                    C = C - q[n1 - 1]
                    obj += c[(min(veh[-1],int(n1)),max(veh[-1],int(n1)))]
                    veh.append(n1)
                    measure.remove(measure[nodes.index(n1)])
                    nodes.remove(n1)
                else:
                    break
            obj += c[(1,veh[-1])]
            veh_set.append(veh)
        else:
            break
            
    return veh_set, obj


      

def var_print(x):
    for var in x:
        if x[var].X > 0.5:
            print (x[var])

 
           
if __name__ == "__main__":
    import sys
    import time
    
    
    #n = 20
    m = 4
    seed = 1
    random.seed(seed)
    #V,c,q,Q = make_data(n)
    V,c,q,Q = read_data()
    start_time2 = time.time()
    veh_set, obj = heuristic_greedy(V,c,m,q,Q)
    print ("heuristic objective: ", obj)
    print (veh_set)
    print("--- Running time: %s seconds ---" % (time.time() - start_time2))

