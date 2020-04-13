# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 13:56:01 2020

@author: jakub.kucera
"""
from default_var_dict import getBase
import numpy as np
import math
import IDP_geometry
import time
from IDP_databases import cnt_X, dc_X
import os

def braidAngle(NS,t,f):
    #Uses vectorised formulas to obtain local braid angle - Johan Van.Ravenhorst thesis reference ....
    #Turn into unit vectors
    tmag = (t[0]**2 +t[1]**2 +t[2]**2)**(1/2)
    NSmag =(NS[0]**2 +NS[1]**2 +NS[2]**2)**(1/2)
    #error handling
    if NSmag == 0:
        print("vector can not have 0 length, this is MADNESS!")
        exit()
    fmag =  (f[0]**2 +f[1]**2 +f[2]**2)**(1/2)
    f = f/fmag
    t = t/tmag
    NS = NS/NSmag
    #syntax issues resolution...
    tFD = [t[0],t[0],t[2]]
    NSfd =[NS[0],NS[1],NS[2]]
    i = t-(np.dot(tFD,NSfd)*NS)
    imag = (i[0]**2 +i[1]**2 +i[2]**2)**(1/2)
    i = i/imag

    j = np.cross(NS,i)
    jmag =(j[0]**2 +j[1]**2 +j[2]**2)**(1/2)
    j = j/jmag
    
    alpha = math.atan(np.dot(f,j)/np.dot(f,i))
    #into degrees for convenience
    alphad = alpha*180/math.pi
    #print(alphad)
    return(i,alphad)

def findClosest(MD,count,seg,poc1,forDelete = []):
    #find closest specified number of points
    #Done by 3D pythagoras 
    MD1 = np.copy(MD)    
    
    #forDelete = np.matrix([[1,0,0]])
    try:
        magd = forDelete[0]**2+forDelete[1]**2+forDelete[2]**2
    except:
        magd = 0
    
    if magd != 0:
        #look through MD1 to delete 
        iii = 0
        while iii < np.size(MD1,0):
            if MD1[iii,1,seg] == forDelete[0] and MD1[iii,2,seg] == forDelete[1] and MD1[iii,3,seg] == forDelete[2]:
                MD1 = np.delete(MD1,iii,axis=0)
                iii = np.size(MD1,0)+1
            iii = iii +1

    ii = 0
    CP0 = np.zeros([count,3])
    #for each point required
    while ii < count:
        i = 0
        c = 1000000
        #loop through all points available
        while i < np.size(MD1,0):
            #calculate the distance between point and reference point
            dl = np.sqrt((poc1[0]-MD1[i,1,seg])**2+(poc1[1]-MD1[i,2,seg])**2+(poc1[2]-MD1[i,3,seg])**2)
            #if no closer point was found yet, insert it into the CP matrix
            if dl < c: #preventing assignment of two fo the same
                CP0[ii,:] = np.matrix([MD1[i,1,seg],MD1[i,2,seg],MD1[i,3,seg]])
                c = dl
                ref = i
            i = i + 1
        ii = ii + 1
        MD1 = np.delete(MD1,ref,axis=0)
    return(CP0)

def noSerpent(T,YARN,maxR,gd,WW,rota,spoolsWa,MS,imd,datum):
    #find d (spool point)
    stangle = math.acos(maxR/gd)

    #warp weft, or the other way around
    if WW == 0:
        ww = 1
    else:
        ww = -1
        
    #first point position
    #This is estimate of where the spool might be at the start of braid, would need to be changed to simulate the initial stabilization of braid
    fpp = -45*math.pi/180
    #rotation due to iteration + intial position based on Yarn number + arbitrary starting position for the spool
    ang_travel = (ww*T*rota+(ww*YARN/spoolsWa)*2*math.pi+stangle*ww+fpp) % (2*math.pi) #0.25 before...
    
    #circular position calculation
    #North is the starting position
    x = gd*math.sin(ang_travel)
    y = gd*math.cos(ang_travel)
    #position of circle in refernce to 0,0,0 (mandrel datum)
    z = T*MS + imd
    f_pt2 = (x,y,z)
    SPP = f_pt2 + datum
    return(SPP)

def poc(MD,varVal,YARN,WW,spoolsWa,spoolsPhy,datum,cdArr,CADfile,rota):
    lPath = os.path.dirname(os.path.abspath(__file__))
    st2 = time.time()  
    #change for iteration

    #POC1 find, fell point
    csL = 0
    csl_mat = [0]
    i = 0 
    #perimeter calculations
    while i < np.size(MD,0):
        if i == (np.size(MD,0)-1):
            localLen = np.sqrt((MD[i,1,0]-MD[0,1,0])**2 + (MD[i,2,0]-MD[0,2,0])**2)
        else:
            localLen = np.sqrt((MD[i,1,0]-MD[i+1,1,0])**2 + (MD[i,2,0]-MD[i+1,2,0])**2)
        csL = csL + localLen
        csl_mat.append(csL)
        i = i + 1
    
    #store perimeter as it is used in other scripts as well
    if YARN == 0:
            cnnB,crrB = cnt_X('NCC')
            query = """UPDATE arun SET root_perimeter = '"""+str(csL)+\
                    """' WHERE CADfile = '"""+CADfile+"""';"""
            crrB.execute(query)
            cnnB.commit()
            #close SQL handles 
            dc_X('NCC',cnnB,crrB)
            
    #initial position depends on yarn type Weft/warp, one is iterated clockwise one anti clockwise
    if WW == 0:
        pos = ((YARN/spoolsWa))*csL
        
    else:
        pos = (1-(YARN/spoolsWa))*csL
    #find between which two points on the perimeter is the current position
    i  = 0 
    while i < np.size(csl_mat):
        if csl_mat[i] <= pos <= csl_mat[i+1]:
            cc  = i
            i = i + 1000000
        i = i + 1
    
    #how far from one point to the other is the current position
    ratio = (pos-csl_mat[cc])/(csl_mat[cc+1]-csl_mat[cc])
    #Exception for lenght calculation for the last point on circumference,
    #as this point follows to the first point of circumference.
    if cc != (np.size(MD,0)-1):
        x = (MD[cc+1,1,0] - MD[cc,1,0])*ratio + MD[cc,1,0]
        y = (MD[cc+1,2,0] - MD[cc,2,0])*ratio + MD[cc,2,0]
        z = 0
    else: 
        x = (MD[0,1,0] - MD[cc,1,0])*ratio + MD[cc,1,0]
        y = (MD[0,2,0] - MD[cc,2,0])*ratio + MD[cc,2,0]
        z = 0
    poc1 = np.array([x,y,z])
    
    #initiates matrix for collection of all fell-points
    pocList= np.matrix([[YARN,poc1[0],poc1[1],poc1[2],0,0,0,0,0,0]])
    
    #useful variables 
    maxR = 21
    gd = varVal["guide_rad"]
    MS = varVal["mandrel_speed"]
    imd = varVal["IMD"]
    
    datum = np.array([datum[0,0],datum[0,1],datum[0,2]])
       
    #for iterations:
    snip = 0.05 #looking for point on on elements sides with these increments
    T= 0
    #timewise propagation
    Tstep = 1
    z = 0  
    seg = 0
    SPP = noSerpent(T,YARN,maxR,gd,WW,rota,spoolsWa,MS,imd,datum)
    sppList= np.matrix([[SPP[0],SPP[1],SPP[2]]])

    #Finding initial element by 4 points.
    CP0 = findClosest(MD,2,0,poc1)
    CP1 = findClosest(MD,2,1,poc1)        
    #Find nearest points at local z:
    #pt1 is further away from SPP
    #pt2 is closer to SPP
    p1d = np.sqrt((SPP[0]-CP0[0,0])**2+(SPP[1]-CP0[0,1])**2+(SPP[2]-CP0[0,2])**2)
    p2d = np.sqrt((SPP[0]-CP0[1,0])**2+(SPP[1]-CP0[1,1])**2+(SPP[2]-CP0[1,2])**2)
    if p1d > p2d:
        p1 = CP0[0,:]
        p2 = CP0[1,:]
    else:
        p1 = CP0[1,:]
        p2 = CP0[0,:]
        
    #find nearest points at z + mesh 
    #pt3 is further away from spp
    #pt4 is closer to spp
    p3d = np.sqrt((SPP[0]-CP1[0,0])**2+(SPP[1]-CP1[0,1])**2+(SPP[2]-CP1[0,2])**2)
    p4d = np.sqrt((SPP[0]-CP1[1,0])**2+(SPP[1]-CP1[1,1])**2+(SPP[2]-CP1[1,2])**2)
    if p3d > p4d:
        p3 = CP1[0,:]
        p4 = CP1[1,:]
    else:
        p3 = CP1[1,:]
        p4 = CP1[0,:]  
    
    #Main iteration
    while seg < np.size(MD,2)-2:
        #find current position of spool
        SPP = noSerpent(T,YARN,maxR,gd,WW,rota,spoolsWa,MS,imd,datum)
            
        #find normal to points 2,3,4
        l1 = p4 - p3
        l2 = p4 - p2 
        normal = np.cross(l1,l2)
        #turn into unit vector
        n_mag = np.sqrt((normal[0])**2+(normal[1])**2+(normal[2])**2)
        if n_mag == 0:
            print("normal broken, two of the same point used")
            print("p1",p1)
            print("p2",p2)
            print("p3",p3)
            print("p4",p4)
            print("bn",bn)
            #try to increase the search for cross section point by 1 #currently unverified method
            if p1[0]==p2[0] and p1[1]==p2[1]:
                #note findClosest now searches for 4 closest points
                CPX = findClosest(MD,4,seg,p1)
                dt = 9999999999
                i = 0
                while i < np.size(CPX,0):
                    pt = np.array([CPX[i,0],CPX[i,1],CPX[i,2]])
                    dist = np.sqrt((SPP[0]-pt[0])**2+(SPP[1]-pt[1])**2+(SPP[2]-pt[2])**2)
                    if dist < dt:
                        p2 = np.copy(pt)
                        dt = dist
                    i = i + 1
            #prints out the fix, so that user can check if it worked
            print("pt2",p2, "fixed?")
            if p3[0]==p4[0] and p3[1]==p4[1]:
                CPX = findClosest(MD,4,seg,p3)
                dt = 9999999999
                i = 0
                while i < np.size(CPX,0):
                    pt = np.array([CPX[i,0],CPX[i,1],CPX[i,2]])
                    dist = np.sqrt((SPP[0]-pt[0])**2+(SPP[1]-pt[1])**2+(SPP[2]-pt[2])**2)
                    if dist < dt:
                        p4 = np.copy(pt)
                        dt = dist
                    i = i + 1    
            #prints out the fix, so that user can check if it worked
            print("pt4",p4, "fixed?")
            l1 = p4 - p3
            l2 = p4 - p2 
            normal = np.cross(l1,l2)
            #turn into unit vector
            n_mag = np.sqrt((normal[0])**2+(normal[1])**2+(normal[2])**2)
        
        #Turn normal into unit vector
        normal = normal/n_mag
        
        #check that vector is pointing away from the origin (assumed at datum)
        check_point = p4 + normal
        point_d = np.sqrt((p4[0]-datum[0])**2+(p4[1]-datum[1])**2+(p4[2]-datum[2])**2)
        check_point_d = np.sqrt((check_point[0]-datum[0])**2+(check_point[1]-datum[1])**2+(check_point[2]-datum[2])**2)
        if point_d > check_point_d:
            normal = normal * -1 
            #making sure normal points away from datum
            
        pocList[np.size(pocList,0)-1,4:7] = normal
            
        #find if spp is above or below plane
        tst = np.dot(normal,(SPP-p4))
 
        #for now normals dont have z element.... shall see what happesn
        normalX = np.copy(normal)
        #normalX[2] = 0
        ui = 0
        #if the spool point is above the element plane, move spool until
        #it gets below the plane. Then itera through elements again.
        while tst > 0:
            normal[2] = 0
            T = T + Tstep
            SPP = noSerpent(T,YARN,maxR,gd,WW,rota,spoolsWa,MS,imd,datum)
            #move spool (by rotation and mandrel speed)
            #find if spp is above or below plane
            tst = np.dot(normalX,(SPP-p4))
                #tst    dot(normal,(spp-p0)) -- where p0 is p4
            ui = ui + 1
            if ui > 100:
                #When the spool didn't get over horizon in 100 spools moves.
                #Prints for troubleshooting. Does not force break of sim.
                #normal[2] = 0
                print("SPP",SPP)
                print("Houston, we have a problem")
                print("p1",p1,"p2",p2,"p3",p3,"p4",p4)
                print(bn)
        #now that tst < 0
        l1_mag = np.sqrt((l1[0])**2+(l1[1])**2+(l1[2])**2)
        l1 = l1/l1_mag
        l2_mag = np.sqrt((l2[0])**2+(l2[1])**2+(l2[2])**2)
        l2 = l2/l2_mag
        

        
        #find the shortest yarn path between poc1 and spp
        mD = 999999999
        prop = np.array([0,0,0])
        i = 0
        bn = 0
        #l1 = pt4-pt3
        #itereate through first element line
        while i <=l1_mag:
            ptx = p3+(l1*i)
            #compute distance point to spp and point to poc
            X1 = np.sqrt((SPP[0]-ptx[0])**2+(SPP[1]-ptx[1])**2+(SPP[2]-ptx[2])**2)
            X2 = np.sqrt((poc1[0]-ptx[0])**2+(poc1[1]-ptx[1])**2+(poc1[2]-ptx[2])**2)
            X = X1 + X2 
            #if this is shortest distance so far, store location
            if X < mD:
                mD = X
                prop = ptx
            i = i + snip
        i = 0
        
        #l2 = pt4-pt2
        #iterate through second element line
        while i <=l2_mag:
            ptx = p2+(l2*i)
            #compute distance point to spp and point to poc
            X1 = np.sqrt((SPP[0]-ptx[0])**2+(SPP[1]-ptx[1])**2+(SPP[2]-ptx[2])**2)
            X2 = np.sqrt((poc1[0]-ptx[0])**2+(poc1[1]-ptx[1])**2+(poc1[2]-ptx[2])**2)
            X = X1 + X2 
            #if this is shortest distance so far, store location
            if X < mD:
                mD = X 
                prop = ptx
                bn = 1
            i = i + snip
        
        poc1 = prop
        #propagate points (p1,p2,p3,p4)
        #refer to sketch for point propagation. TBD
        if bn == 0:
            #propagation spanwise
            seg = seg+1
            p1 = np.copy(p3)
            p2 = np.copy(p4)
            
            dt = 0

            CPX = findClosest(MD,1,seg+1,p1)
            p3 = np.array([CPX[0,0],CPX[0,1],CPX[0,2]])

            CPX = findClosest(MD,1,seg+1,p2)
            p4 = np.array([CPX[0,0],CPX[0,1],CPX[0,2]])
       
        else:
            #propagation along cross-section
            p1 = np.copy(p2)
            p3 = np.copy(p4)
            #implementing optional deletion , check if works
            CPX = findClosest(MD,3,seg,p1,p1)
            dt = 9999999999
            i = 0
            while i < np.size(CPX,0):
                pt = np.array([CPX[i,0],CPX[i,1],CPX[i,2]])
                dist = np.sqrt((SPP[0]-pt[0])**2+(SPP[1]-pt[1])**2+(SPP[2]-pt[2])**2)
                if dist < dt:
                    p2 = np.copy(pt)
                    dt = dist
                i = i + 1
            #implementing optional deletion , check if works
            CPX = findClosest(MD,3,seg+1,p3,p3)
            dt = 9999999999
            i = 0
            while i < np.size(CPX,0):
                pt = np.array([CPX[i,0],CPX[i,1],CPX[i,2]])
                dist = np.sqrt((SPP[0]-pt[0])**2+(SPP[1]-pt[1])**2+(SPP[2]-pt[2])**2)
                if dist < dt:
                    p4 = np.copy(pt)
                    dt = dist
                i = i + 1

        #find normal to points 2,3,4
        l1 = p4 - p3
        l2 = p4 - p2 
        normal1 = np.cross(l1,l2)
        #turn into unit vector
        n_mag = np.sqrt((normal1[0])**2+(normal1[1])**2+(normal1[2])**2)
        normal1 = normal1/n_mag
            
        #get f, yarn vector
        f = SPP -poc1
        
        #get t, vector along centreline
        t = []
        i = 0
        while i < np.size(cdArr,0)-1:
            if cdArr[i,3] <= z <= cdArr[i+1,3]:
                t = [cdArr[i,0],cdArr[i,1],cdArr[i,2]]
                i = i + 999999999
            i = i + 1
        
        #find the local braid angle
        iv, a = braidAngle(normal,t,f)
        #find the local pitch
        pitch = IDP_geometry.pitch(a,MD,z,spoolsPhy)
        pocList[np.size(pocList,0)-1,7] = a
        pocList[np.size(pocList,0)-1,9] = pitch
            
        pocList = np.concatenate((pocList,np.matrix([[YARN,poc1[0],poc1[1],poc1[2],0,0,0,0,T,0]])),axis=0)
        sppList = np.concatenate((sppList,np.matrix([[SPP[0],SPP[1],SPP[2]]])))
        #append to list of pocs
        
        z = poc1[2]
    
        #seg = seg + 1
    #save the list of pocs as numpy for testing 

    #Final braid angle computation
    #get f  
    f = SPP -poc1
    #get t
    t = []
    i = 0
    while i < np.size(cdArr,0)-1:
        if cdArr[i,3] <= z <= cdArr[i+1,3]:
            t = [cdArr[i,0],cdArr[i,1],cdArr[i,2]]
            i = i + 999999999
        i = i + 1

    #find the last braid angle
    iv, a = braidAngle(normal,t,f)
    #find last pitch
    pitch = IDP_geometry.pitch(a,MD,z,spoolsPhy)
    pocList[np.size(pocList,0)-1,7] = a
    pocList[np.size(pocList,0)-1,9] = pitch
    
    #store pocList and sppList for troubleshooting and review
    np.save(lPath+"\\temporary\\pocList.npy", pocList[:,1:4])    
    np.save(lPath+"\\temporary\\sppList.npy", sppList) 
    #add to matrix?
    
    print("YARN "+str(YARN)+" simulation time :--- %s seconds ---" % (time.time() - st2)) 
    if sppList[0,1] == sppList[np.size(sppList,0)-1,1]:
        print(sppList)
    return(pocList)
    
    