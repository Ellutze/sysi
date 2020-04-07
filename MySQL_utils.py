import numpy as np
from IDP_databases import cnt_X,dc_X
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import time
import os
from IDP_cheats import togglePulse

def storeCADinstance(varVal,name,chord_min,chord_max,dihedral):
    #add error handling? (use the error imported, and try function)

    #establish connection with the database
    cnn,crr= cnt_X('NCC')

    query ="CREATE TABLE "
    query += name
    query +="(id int IDENTITY(1,1) PRIMARY KEY,half_span numeric(9,0),airfoil varchar(255),chord_length numeric(8,0),twist numeric(3,1),sweep numeric(3,1),dihedral numeric(3,1))"
    #print(query)
    crr.execute(query)
    #cnn.commit()

    #if section count is changed additional spanwise variables have to be added
    sectCount = 4
    io = 0

    while io < sectCount:

        query = "INSERT INTO "+name+"(half_span,airfoil,chord_length,twist,sweep,dihedral) VALUES("
        query += str((varVal['span']/(sectCount-1)*io))+""",'"""+str(varVal['airfoil_'+str(io)])+"""',"""+str(varVal['chord_'+str(io)])+","+str(varVal['twist_'+str(io)])+","+str(varVal['sweep_'+str(io)])+","+str(dihedral)+")"
        #print(query)
        crr.execute(query)                                                                                                      
        io = io + 1
        
    query = "INSERT INTO SIM_CAD_iterations(Product, Version, Iteration, RefInput,chord_min,chord_max,Created_On) VALUES("
    product = name.split("_")[0]
    version = (name.split("_")[2]).split()[0][0]
    iteration = str(name.split("_")[2])
    iteration = iteration[1:4]
    tdm = str(time.strftime("%m"))
    tdy = str(time.strftime("%y"))
    strDate = str(tdy+tdm)

    query += """'"""+product+"""','"""+version+"""','"""+str(iteration)+"""','"""+name+"""',"""+str(chord_min)+""","""+str(chord_max)+""",'"""+strDate+"""')"""
    #print(query)
    crr.execute(query)
    cnn.commit()
    dc_X('NCC',cnn,crr)
    
def DROPtable():
    #this is to be used only manually
    cnn,crr = cnt_X('NCC')
    no = 1
    while no < 5:
        query ="drop table IDP_oscar_A001_b00"+str(no)
        print(query)
        crr.execute(query)
        cnn.commit()
        no = no + 1
    dc_X('NCC',cnn,crr)
#DROPtable()   
def obtainVariable(CADfile):

    conn,cursor = cnt_X('NCC')
    query = "SELECT MAX(half_span) FROM "+CADfile
    #print(query)
    cursor.execute(query)
    #get results
    sd = np.zeros(2)
    rows = cursor.fetchall()
    for row in rows:
            sd[0] = int(row[0])
    dc_X('NCC',conn,cursor)
    
    half_span = sd[0]
    #print(half_span)
    return(half_span)
    
#obtainVariable("IDP_spariteration0203_1901_A044_JK")
    
    
def CreateTable():
    #this is used for manual table creation
    #the green lines are alteredd manually

    cnnB,crrB = cnt_X('NCC')
    
    query ="CREATE TABLE "
    query += "Mesh_list"
    query +="(id int IDENTITY(1,1) PRIMARY KEY,CADfile varchar(255),MeshFile varchar(255),xs_seed int,span_ele_size numeric(8,3),version int,verified_mesh varchar(255))"
    print(query)
    crrB.execute(query)
    cnnB.commit()
    dc_X('NCC',cnnB,crrB)
    
#CreateTable()

    
def deleteBraidIt(BraidFile,cnn,crr):
    #deletes a Braiding record and corresponding files
    cnn,crr = cnt_X('NCC')
    filePath = """D:\\IDPcode\\CatiaFiles\\BraidFiles\\"""+BraidFile+".CatPart"
    # As file at filePath is deleted now, so we should check if file exists or not not before deleting them
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")
    
    query ="""Delete FROM braidmain where GENfile = '"""+BraidFile+"""';"""
    print(query)
    crr.execute(query)
    cnn.commit()
    query ="drop table "+BraidFile
    print(query)
    crr.execute(query)
    cnn.commit()
    
    dc_X('NCC',cnn,rr)
    
def deleteMeshIt(MeshFile,cnn,crr):
    #deletes a meshing record and corresponding files#
    cnn,crr = cnt_X('NCC')
    filePath = """D:\\IDPcode\\CatiaFiles\\MeshFiles\\"""+MeshFile+".CatPart"
    # As file at filePath is deleted now, so we should check if file exists or not not before deleting them
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")
    filePath = """D:\\IDPcode\\CatiaFiles\\MeshFiles\\"""+MeshFile+".igs"
    # As file at filePath is deleted now, so we should check if file exists or not not before deleting them
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")
    
    query ="""Delete FROM mesh_list where MeshFile = '"""+MeshFile+"""';"""
    print(query)
    crr.execute(query)
    cnn.commit()
    dc_X('NCC', cnn,crr)
    
def deleteCADIt(CADfile):
    #deletes a CAD file records and corresponding files
    cnn,crr = cnt_X('NCC')
    filePath = """D:\\IDPcode\\CatiaFiles\\SourceFile\\"""+CADfile+".CatPart"
    # As file at filePath is deleted now, so we should check if file exists or not not before deleting them
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")
    filePath = """D:\\IDPcode\\CatiaFiles\\SourceFile\\"""+CADfile+".igs"
    # As file at filePath is deleted now, so we should check if file exists or not not before deleting them
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")
    
    query ="""Delete FROM sim_Cad_iterations where RefInput = '"""+CADfile+"""';"""
    print(query)
    crr.execute(query)
    cnn.commit()
    query ="drop table "+CADfile
    print(query)
    crr.execute(query)
    cnn.commit()
    dc_X('NCC',cnn,crr)
#ErrorInLast("IDP","SparIteration")

def dropDownInfo():
    cnn,crr = cnt_X('NCC')
    query  = """SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG='DIGIProps' and TABLE_NAME like '%_iters_%'"""
    crr.execute(query)
    rows = crr.fetchall()
    
    seznam = []
    for row in rows:
        r = str(row)
        #r= r.replace("""'""","")
        r = r.replace("(","")
        r = r.replace(")","")
        r = r.replace(",","")
        r = r.replace(" ","")
      #  print(r)
        query = "SELECT Column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = "+str(r)+"ORDER BY ORDINAL_POSITION"
        crr.execute(query)
        lines = crr.fetchall()
        sz = str(r)
        for line in lines:
            l = str(line)
            l = l.replace(",","")
            l = l.replace("(","")
            l = l.replace(")","")
            l = l.replace("""'""","")
            l = l.replace(" ","")
     #       print(l)
            if l != str("id") and l != str("Specie") and l != str("Generation")and l != str("fitness")and l != str("arunID"):
                sz = sz+","+str(l)
        seznam.append(sz)
    #print(seznam)
    dc_X('NCC',cnn,crr) 
    return(seznam)     
    
#dropDownInfo()
            