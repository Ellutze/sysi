# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 13:17:56 2020

@author: jakub.kucera
"""
import win32com.client.dynamic
import numpy as np
from vecEX2_C import wrmmm

import os
import math
from vecEX2_C import wrmmm


#takes in a CATIA file and creates MD mesh input for braiding
# 1.shape needs to start at z=0
# 2.the shape need centreline starting at x=0,y=0
# 3.all geometries need to be hidden
# 4.the complete surface needs to be called "MainLoft"

def cat_mesh(span,part, XSeed, SPele):
    #inputs are the span lenght in mm, the name of CATIA file, number of nodes around cross-section, spanwise size of element
    CATIA = win32com.client.Dispatch("CATIA.Application")
    CATIA.RefreshDisplay = False
    lPath = os.path.dirname(os.path.abspath(__file__))
    
    '''
    #Location of CATIA file to be meshed.
    str15 = "CatiaFiles\\SourceFiles\\"+part+".CatPart"
    partDocument1 = CATIA.Documents.Open(str15)
    part1 = partDocument1.Part
    HSF1 = part1.HybridShapeFactory
    hbs1 = part1.HybridBodies
    
    #create geometry set for intersection and hide it
    hb1 = hbs1.Add()
    hb1.Name="ints"
    hb2 = hbs1.Add()
    hb2.Name="pts"
    hb3 = hbs1.Item("Surfaces")
    hs3 = hb3.HybridShapes
    hsl1 = hs3.Item("MainLoft")
    
    #hide
    selection1 = partDocument1.Selection
    visPropertySet1 = selection1.VisProperties
    selection1.Add(hb1)
    visPropertySet1 = visPropertySet1.Parent
    visPropertySet1.SetShow(1)
    selection1.Clear 
    '''
    
    #create MD numpy matrix
    ML = np.zeros([XSeed,4,1])
    
    #loop through matrix
    i = 0 
    sf = math.floor(span/SPele) + 1
    while i < sf:
        
        #Location of CATIA file to be meshed.
        str15 = lPath+"\\CatiaFiles\\SourceFiles\\"+part+".CatPart"
        partDocument1 = CATIA.Documents.Open(str15)
        part1 = partDocument1.Part
        HSF1 = part1.HybridShapeFactory
        hbs1 = part1.HybridBodies
        
        #create geometry set for intersection and hide it
        hb1 = hbs1.Add()
        hb1.Name="ints"
        hb2 = hbs1.Add()
        hb2.Name="pts"
        hb3 = hbs1.Item("Surfaces")
        hs3 = hb3.HybridShapes
        hsl1 = hs3.Item("MainLoft")
        
        #hide
        selection1 = partDocument1.Selection
        visPropertySet1 = selection1.VisProperties
        selection1.Add(hb1)
        visPropertySet1 = visPropertySet1.Parent
        visPropertySet1.SetShow(1)
        selection1.Clear 
        
        
        MS = np.zeros([XSeed,4,1])
        #make plane
        z = i*SPele
        originElements1 = part1.OriginElements
        PlaneExplicit1 = originElements1.PlaneXY
        ref1 = part1.CreateReferenceFromObject(PlaneExplicit1)
        offset1 = HSF1.AddNewPlaneOffset(ref1,z,False)
        hb1.AppendHybridShape(offset1)
    
            
        #make intersection
        ref1 = part1.CreateReferenceFromObject(offset1)
        ref2 = part1.CreateReferenceFromObject(hsl1)
        hsi1 = HSF1.AddNewIntersection(ref1,ref2)
        #hsi1.PointType = 0
        hb1.AppendHybridShape(hsi1)
        ref3 = part1.CreateReferenceFromObject(hsi1)
        
        #create a stable starting point on cross-sections
        cord1 = HSF1.AddNewPointCoord(0, 0, z)
        hb1.AppendHybridShape(cord1)
        cord2 = HSF1.AddNewPointCoord(0, 10000, z)
        hb1.AppendHybridShape(cord2)
        ref222 = part1.CreateReferenceFromObject(cord2)
        ref111 = part1.CreateReferenceFromObject(cord1)
        hslx = HSF1.AddNewLinePtPt(ref111, ref222)
        hb1.AppendHybridShape(hslx)
        ref122 = part1.CreatereferenceFromObject(hslx)
        hsi2 = HSF1.AddNewIntersection(ref3,ref122)
        hb1.AppendHybridShape(hsi2)
        ref78 = part1.CreatereferenceFromObject(hsi2)
        
        #hsd1 = HSF1.AddNewDirectionByCoord(1,2,3)
        #hse1 = HSF1.AddNewExtremum(ref3,hsd1,1)
        #hb1.AppendHybridShape(hse1)
        #ref4 = part1.CreateReferenceFromObject(hse1)
        
        ii = 0
        #loop through interssection
        while ii < XSeed:
            
            #make a point
            #hsd1 = HSF1.AddNewDirectionByCoord(1,2,3)
            #hse1 = HSF1.AddNewExtremum(ref3,hsd1,1)
            #hb1.AppendHybridShape(hse1)
            #ref4 = part1.CreateReferenceFromObject(hse1)
            
            
            poc1 = HSF1.AddNewPointOnCurveWithReferenceFromPercent(ref3,ref78,(ii/XSeed),False)
            hb2.AppendHybridShape(poc1)
            poc1.Name="MeshPoint"+str(ii+i*XSeed)
            
            #extract 3d coordinates
            part1.Update() 
            partDocument1.ExportData(lPath+"\\Temporary\\xxx.wrl", "wrl")
            #vector result:
            NS,f_pt1 = wrmmm()
            #print(f_pt1)
            MS[ii,1,0] = f_pt1[0,0]
            MS[ii,2,0] = f_pt1[0,1]
            MS[ii,3,0] = f_pt1[0,2]
            if i == 0:
                MS[ii,3,0] = 0
            
            #hide point
            selection1 = partDocument1.Selection
            visPropertySet1 = selection1.VisProperties
            selection1.Add(poc1)
            visPropertySet1 = visPropertySet1.Parent
            visPropertySet1.SetShow(1)
            selection1.Clear 
            
            ii = ii + 1
            
        #store 3D coordinates in MD 
        print(MS)
        ML = np.concatenate((ML,MS),axis = 2)  
        
        partDocument1.Close()

        i = i + 1
    #save mesh
    ML = np.delete(ML,0,axis=2)
    np.save('Temporary\\ex_mesh.npy', ML)
    #np.savetxt("Temporary\\test1.csv", ML, delimiter=",")
            
    return(ML)
    
#ML = cat_mesh(1500,"IDP_oscar_1904_A001_JK",20,20)