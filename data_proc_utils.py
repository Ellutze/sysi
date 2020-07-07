# -*- coding: utf-8 -*-
"""
Created on Tue May 12 11:16:17 2020

@author: jakub.kucera
"""
import numpy as np

def shuffle(matrix):
    sf = np.zeros([1,np.size(matrix,1)])
    #print(sf)
    sf[0,:] = matrix[0,:]
    #sf =matrix[0,:]
    i = 1
    while i < np.size(matrix,0):
        ii = np.random.randint(i+1)
        sf = np.insert(sf, ii, matrix[i,:], 0)  
        #print(sf)
        i = i + 1
    return(sf)
    
#a = np.matrix([[1,2,3],[4,5,6],[7,8,9]])
#a= shuffle(a)
#print(a)
        
    
from IDP_databases import cnt_X,dc_X
from python_mysql_dbconfig import read_db_config


def collector(tlist):
    #tlist lists the tables that are to be collected
    colis = []
    for number in tlist:
        #loop thorugh all tables, search for column names
        cnnT,crrT = cnt_X('NCC')
        query = """SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '_iters_"""+str(number)+"""' ORDER BY ORDINAL_POSITION"""
        crrT.execute(query)
        rows = crrT.fetchall()
        #for each column that was not listed (and does not correspond to default column), add to list
        for row in rows:
            if row[0] not in colis:
                colis.append(row[0])
        dc_X('NCC',cnnT,crrT)

    colis.remove('fitness')
    colis.remove('Specie')
    colis.remove('Generation')
    colis.remove('arunID')
    colis.remove('id')
    #print(colis)

    #make zeros line for the required number of vars + fitness + def + weight
    sz = len(colis) + 3
    dt = np.zeros([1,sz])

    #for each table
    for number in tlist:
        colisy = []
        colisx = colis.copy()
        #print(colisx)
        cnnT,crrT = cnt_X('NCC')
        query = """SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '_iters_"""+str(number)+"""' ORDER BY ORDINAL_POSITION"""
        crrT.execute(query)
        rows = crrT.fetchall()
        
        #for each column that was not listed (and does not correspond to default column), add to list
        query = "SELECT "
        for row in rows:
            if row[0] in colisx:
                #colisx will be the remaining entries that will be added from fixed variables table
                #colisy is the list of variables obtained here from the main table
                query += row[0]+","
                colisy.append(row[0])
                colisx.remove(row[0])

        query += """fitness,arunID FROM [DIGIProps].[dbo].[_iters_"""+str(number)+"""] where fitness > 0;"""
        crrT.execute(query)
        mt = crrT.fetchall()
        #mt is later used for construction of the overall table

        #obtain variables from fixed variables table
        if len(colisx) > 0:
            query = "SELECT "
            for i in colisx:
                query += str(i)+","
            query = query[:-1]
            query += """ From [DIGIProps].[dbo].[UserDefIterations] where ref_no = """+str(number)+""";"""
            crrT.execute(query)
            addx = crrT.fetchall()
            for a in addx:
                adx = a
                
        #populate each row of data from corresponding sources
        dtt = np.zeros([1,sz])
        for m in mt:
            i = 0
            while i < len(colis):
                ii = 0
                #from fixed variables table
                while ii < len(colisx):
                    if colis[i] == colisx[ii]:
                        dtt[0,i] = adx[ii]
                    ii = ii + 1
                ii = 0
                #from main table
                while ii < len(colisy):
                    if colis[i] == colisy[ii]:
                        dtt[0,i] = m[ii]
                    ii = ii + 1
                i = i + 1
                
            #add fitness
            fn = np.size(dtt,1)-3
            mn = len(m)-2
            dtt[0,fn] = m[mn]
            
            #find idArun
            mn = len(m)-1
            idArun = m[mn]
            
            #use the idArun to obtain the deconstructed fitness (mass, deflection)
            query = """SELECT FEfile FROM arun where idArun = """+str(idArun)+""";"""
            crrT.execute(query)
            FEfile = crrT.fetchall()
            for mu in FEfile:    
                mu1 = str(mu[0])
            query = """SELECT max_deflection, mass FROM fe_inst where FEfile = '"""+mu1+"""';"""
            #print(query)
            crrT.execute(query)
            fitComp = crrT.fetchall()  
            #print(fitComp)
            for nu in fitComp:
                #max_deflectoin
                dtt[0,np.size(dtt,1)-1] = nu[0]
                #mass
                dtt[0,np.size(dtt,1)-2] = nu[1]

            
            dt = np.concatenate((dt,dtt),axis=0)
            
        dc_X('NCC',cnnT,crrT)
    
    dt = np.delete(dt,0,axis=0)
    
    return(len(colis), dt, colis)
    
#collector([36,37])
    
def fit2(dt):
    #second fitness function
    i = 0
    while i < np.size(dt,0):
        #weight 
        w = dt[i,(np.size(dt,1)-2)]
        #deflection
        d = dt[i,(np.size(dt,1)-1)]
        
        #deflection has to be below 5, while additional weight costs exponentially
        if d > 5:
            dt[i,(np.size(dt,1)-3)] = 0
        else:
            dt[i,(np.size(dt,1)-3)] = (1 - 0.5*(d/10))*0.9**(w*10000)
        i = i + 1
    np.savetxt("Temporary\\testFIT2.csv", dt, delimiter=",")
    return(dt)
    
def fit3(dt):
    i = 0
    while i < np.size(dt,0):
        #weight 
        w = dt[i,(np.size(dt,1)-2)]
        #deflection
        d = dt[i,(np.size(dt,1)-1)]
        
        #deflection has to be below 5, while additional weight costs exponentially
        dt[i,(np.size(dt,1)-3)] = 0.5*(0.5**(w*20000))+0.5*(0.5**(d/10))#

        i = i + 1
    np.savetxt("Temporary\\testFIT3.csv", dt, delimiter=",")
    return(dt)    
        