import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QFormLayout, QLineEdit, QTableWidget, QTableWidgetItem,QLabel,QComboBox,QVBoxLayout,QGridLayout
)
np.set_printoptions(suppress=True)
# def pls(A: np.array ,q,b):
#     l,c=A.shape
#     for i in  range(l):
#         for j in range(c) :
#             print(A[i][j],end=" ")
#         if q[i]==-1 :print("-e",i+1,"=",b[i])
#         elif q[i]==1 :print("e",i+1,"=",b[i])
#         else  : print("=",b[i])
def Sim_tab(A,q,b,func_obj) :
    l,c = A.shape
    labels = ["X"+str(i+1) for i in range(c)]
    lab_art = []
    vbl = []
    # si cpt=0 --> pas de variable artificielle :si cpt=n --> il ya n variables artificielles 
    cpt = 0
    sim_tab = A
    Zartif=[]
    for  i in range(l):
        # contrainte ou il ya <=
        if q[i] == 1 :
            colonne=np.zeros((l,1))
            colonne[i] = 1
            sim_tab=np.append(sim_tab,colonne,axis=1)
            labels.append("e"+str(i+1))
            vbl.append("e"+str(i+1))
        #contrainte ou il ya >=
        elif q[i]==-1 :
            colonne=np.zeros((l,1))
            colonne[i]=-1
            sim_tab=np.append(sim_tab,colonne,axis=1)
            if cpt==0:
                var_artif=-colonne
            elif cpt>0:
                var_artif=np.append(var_artif,-colonne,axis=1)
            labels.append("e"+str(i+1))
            lab_art.append("a"+str(i+1))
            vbl.append("a"+str(i+1))
            Zartif.append(1)
            cpt+=1
        # contrainte ou il ya =
        elif q[i]==0 :
            colonne=np.zeros((l,1))
            colonne[i]=1
            if cpt==0:
                var_artif=colonne
            if cpt>0:
                var_artif=np.append(var_artif,colonne,axis=1)
            cpt+=1
            lab_art.append("a"+str(i+1))
            vbl.append("a"+str(i+1))
            Zartif.append(1)
    # si cpt=1 --> pas de variable artificielle :si cpt=0 --> il ya ou moins une variable artificielle 
    if cpt>=1 :
        Zartif.append(0)
        sim_tab=np.append(sim_tab,var_artif,axis=1)
        sim_tab=np.append(sim_tab,b.reshape(-1,1),axis=1)
        Za=np.zeros(sim_tab.shape[1]-cpt-1)
        Za=np.append(Za,np.array(Zartif))
        sim_tab=np.append(sim_tab,[Za],axis=0)
        z=np.array(func_obj)
        z=np.append(z,np.zeros(sim_tab.shape[1]-c))
        sim_tab=np.append(sim_tab,[z],axis=0)
        vbl.append("Za")
    elif cpt==0:
        sim_tab=np.append(sim_tab,b.reshape(-1,1),axis=1)
        z=np.array(func_obj)
        z=np.append(z,np.zeros(l+1))
        sim_tab=np.append(sim_tab,[z],axis=0)
    vbl.append("Z")
    labels+=lab_art+["b"]
    #np.append(sim_tab,b,axis=1)
    return sim_tab,labels,vbl,cpt

def phase1(sim_tab,labels,vbl,grid,pyqt=False):
    print(sim_tab)
    print(vbl)
    print(labels)
    #correction du tableau
    l,c=sim_tab.shape
    v_art_indices=np.where(sim_tab[l-2]==1)
    for i in v_art_indices[0] :
        # print(i)
        j=np.where(sim_tab[:,i]==1)[0][0]
        # print(j)
        sim_tab[l-2]=sim_tab[l-2]-sim_tab[j]
    while True :    
        QputNparray(grid,sim_tab,vbl,labels)
        data=pd.DataFrame(data=sim_tab,columns=labels,index=vbl)
        print(data)
        piv=find_pivot(sim_tab[:l-1,],MinMax=-1)
        if piv==None: 
            print("final table")
            break
        if piv==False :
            print("no bornée")
            break
        i,j=piv
        vbl[i]=labels[j]
        print(i,j)
        pivoter(sim_tab,i,j)


