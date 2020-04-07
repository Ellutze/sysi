# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 17:18:13 2020

@author: jakub.kucera
"""
import numpy as np
import os

def spheres(varVal):
    lPath = os.path.dirname(os.path.abspath(__file__))
    #this function records recommended spanwise mesh sizes, currently doesnt change, use the commented out section later for precise mesh spheres
    
    m = varVal["mesh_size"]
    s = varVal["span"]
    i = 0
    MD = np.zeros([1,2])
    while i <= s:
        temp = np.matrix([[i,m]])
        MD = np.concatenate((MD,temp),axis=0)
        i = i + m
    MD = np.delete(MD,0,axis=0)
    #print(MD)
    np.save(lPath+'\\Temporary\\for_spheres', MD)
    
    '''
    conn,cursor = cnt_X('NCC')
    
    #replace max(half_span) by half_span and create a matrix
    
    query = "SELECT half_span,chord_length FROM "+CADfile
    print(query)
    cursor.execute(query)
    #get results
    sd = np.zeros([1,2])
    sdTemp = np.zeros([1,2])
    rows = cursor.fetchall()
    for row in rows:
        sdTemp[0,0] = float(row[0])
        sdTemp[0,1] = float(row[1])
        sd = np.concatenate((sd,sdTemp),axis=0)
    sd = np.delete(sd, (0), axis=0)
    dc_X('NCC',conn,cursor)
    
    meshMAT = np.matrix([float(0),spn])
    meshMATtemp = np.matrix([float(0),float(0)])
    
    i = 1
    ii = 0
    while i < sd.shape[0]:
        z1 = sd[i-1,0]
        z2 = sd[i,0]
        ratELE = sd[i,1]/sd[i-1,1]
        maxELE = meshMAT[ii,1]
        minELE = ratELE*maxELE
        z = (meshMAT[ii,0])
        i = i + 1
        while z < z2:
            ii = ii + 1
            meshMATtemp[0,1] = ((z-z1)/(z2-z1))*(minELE-maxELE)+maxELE
            meshMATtemp[0,0] = meshMAT[ii-1,0] + meshMATtemp[0,1]
            meshMAT = np.concatenate((meshMAT,meshMATtemp),axis=0)
            z = meshMATtemp[0,0]
        
    #the distance of the far edge of last element from the part edge
    diff1 = abs(meshMAT[meshMAT.shape[0]-1,0]-sd[sd.shape[0]-1,0])
    #distance of the second last element edge from the part edge
    diff2 = abs(meshMAT[meshMAT.shape[0]-2,0]-sd[sd.shape[0]-1,0])
    
    if diff1 < diff2:
        #shorten the last element and ammend the size 
        meshMAT[(meshMAT.shape[0]-1),0] = sd[sd.shape[0]-1,0]
        meshMAT[(meshMAT.shape[0]-1),1] = meshMAT[(meshMAT.shape[0]-1),1] #-diff1 purposefully letting the element size be larger helps assign properties
    else:
        #the element length of the two sections needs to be added - excess
        meshMAT[(meshMAT.shape[0]-2),1] = meshMAT[(meshMAT.shape[0]-1),1]+meshMAT[(meshMAT.shape[0]-2),1]-diff1
        
        meshMAT = np.delete(meshMAT, (meshMAT.shape[0]-1), axis=0)
        meshMAT[(meshMAT.shape[0]-1),0] = sd[sd.shape[0]-1,0]
        
    MD = meshMAT
    #count spanwise elements : cse
    cse = np.size(MD,0)
        #for each of the sections
        
        #calculate the end section size of element
        #find average element size in the section
        #iterate through elements, new element size is the local ratio from max to min

    #the meshing functions:~~~~~~~~~~~~ replace this 
    #MD = catia_mesh.paraRedef(md,sd)
    
    
    part1, HSF1, partDocument1 = catia_mesh.openPart(CADfile)  
    catia_mesh.planes(part1, HSF1,MD,rnc)   
    catia_mesh.insects(part1,HSF1,MD,rnc)
    catia_mesh.pts(part1,HSF1,MD,rnc)
    catia_mesh.cnxl(part1,HSF1,MD,rnc)
    catia_mesh.sweep(part1,HSF1,MD,rnc)
    
    np.save('D:\\IDPcode\\Temporary\\for_spheres', MD)
    '''
    
#from default_var_dict import getBase
#
#varVal, varMin,varMax = getBase()
#spheres(varVal)