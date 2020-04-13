# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 13:22:34 2020

@author: jakub.kucera
"""

import numpy as np
from IDP_databases import cnt_X, dc_X
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from Braid_main_P import poc
from default_var_dict import getBase
import time
import IDP_geometry
import os

def maxVersion(trimfile):
    conn,cursor = cnt_X('NCC')   
    here = """'%"""+trimfile+"""%'"""
    query = "SELECT version FROM BraidMain where GENfile like "+here
    #print(query)
    cursor.execute(query)
    #get results
    sd = []
    rows = cursor.fetchall()
    for row in rows:
        sd.append(int(row[0])) 
    dc_X('NCC',conn,cursor)
    if is_empty(sd) ==True:
        maxNo = 0
    else:
        maxNo = max(sd)
    bIT = maxNo + 1
    return(bIT)
      
def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True

def baseBraid(varVal,CADfile,MeshFile):
    lPath = os.path.dirname(os.path.abspath(__file__))
    st1 = time.time() 

    MD = np.load(lPath+"\\catiafiles\\meshfiles\\"+MeshFile+"_nodes.npy")
    
    MS = varVal["mandrel_speed"]
    spoolsPhy = varVal['spools']
    rotax = 0.15 #travel per second (rad/s)
    #0.11 for braid comparison oscar
    
    #ammending the number of iterations required based on expected braid angles
    ratio2 = MS/rotax
    spoolsWa =  max(4,int(0.4*ratio2))
    print(spoolsWa)
    
    trimfile = CADfile.split("_")[0]+"_"+CADfile.split("_")[1]+"_"\
               +CADfile.split("_")[2]+"_"
    #Checks SQL braiding simulations table for latest version name.
    bIT = maxVersion(trimfile)
    #If function addpats number into correct filename segment.
    if bIT < 10:
        vn = "00"+str(int(bIT))
    elif bIT <100:
        vn = "0"+str(int(bIT))
    else:
        vn = str(int(bIT))
    vn = "B"+vn   
    BraidFile = trimfile+vn
    print(BraidFile)
    
    #Create a table to store braidign point by point data
    GENfile = BraidFile #CADfile.replace("_A0", "_X0")         
    cnnB,crrB = cnt_X('NCC')       
    query ="CREATE TABLE "
    query += GENfile
    query +="(id int IDENTITY(1,1) PRIMARY KEY,YARN integer,x numeric(8,3),y numeric(8,3),z numeric(8,3),bAngle numeric(4,2),xN numeric(8,3),yN numeric(8,3),zN numeric(8,3),pitch numeric(8,3),iteration_time numeric(8,4),warpORweft integer)"
    crrB.execute(query)
    cnnB.commit()

    #upload the high level braiding information to main braiding table
    query = "INSERT INTO BraidMain(GENfile,version, spoolsWa, rota, travel, GuideRadius,InitialMandrelDistance,simulation_time) VALUES("
    query += """'"""+GENfile+"""',"""+str(bIT)+""","""+str(spoolsWa)+""","""+str(rotax)+""","""+str(varVal["mandrel_speed"])+""","""+str(varVal["guide_rad"])+""","""+str(varVal["IMD"])+""","""+str(0)+""")"""
    crrB.execute(query)
    cnnB.commit()
    dc_X('NCC',cnnB,crrB)
    
    #find points on mandrel centreline
    datum, cdArr = IDP_geometry.centreline(MD)
    print(datum)
    WW = 0
    while WW < 2:
        YARN = 0
        #for each yarn
        while YARN < spoolsWa:
            #following function simulates positioning of a specific yarn on mandrel surface
            pocList = poc(MD,varVal,YARN,WW,spoolsWa,spoolsPhy,datum,cdArr,CADfile,rotax)
            cnnB,crrB = cnt_X('NCC')  
            i = 0
            while i < np.size(pocList,0):
                #pocList decomposed for clarity of the script
                x = pocList[i,1]
                y = pocList[i,2]
                z = pocList[i,3]
                xN = pocList[i,4]
                yN = pocList[i,5]
                zN = pocList[i,6]               
                bAngle = pocList[i,7]
                pitch =  pocList[i,9]
                tt = pocList[i,8]   
                query = "INSERT INTO "+GENfile+"(YARN,x,y,z,bAngle,xN,yN,zN,pitch,iteration_time,warpORweft) VALUES("
                query +=str(YARN)+","+str(x)+","+str(y)+","+str(z)+","+str(bAngle)+","+str(xN)+","+str(yN)+","+str(zN)+","+str(pitch)+","+str(tt)+","+str(WW)+")"
                #print(query)
                crrB.execute(query)    
                i = i + 1
            cnnB.commit()
            dc_X('NCC',cnnB,crrB)
            YARN = YARN + 1
        WW = WW + 1
    
    bstt = time.time() - st1
    cnnB,crrB = cnt_X('NCC')  
    print("Total braiding simulation time:--- %s seconds ---" % (bstt)) 
    query = "INSERT INTO BraidMain(simulation_time) VALUES("+str(bstt)+")"
    crrB.execute(query)
    cnnB.commit()
    dc_X('NCC',cnnB,crrB)    
    
    return(BraidFile)

#varVal, varMin,varMax = getBase()
#varVal["guide_rad"] = 300
#CADfile = "IDP_spar_A270_JK"
#MeshFile = "IDP_spar_A270_N001"
#baseBraid(varVal,CADfile,MeshFile)

       