def phase2(sim_tab,MinMax,labels,vbl,grid):
    while(True):
        QputNparray(grid,sim_tab,vbl,labels)
        data=pd.DataFrame(data=sim_tab,columns=labels,index=vbl)
        print(data)
        piv=find_pivot(sim_tab,MinMax)
        if piv==None: 
            print("final table")
            break
        if piv==False :
            print("no bornée")
            break
        i,j=find_pivot(sim_tab,MinMax)
        vbl[i]=labels[j]
        print(i,j)
        pivoter(sim_tab,i,j)
#minmax=1 probleme de maximisation minmax=-1 probleme de minimisation
def find_pivot(sim_tab,MinMax=1) :
    l,c=sim_tab.shape
    if MinMax==1:
        #indice du colonne du variable avec le plus grand positive cout 
        v_entrant= np.where(sim_tab[l-1]==max(sim_tab[l-1,:c-1]))[0][0]
        if sim_tab[l-1][v_entrant]<=0:return None #optimal
    elif MinMax==-1 :
        v_entrant= np.where(sim_tab[l-1]==min(sim_tab[l-1,:c-1]))[0][0]
        if sim_tab[l-1][v_entrant]>=0:return None #optimal

    #indice du ligne du variable avec le plus petit positive ratio
    ratio=np.inf
    v_sortant=0
    # v_sortant_bool false --> on a pas trouver aucun variable sortant
    v_sortant_bool=False
    for i in range(l-1):
        if sim_tab[i][v_entrant]<=0 : continue
        if ratio > sim_tab[i][c-1]/sim_tab[i][v_entrant] :
            ratio=sim_tab[i][c-1]/sim_tab[i][v_entrant]
            v_sortant=i
            v_sortant_bool=True
    if v_sortant_bool :
        return v_sortant,v_entrant
    else :
        return False

def pivoter(sim_tab,i,j):
    l,c=sim_tab.shape
    pivot=sim_tab[i][j]
    #a[i][j] -= a[p][j] * a[i][q] / a[p][q];
    for r in range(l):
        for k in range(c):
            if i!=r and k!=j :
                #print("in")
                #print(sim_tab[r][k]-(sim_tab[i][k]*sim_tab[r][j])/pivot)
                sim_tab[r][k]=sim_tab[r][k]-(sim_tab[i][k]*sim_tab[r][j])/pivot
    
    #dans le colonne du pivot tous les son null 
    sim_tab[0:i,j]=0
    sim_tab[i+1:,j]=0
    #dans la ligne du pivot par sa valeur
    sim_tab[i]=sim_tab[i]/pivot
    sim_tab[i][j]=1
        
        
def simplexe(A,q,b,func_obj,MinMax,grid,pyqt=False):
    sim_tab,labels,vbl,cpt=Sim_tab(A,q,b,func_obj)
    if cpt==0 :
        phase2(sim_tab,MinMax,labels,vbl,grid)
    elif cpt>0:
        phase1(sim_tab,labels,vbl,grid,pyqt)
        if solutionexist(vbl):
            print("il ya une solution")        
            sim_tab=np.delete(sim_tab,-2,axis=0)
            vbl.remove("Za")
            k=0
            while(labels[k]!="b"):
                if labels[k].startswith('a'):
                    labels.pop(k)
                    sim_tab=np.delete(sim_tab,k,axis=1)
                else :
                    k+=1     
            print(sim_tab.shape)       
            data=pd.DataFrame(sim_tab,columns=labels,index=vbl)
            print(data)
            #PHASE II
            print('DEBUT DE PHASE II')
            phase2(sim_tab,MinMax,labels,vbl,grid)
        else : 
            print('pas de solution')
def QputNparray(grid,npArr,Vheaders,Hheaders):
    num_rows,num_cols=npArr.shape
    table=QTableWidget()
    # Set the number of rows and columns in the table
    table.setRowCount(num_rows)
    table.setColumnCount(num_cols)

    # Set the column and row names
    table.setHorizontalHeaderLabels(Hheaders)
    table.setVerticalHeaderLabels(Vheaders)

# Populate the table with the values from the NumPy array
    for k in range(num_rows) :
        for l in range(num_cols) :
            item = QTableWidgetItem(str(npArr[k, l]))
            table.setItem(k, l, item)
    grid.addWidget(table)

def solutionexist(vbl):
    exist = True
    for i in vbl :
        if i.startswith('a'): return False
    return True