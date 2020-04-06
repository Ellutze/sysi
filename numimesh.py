# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 09:28:11 2020

@author: jk17757
"""

import time
import numpy as np
from general_utils import foil_to_spar
from default_var_dict import getBase
from math_utils import orderByColumn
import math
import IDP_inpGen

from IDP_databases import cnt_X,dc_X

def is_empty(any_structure):
    #this functions checks if a list (or suchlike) is empty, used below in abaMain
    if any_structure:
        return False
    else:
        return True

def XSP(varVal,CADfile = "none_A000_JK"):
    
    st118 = time.time()
    #Naming convention used for the System of Simulations (SoS) - bit long, maybe simplify? or replace by input?
    #looks for other meshes with the same source geomertry
    cnnB,crrB = cnt_X('NCC')
    here = """'%"""+CADfile+"""%'"""
    query = "SELECT version FROM mesh_list where CADfile like "+here
    #print(query)
    crrB.execute(query)
    #get results
    sd = []
    rows = crrB.fetchall()
    #creates a list of version numbers
    for row in rows:
        try:
            sd.append(int(row[0]))
            #break
        except TypeError:
            print("x")
    #highest version number is stored
    if is_empty(sd) ==True:
        maxNo = 0
    else:
        maxNo = max(sd)
    #next version number - used for this analysis
    version = maxNo + 1
    trimfile = CADfile.split("_")[0]+"_"+CADfile.split("_")[1]+"_"+CADfile.split("_")[2]+"_"
    #file definition based on version number
    if version < 10:
        vn = "00"+str(int(version))
    elif version <100:
        vn = "0"+str(int(version))
    else:
        vn = str(int(version))
    #create a MeshFile name from CadFile and mesh version
    MeshFile = trimfile +"N"+ vn
    #close SQL handles 
    dc_X('NCC',cnnB,crrB)
    
    
    mshI = varVal["mesh_size"]
    #Count the number of sections based on number of airfoils in varVal
    NX = 0
    for key in varVal: 
        if "airfoil" in key:
            NX = NX + 1 

    #the spanwise lenght of section         
    zit = varVal["span"]/(NX-1)

    #iterate through sections 
    meepo = 0
    while meepo < NX:
        #often used variables taken out of varVal
        chord = float(varVal['chord_'+str(meepo)])
        twist= float(varVal['twist_'+str(meepo)])
        dihedral = float(varVal['dihedral_'+str(meepo)])
    
        print("meepo:",meepo)
        
        #z and data to foil need to come from above step of iteration
        spar = foil_to_spar(varVal["airfoil_"+str(meepo)],varVal["c_min"],varVal["c_max"])
        #cLoc = varVal["chord_"+str(meepo)]
        z = zit*meepo
    
        #Reference point for scaling and rotations.
        xAnchor = (varVal["c_max"]+varVal["c_min"])/2
        #Significantly cambered aerofoils might require yAnchor to be calculated
        yAnchor = 0
        #Adjusting airfoil points, based on section parameters.
        e = 0
        af = np.zeros([np.size(spar,0),2])
        while e < np.size(spar,0):
            
            #translate choordinate system for correct scaling
            x = spar[e,0]-xAnchor
            y = spar[e,1]-yAnchor
            #scale the part
            x = chord*x
            y = chord*y
            #rotation before translation
            r = math.sqrt(y**2+x**2)
            epsi = math.asin(y/r)
            epsiD = epsi*180/math.pi
            #the ifs adjust for math.sin only working with half a circle
            if x < 0 and y >0:
                epsiD = 180-epsiD
            if x < 0 and y <0:
                epsiD = (180-abs(epsiD))*-1
            epsiD = twist+epsiD
            epsi = epsiD*math.pi/180
            y = r*math.sin(epsi)
            x = math.sqrt(r**2-y**2)
            if - 90 < epsiD <90:
                x = abs(x)
            if 90 < epsiD or epsiD < -90:
                x = abs(x)*-1
            #sweep, x-translation
            xT =(z)*math.tan(float(varVal['sweep_'+str(meepo)])*math.pi/180)
            x = x  + xT
            #dihedral, y -translation
            yT =(z)*math.tan(float(dihedral)*math.pi/180)
            y = y + yT
            #New set of points.
            af[e,0] = x
            af[e,1] = y
            e = e + 1
        #translated coordinates of spar
        spar = af
        i = 0
        #c is the gradient of line dividing top and bottom surface points.
        c = xT*math.sin(twist*math.pi/180)
        TT = np.zeros([1,4])
        BB = np.zeros([1,4])
        rtemp = np.zeros([1,4])
        while i < np.size(spar,0):
            if spar[i,1] < (yAnchor-c+yT+math.tan(twist*math.pi/180)*(spar[i,0]-xAnchor)):
                rtemp = np.matrix([4,spar[i,0],spar[i,1],z])
                BB = np.concatenate((BB,rtemp),axis=0)
            else:
                rtemp = np.matrix([0,spar[i,0],spar[i,1],z])
                TT = np.concatenate((TT,rtemp),axis=0)
            i = i + 1
        TT = np.delete(TT,0,axis=0)
        BB = np.delete(BB,0,axis=0)
    
        #here you need to sort the TT and BB based on X
        TT = orderByColumn(TT,1,1)
        BB = orderByColumn(BB,1,-1)
        
        #Here you use the mesh size to find positions in x, with position in x find nearest x position and extrapolates for actual x-y cc
        #create BB1 and TT1 for actual points used later
        TTdiff = max(TT[:,1])-min(TT[:,1])
        if meepo > 0:
            ML0_old = np.copy(ML0)
            mshTi = TTdiff/((np.size(ML0_old,0)-0.999))
        else:
            mshTi = int((TTdiff)/mshI)
            #the number of steps is increased by 0.0001 ensuring that when later iterated the last step always fits the while loop
            mshTi = (TTdiff)/(mshTi+0.0001)
        #Top surface points are generated by interpolation between existing airfoil points,
        #single mesh size appart.
        no_steps = TTdiff/mshTi    
        ML0 = np.zeros([1,4])
        i = 0
        x = min(TT[:,1])
        while i < no_steps:
            ii = 0
            while ii < np.size(TT,0):
                #find the nearest points
                if TT[ii,1] <= x <= TT[ii+1,1]:
                    #interpolate between nearest points
                    y = ((x-TT[ii,1])/(TT[ii+1,1]-TT[ii,1]))*(TT[ii+1,2]-TT[ii,2])+TT[ii,2]
                    tempML = np.matrix([TT[ii,0]+0.0001*x,x,y ,z])
                    ML0 = np.concatenate((ML0,tempML),axis=0)
                    ii = ii + np.size(TT,0)
                ii = ii + 1
            x = x + mshTi
            i = i + 1
        ML0 = np.delete(ML0,0,axis=0)

        #check that number of elements per cross-section remains constant
        if meepo != 0:
            if np.size(ML0,0) != np.size(ML0_old,0):
                print("error has occured, top sections have varying number of elements")
                print("ML0_old:", np.size(ML0_old,0))
                print("ML0:",np.size(ML0,0))
    
        BBdiff = max(BB[:,1])-min(BB[:,1])
        if meepo > 0:
            ML4_old = np.copy(ML4)
            mshTi = BBdiff/((np.size(ML4_old,0)-0.999))
        else:
            mshTi = int(BBdiff/mshI)
            #the number of steps is increased by 0.0001 ensuring that when later iterated the last step always fits the while loop
            mshTi = BBdiff/(mshTi+0.0001)
        ML4 = np.zeros([1,4])
        no_steps = BBdiff/mshTi
        i = 0
        x = max(BB[:,1])
        while i < no_steps:
            ii = 0
            while ii < np.size(BB,0):
                #find the nearest points
                if BB[ii,1] >= x >= BB[ii+1,1]:
                    #interpolate between nearest points
                    y = ((x-BB[ii,1])/(BB[ii+1,1]-BB[ii,1]))*(BB[ii+1,2]-BB[ii,2])+BB[ii,2]
                    tempML = np.matrix([BB[ii,0]+0.1-0.0001*x,x,y ,z])
                    ML4 = np.concatenate((ML4,tempML),axis=0)
                    ii = ii + np.size(BB,0)
                ii = ii + 1

            x = x - mshTi
            i = i + 1

        ML4 = np.delete(ML4,0,axis=0)

        if meepo != 0:
            if np.size(ML4,0) != np.size(ML4_old,0):
                print("error has occured, bottom sections have varying number of elements")  
                print("ML4_old:", np.size(ML4_old,0))
                print("ML4:",np.size(ML4,0))
        #...
        ML0l = np.size(ML0,0)
        ML4l = np.size(ML4,0)
        
        BBl = np.size(BB,0)
        TTl = np.size(TT,0)
    
        #check if enough space to use prescribed radius
        RADi = 0
        while RADi <= varVal["RAD"]:
            #find the distance between the front nodes of the spars, and aft nodes of the spar, consider the smaller gap
            RADi = min(abs(TT[0,2]-BB[BBl-1,2])/2 , abs(TT[TTl-1,2]-BB[0,2])/2)
            if RADi < varVal["RAD"]*5:
                varVal["RAD"] = varVal["RAD"]*0.95
                print("radius has been adjusted")
                print(varVal["RAD"])
        #print(varVal["RAD"],"RAD")
    
        if meepo != 0:
            ML2_old = np.copy(ML2)
        #if enough space, create points for groups 2,6
        ML2 = np.matrix([[2.0000, varVal["RAD"]+ML0[np.size(ML0,0)-1,1] ,ML0[np.size(ML0,0)-1,2]-varVal["RAD"] , z],
                         [2.0999, varVal["RAD"]+ML4[0,1] ,ML4[0,2]+varVal["RAD"] , z]])
    
        ML2s = np.copy(ML2[0,2])-np.copy(ML2[1,2])
        MLYs = np.copy(ML2[0,1])-np.copy(ML2[1,1])
        if meepo == 0:
            nE = round(ML2s/mshI)
        else:
            nE = np.size(ML2_old,0)-1
    
        i = 1
        while i < nE:
            ML2 = np.insert(ML2, (i), np.matrix([2+0.0001*i,ML2[(i-1),1]-(MLYs/nE),ML2[(i-1),2]-(ML2s/nE),z]), axis=0)
            i = i + 1
        if meepo !=0:
            if np.size(ML2,0) != np.size(ML2_old,0):
                print("error has occured, third sections have varying number of elements")     
                print("ML2_old:", np.size(ML2_old,0))
                print("ML2:",np.size(ML2,0))

        if meepo != 0:
            ML6_old = np.copy(ML6)    
            
        ML6 = np.matrix([[6.0000, ML4[(np.size(ML4,0)-1),1]-varVal["RAD"] ,ML4[np.size(ML4,0)-1,2]+varVal["RAD"] , z],
                         [6.0999, ML0[0,1]-varVal["RAD"] ,ML0[0,2]-varVal["RAD"] , z]])
    
        ML6s = abs(np.copy(ML6[0,2])-np.copy(ML6[1,2]))
        MLY6s = -(np.copy(ML6[0,1])-np.copy(ML6[1,1]))
        if meepo == 0:
            nE = round(ML6s/mshI)
        else:
            nE = np.size(ML6_old,0)-1
        
    
        i = 1
        while i < nE:
            ML6 = np.insert(ML6, (i), np.matrix([6+0.0001*i,ML6[(i-1),1]+(MLY6s/nE),ML6[(i-1),2]+(ML6s/nE),z]), axis=0)
            i = i + 1
        if meepo !=0:
            if np.size(ML2,0) != np.size(ML2_old,0):
                print("error has occured, sixt sections have varying number of elements") 
                print("ML6_old:", np.size(ML6_old,0))
                print("ML6:",np.size(ML6,0))
        #Corners 
        if meepo != 0:
            ML99_old = np.copy(ML99)
            
        ML99 = np.zeros([1,4])
        #ML_ =np.zeros([1,4])
        #print(ML0)
        #print(ML2)
        #print(ML4)
        #print(ML6)
        #print(ML0[np.size(ML0,0)-1,1])
        ML8 = ML0
        ii = 0
        while ii < 4:
            EX = "ML"+str((ii*2))+"[np.size(ML"+str((ii*2))+",0)-1,1]"
            x1 = eval(EX)
            EX = "ML"+str(((ii*2)+2))+"[0,1]"
            x2 = eval(EX)
            EX = "ML"+str((ii*2))+"[np.size(ML"+str((ii*2))+",0)-1,2]"
            y1 = eval(EX)
            EX = "ML"+str(((ii*2)+2))+"[0,2]"
            y2 = eval(EX)
            print(x1,y1,x2,y2)
            d = (((y1-y2)**2+(x1-x2)**2)**(0.5))/2
            A = (varVal["RAD"]**2-d**2)**0.5
            #unit vectors
            if ii == 0 or ii == 1:
                ix = -1
            else:
                ix = 1
            if ii == 1 or ii == 2:
                iy = 1
                
            else:
                iy = -1
            
            Vx = (abs(x1-x2)*ix)/(d*2)
            Vy = (abs(y1-y2)*iy)/(d*2)
        
            ptx = ((x1+x2)/2)+A*Vx
            pty = ((y1+y2)/2)+A*Vy
            
            if ii == 0 or ii == 2:
                theta0 = math.atan(abs((x1-ptx)/(y1-pty)))
                theta1 = math.atan(abs((x2-ptx)/(y2-pty)))
            else:
                theta0 = math.atan(abs((y1-pty)/(x1-ptx)))
                theta1 = math.atan(abs((y2-pty)/(x2-ptx))) 
            if meepo == 0:
                #by changing o the mesh in corners can be of different width than other mesh
                o = 1
                cca = int((d*2)/(mshI/o))
                #check if this works, prevents division by 0
                if cca == 0:
                    cca = 1
            else:
                count = 0
                mj = 0
                #print(ML99_old)
                while mj < np.size(ML99_old,0):
                    if (ii*2+1) < ML99_old[mj,0] < (ii*2+2):
                        count = count + 1
                    mj = mj + 1
                cca = count+1
            tI = (theta1-theta0)/cca
        
            i= 1
            while i < cca:
                theta = i*tI+theta0
                if ii == 0:
                    temp = np.matrix([[1+0.0001*i,varVal["RAD"]*math.sin(theta)+ptx,varVal["RAD"]*math.cos(theta)+pty,z]])
                elif ii == 1:
                    temp = np.matrix([[3+0.0001*i,varVal["RAD"]*math.cos(theta)+ptx,pty-varVal["RAD"]*math.sin(theta),z]])
                elif ii == 2:
                    temp = np.matrix([[5+0.0001*i,ptx-varVal["RAD"]*math.sin(theta),pty-varVal["RAD"]*math.cos(theta),z]])
                else:
                    temp = np.matrix([[7+0.0001*i,ptx-varVal["RAD"]*math.cos(theta),varVal["RAD"]*math.sin(theta)+pty,z]])
                ML99 = np.concatenate((ML99,temp),axis=0)
                i = i + 1
            ii = ii + 1  
        ML99 = np.delete(ML99,0,axis=0)
    
        if meepo !=0:
            if np.size(ML99,0) != np.size(ML99_old,0):
                print("error has occured, corner sections have varying number of elements") 
                print("ML99_old:", np.size(ML99_old,0))
                print("ML99:",np.size(ML99,0))    
        MLX = np.concatenate((ML99,ML0,ML2,ML4,ML6),axis = 0)
        MLX = orderByColumn(MLX,0,1)
        #print(MLX)
        np.savetxt("D:\\IDPcode\\Temporary\\MLX"+str(meepo)+".csv", MLX, delimiter=",")
    
    
        #print(MLX)
        #move into later - instead of 1 count the actual rows
        if meepo == 0:
            ML = np.zeros([np.size(MLX,0),4,NX])
        ML[:,:,meepo]=MLX
        #print(np.size(ML,0))
        
        #assemble all groups of points into the first matrix of ML
        meepo = meepo + 1    
        #note down the number of points in each section... next iteration/cross-section will have element size based on number of elements in first
        
        #iterate 
        
        # after points on cross-sections exist
        #create matrix of vectors
        #the spanwise size of elements depends on local cross-section size
        #use the vectors to generate all points
    MLm = np.copy(ML)

    i = 0
    while i < (NX-1):
        #print("i:",i)
        zdif = ML[0,3,i+1]-ML[0,3,i]
        mshTii = int(zdif/mshI)
        mshTi = zdif/mshTii
        
        ii = 1
        while ii < mshTii:
            #print("ii:",ii)
            seg = np.zeros([np.size(ML,0),4])
            z = mshTi*ii+ML[0,3,i]
            iii = 0
            while iii < (np.size(ML,0)):
                #print("iii:",iii)
                seg[iii,0] = ML[iii,0,i]
                seg[iii,1] = ((z-ML[iii,3,i])/(ML[iii,3,i+1]-ML[iii,3,i]))*(ML[iii,1,i+1]-ML[iii,1,i])+ML[iii,1,i]
                seg[iii,2] = ((z-ML[iii,3,i])/(ML[iii,3,i+1]-ML[iii,3,i]))*(ML[iii,2,i+1]-ML[iii,2,i])+ML[iii,2,i]
                seg[iii,3] = z
                iii = iii + 1
            #seg = np.delete(seg,0,axis=0)
            MLm = np.insert(MLm, (np.size(MLm,2)-(NX-1-i)), seg, axis=2)
            ii = ii + 1
        i = i + 1
    IDP_inpGen.inpGen(MLm,MeshFile)
    span_ele_size = varVal["mesh_size"]
    xs_seed = np.size(MLm,0)
    
    count_span_el = np.size(MLm,2)
    
    cnnB,crrB = cnt_X('NCC')
    mTime = time.time() - st118
    query = "INSERT INTO mesh_list(CADfile,MeshFile,xs_seed,span_ele_size,version,meshing_time) VALUES("
    query += """'"""+CADfile+"""','"""+MeshFile+"""',"""+str(xs_seed)+""","""+str(count_span_el)+""","""+str(version)+""","""+str(mTime)+""")"""
    crrB.execute(query)
    cnnB.commit()
    
    #close SQL handles 
    dc_X('NCC',cnnB,crrB)
    print("meshing took:"+str(time.time()-st118)+" seconds") 
    np.save("D:\\IDPcode\\catiafiles\\meshfiles\\"+MeshFile+"_nodes.npy", MLm)
    return(MeshFile, span_ele_size, xs_seed)
        #save all points - into CATIA for check? 
        
#MeshFile = "timeCompX"
#varVal, varMin,varMax = getBase()
#varVal["mesh_size"] = 1
#MLm,xAnchor,yAnchor = XSP(varVal)
#print(MLm)
#IDP_inpGen.plotXSP(MLm,xAnchor,yAnchor,varVal)
#IDP_inpGen.inpGen(MLm,MeshFile)