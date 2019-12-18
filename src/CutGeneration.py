"""
Porgrammer Zohreh Raziei: zohrehraziei@gmail.com
vehicle Routing Problem with using cut generation

        
"""
import math
import random
import networkx
from gurobipy import *


def vrp2(V,c,m,q,Q):    
    def vrp_cutgen(model):
        isCut = False
        x = model.__data
        edges = []
        for (i,j) in x:
            if x[i,j].X > .5:
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
                #add cut as a constraint
                model.addConstr(quicksum(x[i,j] for i in S for j in S if j > i) <= S_card-NS)
                print ("adding cut for",S_edges)
                isCut = True
                
        return isCut


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
    for i in V[1:]:
        model.addConstr(quicksum(x[j,i] for j in V if j < i) +
                        quicksum(x[i,j] for j in V if j > i) == 2, "Degree(%s)"%i)

    model.setObjective(quicksum(c[i,j]*x[i,j] for i in V for j in V if j>i), GRB.MINIMIZE)

    model.update()
    model.__data = x
    return model,vrp_cutgen

def distance(x1,y1,x2,y2):
    """distance: euclidean distance between (x1,y1) and (x2,y2)"""
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def make_data(n):
    """make_data: compute matrix distance based on euclidean distance"""
    V = range(1,n+1)
    #x = dict([(i,random.random()) for i in V])
    #y = dict([(i,random.random()) for i in V])
    c,q,x,y = {},{},{},{}
    Q = 350
    for i in V:
     #   q[i] = random.randint(10,20)
       # Valuee[i] = random.randint(20,30)
        for j in V:
            if j > i:
                c[i,j] = distance(x[i],y[i],x[j],y[j])
                
    return V,c,q,Q

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
    model,vrp_cutgen = vrp2(V,c,m,q,Q)
    model.params.LazyConstraints = 0
    isCut = True
    while isCut:
        model.optimize()
        isCut = vrp_cutgen(model)
        print("--- Running time: %s seconds ---" % (time.time() - start_time2))
     
    x = model.__data
    print("----------------------------------------------------------------")
    print("--- Cut Generation:")
    print("--- Running time: %s seconds ---" % (time.time() - start_time2))
    edges = represent(x)
    print ("Optimal solution:",model.ObjVal)
    print ("Edges in the solution:")
    print (sorted(edges))
    print ("Positive Vars: ")
    var_print(x)    
