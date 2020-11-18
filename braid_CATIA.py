# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 10:13:55 2020

@author: jakub.kucera
"""
from mesh_anyshape import cat_mesh
from Braid_CMD_S import baseBraid
import win32com.client.dynamic
import numpy as np
import time


#takes in a CATIA file and creates MD mesh input for braiding
# 1.shape needs to start at z=0
# 2.the shape need centreline starting at x=0,y=0
# 3.all geometries need to be hidden
# 4.the complete surface needs to be called "MainLoft"

def b_master(part,varVal):
    #inputs are the CATIA file, "varVal", ...
    
    mesh = varVal["mesh_size"]
    span = varVal["span"]
    ML = cat_mesh(span,part,60,mesh)
    
    noSQL = baseBraid(varVal,part,ML)
    
    st42 = time.time() 
    CATIA = win32com.client.Dispatch("CATIA.Application")
    CATIA.RefreshDisplay = False 
    str15 = "D:\\sysi\\catiafiles\\sourcefiles\\"+part+".CatPart"
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
    
    
    hss1 = ""
    BP = []
    yarn = 0
    hss1 = HSF.AddNewSpline()
    hss1.SetSplineType(0)
    hss1.SetClosing(0)
    ref1 = part1.CreateReferenceFromObject(hsl1)
    hss1.SetSupport(ref1)
    count = 0
    for row in noSQL:
        
        if count < 9:
            BP.append(row)
            yr = int(row[0,0])
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
            
            x = row[0,1]
            y = row[0,2]
            z = row[0,3]
                
            cord1 = HSF.AddNewPointCoord(x, y, z)
            hb2.AppendHybridShape(cord1)
            ref2 = part1.CreateReferenceFromObject(cord1)
            hss1.AddPointWithConstraintExplicit(ref2,None,-1,1,None,0)
    
    hb2.AppendHybridShape(hss1)
    
    
    import os
    
    lPath = os.path.dirname(os.path.abspath(__file__))
    part1.Update 
      
    SplineFile = part+"_B_S"   
    silo = lPath+"\\CatiaFiles\\BraidFiles\\"+SplineFile+"_JK.CatPart"
    partDocument1.SaveAs(silo)
    
    CATIA.RefreshDisplay = True
    print("Time to create splines:--- %s seconds ---" % (time.time() - st42))
    

varVal = {'span': 200,'mesh_size':0.8,'spools':16,'mandrel_speed':1.2,'guide_rad':700,'IMD':5}
b_master("_test_A005_JK",varVal)