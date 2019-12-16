# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 11:22:44 2019

@author: zohre
"""

"""
Porgrammer Zohreh Raziei: zohrehraziei@gmail.com
vehicle Routing Problem with using Heuristic with Valid Inequality

        
"""
import math
import random
import networkx
from gurobipy import *


def vrp(V,c,m,q,Q,veh_set,hobj):
    def vrp_callback(model,where):

        # remember to set     model.params.DualReductions = 0     before using!
        # remember to set     model.params.LazyConstraints = 1     before using!
        if where != GRB.callback.MIPSOL:
            return
        edges = []
        for (i,j) in x:
            if model.cbGetSolution(x[i,j]) > .5:
                if i != V[0] and j != V[0]:
                    edges.append( (i,j) )
        G = networkx.Graph()
        G.add_edges_from(edges)
        Components = networkx.connected_components(G)
        for S in Components:
            S_card = len(S)
            q_sum = sum(q[i] for i in S)
            NS = int(math.ceil(float(q_sum)/Q))
            S_edges = [(i,j) for i in S for j in S if i<j and (i,j) in edges]
            if S_card >= 3 and (len(S_edges) >= S_card or NS > 1):
                model.cbLazy(quicksum(x[i,j] for i in S for j in S if j > i) <= S_card-NS)
                print ("adding cut for",S_edges)
        return


    model = Model("vrp")
    model.setParam('LogToConsole',0)
    x = {}
    for i in V:
        for j in V:
            if j > i and i == V[0]:       # depot
                x[i,j] = model.addVar(ub=2, vtype="I", name="x(%s,%s)"%(i,j))
            elif j > i:
                x[i,j] = model.addVar(ub=1, vtype="I", name="x(%s,%s)"%(i,j))
    model.update()

    model.addConstr(quicksum(x[V[0],j] for j in V[1:]) == 2*m, "DegreeDepot")
    model.addConstr(quicksum(c[i,j]*x[i,j] for i in V for j in V if j>i) <= hobj, "UpperBound")
    for veh in veh_set:
        idx = veh_set.index(veh)
        if idx < len(veh_set)-1:
            min_idx = min(veh[-1],veh_set[idx+1][0])
            max_idx = max(veh[-1],veh_set[idx+1][0])
            rhs = len(veh)+2
            model.addConstr(x[1,veh[1]] + x[1,veh[-1]] + quicksum(x[min(veh[j],veh[j+1]),max(veh[j],veh[j+1])]  for j in range(len(veh)-1) ) + x[min_idx,max_idx] <= rhs, "Valid(%s)"%idx)
            for nd in V:
                if nd != V[0]:
                    model.addConstr(x[1,veh[1]] + x[1,veh[-1]] + quicksum(x[min(veh[j],veh[j+1]),max(veh[j],veh[j+1])] for j in range(len(veh)-1) ) + x[1,nd] <= rhs, "Valid2(%s)"%idx)
    
    for i in V[1:]:
        model.addConstr(quicksum(x[j,i] for j in V if j < i) +
                        quicksum(x[i,j] for j in V if j > i) == 2, "Degree(%s)"%i)

    model.setObjective(quicksum(c[i,j]*x[i,j] for i in V for j in V if j>i), GRB.MINIMIZE)

    model.update()
    model.__data = x
    return model,vrp_callback


def distance(x1,y1,x2,y2):
    """distance: euclidean distance between (x1,y1) and (x2,y2)"""
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def make_data(n):
    """make_data: compute matrix distance based on euclidean distance"""
    V = range(1,n+1)
    #x = dict([(i,random.random()) for i in V])
    #y = dict([(i,random.random()) for i in V])
    c,q,x,y = {},{},{},{}
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
    Q = 100
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
            measure.remove(measure[n1])
            nodes.remove(nodes[n1])
            C = Q - q[nodes[n1]]
            while C > 0:
                ls = [c[(min(veh[-1],int(i)),max(veh[-1],int(i)))] for i in nodes if int(i) != 1]
                ls2 = [int(i) for i in nodes if int(i) != 1]
                if len(ls)>0:
                    n1 = int(ls2[ls.index(min(ls))]) - 1
                    C = C - q[n1]
                    obj += c[(min(veh[-1],int(n1+1)),max(veh[-1],int(n1+1)))]
                    veh.append(n1+1)
                    measure.remove(measure[nodes.index(n1+1)])
                    nodes.remove(n1+1)
                else:
                    break
            obj += c[(1,veh[-1])]
            veh_set.append(veh)
        else:
            break
            
    return veh_set, obj


def heuristic(V,c,m,q,Q):
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
    m = 3
    seed = 1
    random.seed(seed)
    #V,c,q,Q = make_data(n)
    V,c,q,Q = read_data()
    veh_set, obj = heuristic_greedy(V,c,m,q,Q)
    print ("heuristic objective: ", obj)
    print (veh_set)
    start_time2 = time.time()
    print("--- Running time: %s seconds ---" % (time.time() - start_time2))
    
    
     
    model,vrp_callback = vrp(V,c,m,q,Q,veh_set,obj)

    # model.Params.OutputFlag = 0 # silent mode
    # 0 : min value
    model.params.DualReductions = 0 
    model.params.LazyConstraints = 1  
    #1: Implies Gurobi algorithms to avoid certain reductions and transformations
    #that are incompatible with lazy constraints.
    start_time3 = time.time()
    model.optimize(vrp_callback)
    x = model.__data
    
    edges = represent(x)
    
    print ("Optimal objective:",model.ObjVal)
    print ("Edges in the solution:")
    print (sorted(edges))
    print ("Positive Vars: ")
    var_print(x)
    
    
    print("--- Running time valid inequalities: %s seconds ---" % (time.time() - start_time3))

   
