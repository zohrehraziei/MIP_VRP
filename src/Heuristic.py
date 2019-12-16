# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 11:22:44 2019

@author: zohre
"""

"""
Porgrammer Zohreh Raziei: zohrehraziei@gmail.com
vehicle Routing Problem with using cut generation

        
"""
import math
import random
import networkx
from gurobipy import *



def distance(x1,y1,x2,y2):
    """distance: euclidean distance between (x1,y1) and (x2,y2)"""
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def make_data(n):
    """make_data: compute matrix distance based on euclidean distance"""
    V = range(1,n+1)
    #x = dict([(i,random.random()) for i in V])
    #y = dict([(i,random.random()) for i in V])
    c,q,vlu,x,y = {},{},{},{},{}
    Q = 100
    for i in V:
     #   q[i] = random.randint(10,20)
       # Valuee[i] = random.randint(20,30)
        for j in V:
            if j > i:
                c[i,j] = distance(x[i],y[i],x[j],y[j])
                
    return V,c,q,Q,vlu

def read_data():
    import xlrd
    file_loc=".\\dist.xlsx"
    wkb=xlrd.open_workbook(file_loc)
    dat_mat = []
    nrow = 0
    for sht in range(3): #Three sheets: 0:c[i,j] 1:q[j], 2:vlu[j]
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
    c,q,vlu,x,y = {},{},{},{},{}
    Q = 100
   # q = {}
    for i in V:
        q[i] = dat_mat[1][i-1][0]
        vlu[i] = dat_mat[2][i-1][0]
        x[i] = dat_mat[0][i-1][0]
        y[i] = dat_mat[0][i-1][1]
    for i in V:
        for j in V:
            if j > i:
                c[i,j] = distance(x[i],y[i],x[j],y[j])
            
#        for j in V:
#            if j > i:
#                c[i,j] = dat_mat[0][i-1][j-1]
          
    return V,c,q,Q,vlu

def represent(x):
    edges = []
    tour = ''
    for i in V:
        if i > V[0] and x[V[0],i].X > .5:
            cond = True
            for t in edges:
                if str(i) in t:
                    cond = False
                    break
            if cond == True:
                tour = str(V[0]) + ' - ' + str(i)
                nextn = i   
                prevnext = nextn
                point = [str(V[0]) + ',' + str(i)]
                for v in V:
                    if nextn == V[0]:
                        break
                    for (ii,jj) in x:
                        e = str(ii) + ',' + str(jj)
                        if e not in point and x[ii,jj].X > .5:
                            if str(nextn) == str(ii):
                                point.append(str(ii) + ',' + str(jj))
                                tour += ' - ' + str(jj)
                                nextn = jj
                            elif str(nextn) == str(jj):
                                point.append(str(ii) + ',' + str(jj))
                                tour += ' - ' + str(ii)
                                nextn = ii
                            if nextn == V[0]:
                                edges.append(tour)
                                break
                if nextn == prevnext:
                    tour += ' - ' + str(V[0])
                    edges.append(tour)
                
    return edges

def heuristic(V,c,m,q,Q,vlu):
    nodes = list(q.values())
    nodes2 = list(q.keys())
    veh_set = []   
    obj = 0
    
    while len(nodes) > 0:
        n1 = nodes.index(max(nodes))
        if n1 > 1:
            veh = [n1]
            obj += c[(1,n1)]
            nodes.remove(q[n1])
            nodes2.remove(n1)
            C = Q - q[n1]
            while C > 0:
                ls = [c[(veh[-1],int(i))] for i in nodes2 if int(i) != 1 and i > veh[-1]]
                ls2 = [int(i) for i in nodes2 if int(i) != 1 and i > veh[-1]]
                if len(ls)>0:
                    n1 = int(ls2[ls.index(min(ls))])
                    C = C - q[n1]
                    obj += c[(veh[-1],n1)]
                    veh.append(n1)
                    nodes.remove(q[n1])
                    nodes2.remove(n1)
                else:
                    break
            obj += c[(1,veh[-1])]
            veh_set.append(veh)
        else:
            break
            
    print(veh_set)
    print ("objective: ", obj)
        
        

def var_print(x):
    for var in x:
        if x[var].X > 0.5:
            print (x[var])

 
           
if __name__ == "__main__":
    import sys
    import time
    
    
    #n = 20
    m = 5
    seed = 1
    random.seed(seed)
    #V,c,q,Q = make_data(n)
    V,c,q,Q,vlu = read_data()
    heuristic(V,c,m,q,Q,vlu)
    
    start_time2 = time.time()
    
    print("--- Running time: %s seconds ---" % (time.time() - start_time2))

   
