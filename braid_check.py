# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 14:53:57 2020

@author: jakub.kucera
"""
import time
import numpy as np

import win32com.client.dynamic
from IDP_databases import cnt_X,dc_X
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config




st42 = time.time()  
#BP = np.zeros([spoolsWa,iters],dtype=object)

CATIA = win32com.client.Dispatch("CATIA.Application")
CATIA.RefreshDisplay = False
#documents1 = CATIA.Documents # this line is not currently in use
cadFile = "IDP_spar_A758_JK"
braidFile = "IDP_spar_A758_B001"

#location of CATIA file to be meshed
#delete after testing:
#BraidFile = CADfile.replace("_A0", "_B0") 
str15 = "D:\\sysi\\catiafiles\\sourcefiles\\"+cadFile+".CatPart"
partDocument1 = CATIA.Documents.Open(str15)
part1 = partDocument1.Part
HSF = part1.HybridShapeFactory
hbs = part1.HybridBodies


    
hb1 = hbs.Add()


hb1.Name="spools"
hb1 = hbs.Add()
hb2 = hbs.Add()
hb2.Name="pocs"
hb2 = hbs.Add()

hb3 = hbs.Item("Surfaces")
hs3 = hb3.HybridShapes
hsl1 = hs3.Item("MainLoft")

cnnB,crrB = cnt_X('NCC')
query = """SELECT yarn,x,y,z FROM """+braidFile+""";"""
crrB.execute(query)
rows = crrB.fetchall()
#close SQL handles 
dc_X('NCC',cnnB,crrB)

hss1 = ""
BP = []
yarn = 0
hss1 = HSF.AddNewSpline()
hss1.SetSplineType(0)
hss1.SetClosing(0)
ref1 = part1.CreateReferenceFromObject(hsl1)
hss1.SetSupport(ref1)
count = 0
for row in rows:
    
    if count < 2:
        BP.append(row)
        yr = int(row[0])
        if yarn < yr:
            if yarn > 0:
                hb1.AppendHybridShape(hss1)
                count = count + 1
                print(count)
            yarn = yr
            hss1 = HSF.AddNewSpline()
            hss1.SetSplineType(0)
            hss1.SetClosing(0)
            ref1 = part1.CreateReferenceFromObject(hsl1)
            hss1.SetSupport(ref1)
        
        x = row[1]
        y = row[2]
        z = row[3]
            
        cord1 = HSF.AddNewPointCoord(x, y, z)
        hb2.AppendHybridShape(cord1)
        ref2 = part1.CreateReferenceFromObject(cord1)
        hss1.AddPointWithConstraintExplicit(ref2,None,-1,1,None,0)

hb2.AppendHybridShape(hss1)


import os

lPath = os.path.dirname(os.path.abspath(__file__))

#np import spheres
II = np.load(lPath+'\\catiafiles\\meshfiles\\IDP_spar_A758_N001_nodes.npy')
print(II)
hb91 = hbs.Add()
hb91.Name="mesh"
hb91 = hbs.Add()
#hb91 = hbs.Item("xxx")
i = 0
while i < np.size(II,0):
    ii = 0
    while ii < np.size(II,2):
        #CATIA FOR TESTING
        hybridShapePointCoord1 = HSF.AddNewPointCoord(II[i,1,ii],II[i,2,ii],II[i,3,ii])
        hb91.AppendHybridShape(hybridShapePointCoord1)
        ii = ii + 1
    i = i + 1


'''
hb11 = hbs.Add()
hb11.Name="SPP"
hb22 = hbs.Add()
hb22.Name="poc1"
hb = hbs.Add()
hb.Name="connections"
p = np.load(lPath+'\\temporary\\1yarn0.npy')
i = 0
while i < np.size(p,0):
    cord1 = HSF.AddNewPointCoord(p[i,0], p[i,1], p[i,2])
    hb11.AppendHybridShape(cord1)
    cord2 = HSF.AddNewPointCoord(p[i,3], p[i,4], p[i,5])
    hb22.AppendHybridShape(cord2)    
    ref2 = part1.CreateReferenceFromObject(cord1)
    ref1 = part1.CreateReferenceFromObject(cord2)
    hslx = HSF.AddNewLinePtPt(ref1, ref2)
    hb.AppendHybridShape(hslx)
    i = i + 1

'''
part1.Update 



SplineFile = braidFile.replace("_A", "_S")     
silo = "D:\\sysi\\CatiaFiles\\BraidFiles\\"+SplineFile+"_JK.CatPart"
partDocument1.SaveAs(silo)

CATIA.RefreshDisplay = True
print("Time to create splines:--- %s seconds ---" % (time.time() - st42))