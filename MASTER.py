from optis import SingleCAD, MultiMesh


#import Braid_CMD_C 
import Braid_CMD_P 



from Abaqus_main import abaMain
import numpy as np
from IDP_databases import cnt_X,dc_X
from mysql.connector import MySQLConnection
from IDP_cheats import togglePulse
from python_mysql_dbconfig import read_db_config
import time
import datetime
import os
import sys
from RTM_main import mRTM
import datetime
import time
import numimesh
from default_var_dict import getBase

def AgentTyrael(deflection, mass):
    #Fitness functoin - Tyrael judges the worthiness of a member.
    maxweight = 0.0005      #ton
    maxdeflection = 50      #mm
    idweight =0 
    idealdeflection = 5
    importance_w = 1
    importance_d = 1
    sW = max(0,(1- (mass-idweight)/(maxweight-idweight)))
    sD = max(0,(1- (deflection -idealdeflection)/
            (maxdeflection-idealdeflection))
            )
    print("sW",sW)
    print("sD",sD)
    mW = importance_w*sW
    mD = importance_d*sD
    phero = (mW+mD)/2
    return(phero)

def is_empty(any_structure):
    #This functions checks if a list (or suchlike) is empty, 
    #used below in abaMain.
    if any_structure:
        return False
    else:
        return True

def SingleLoop(varVal):
    lPath = os.path.dirname(os.path.abspath(__file__))
    #input: variable variation (5 atm)
    
    #this is where the loop really starts.
    
    #The project and part should be the same for all parts subject to same 
    #optimisation loop.
    part = "UAV1"
    project = "IDP"
    
    #If "new" is set, the corresponding simulation is run.
    #If an existent name of file is set, the simulation just records 
    #the name of the file and proceeds to next simulation
    CADfile = "new"
    BraidFile = "new"
    #Optional specification lines:
    #BraidFile = "IDP_spar_A147_b001"
    #CADfile = "IDP_spar_A147_JK"
    #CADfile = "IDP_oscar_A044_NA"
    
    #cannot have old braiding without old CADfile
    if BraidFile != "new" and CADfile == "new":
        print("cannot have old braiding simulation with new CAD")
        quit()
    MeshFile = "new"
    #MeshFile = "IDP_Spar_A147_M001"

    st999 = time.time()
    print(datetime.datetime.now())
    cnnC,crrC = cnt_X('NCC')
    
    #SETUP NEW ENTRY IN SQL 
    #looks for other analysis of the same source geomertry
    query = """SELECT Iteration_count FROM arun where project like '"""\
            +project+"""' and part like '"""+part+"""'"""
    crrC.execute(query)
    #get results
    sd = []
    rows = crrC.fetchall()
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
    Iteration_count = maxNo + 1

    #input information into SQL
    query = "INSERT INTO arun(Project,part,Iteration_count) VALUES("
    query += """'"""+project+"""','"""+part+"""',"""+str(Iteration_count)+""")"""
    crrC.execute(query)
    cnnC.commit()
    #close SQL handles 
    dc_X('NCC',cnnC,crrC)

    with open(lPath+"\\temporary\\underground.txt", "a") as text_file:
        text_file.write("Generating CAD shape.\n")

    #MAIN BODY OF THE SCRIPT
    if CADfile == "new":
        #Assign the chord limits of the spar, these are expressed as ratio 
        #of full chord lenght, and remain in the same proportion through 
        #the span.
        
        #aerofoil_S = "clarkYdata.dat"
        
        
        #aerofoil_S = "AerofoilCollection\\clarkYdata.dat"
        #Each section defined by: span position, aerofoil, 
        #size multiplier (taper...), twist,sweep,dihedral
        #sectioned = np.matrix([[0,varVal['airfoil_0'],varVal['chord_0'],varVal['twist_0'],varVal['sweep_0'],0]
        #                     ,[(200),varVal['airfoil_1'],varVal['chord_1'],varVal['twist_1'],varVal['sweep_1'],0]
        #                     ,[300,varVal['airfoil_2'],varVal['chord_2'],varVal['twist_2'],varVal['sweep_2'],0]
        #                     ,[400,varVal['airfoil_3'],varVal['chord_3'],varVal['twist_3'],varVal['sweep_3'],0]
        #                      ])    
        #start CATIA and run the script
        os.startfile(r"C:\Program Files\Dassault Systemes\B27\win_b64\code\bin\CNEXT.exe")  
        CADfile = SingleCAD(project,part,varVal)  
        os.system("TASKKILL /F /IM Cnext.exe")
    #update SQL after CAD creation
    cnnC,crrC = cnt_X('NCC')    
    query = """UPDATE arun SET CADfile = '"""+str(CADfile)+"""'"""\
            """WHERE (part = '"""+part+"""') and (project = '"""+project+"""')"""\
            """and (iteration_count = """+str(Iteration_count)+""");"""
    crrC.execute(query)
    cnnC.commit()

    #close SQL handles 
    dc_X('NCC',cnnC,crrC)
    
    with open(lPath+"\\temporary\\underground.txt", "a") as text_file:
        text_file.write("Running braiding simulation.\n")

    #Braiding and meshing could be run in parallel - if separate catia 
    #machine is available.
    print("CAD module finished "+CADfile+", commencing Meshing module")
    
    #meshType should be selected in the GUI eventually...
    #also the sizes available with meshTypes differ
    meshType = "numimesh"
    if MeshFile =="new":
        if meshType == "CATIA":
            os.startfile(r"C:\Program Files\Dassault Systemes\B27\win_b64\code\bin\CNEXT.exe") 
            MeshFile, span_ele_size, xs_seed = MultiMesh(CADfile,varVal)
            os.system("TASKKILL /F /IM Cnext.exe")
        elif meshType == "numimesh":
            MeshFile, span_ele_size, xs_seed = numimesh.XSP(varVal,CADfile)
            
        #Open and close MySQL connection.
        cnnC,crrC = cnt_X('NCC')
        query = """UPDATE arun SET span_ele_size = '"""+str(span_ele_size)+\
        """' WHERE (part = '"""+part+"""') and (project = '"""+project+"""')\
        and (iteration_count = """+str(Iteration_count)+""");"""
        crrC.execute(query)
        cnnC.commit()
        query = """UPDATE arun SET xs_seed = '"""+str(xs_seed)+"""'\
                WHERE (part = '"""+part+"""') and (project = '"""\
                +project+"""') and (iteration_count = """\
                +str(Iteration_count)+""");"""
        crrC.execute(query)
        cnnC.commit()
    else:
        #Open and close MySQL connection.
        cnnC,crrC = cnt_X('NCC')
        query = """SELECT xs_seed FROM arun where MeshFile = '"""\
                +MeshFile+"""' and xs_seed is not null;"""
        crrC.execute(query)
        rows = crrC.fetchall()
        xs_seed = 0
        for row in rows:
            xs_seed = float(row[0])
        query = """UPDATE arun SET xs_seed = '"""+str(xs_seed)+"""'\
                WHERE (part = '"""+part+"""') and (project = '"""+project+\
                """') and (iteration_count = """+str(Iteration_count)+\
                """);"""
        crrC.execute(query)
        cnnC.commit()        
        query = """SELECT span_ele_size FROM arun where MeshFile = '"""\
                +MeshFile+"""' and span_ele_size is not null;"""
        crrC.execute(query)
        rows = crrC.fetchall()
        span_ele_size = 0
        for row in rows:
            span_ele_size = float(row[0])
        query = """UPDATE arun SET span_ele_size = '"""+str(span_ele_size)\
                +"""' WHERE (part = '"""+part+"""') and (project = '"""\
                +project+"""') and (iteration_count = """\
                +str(Iteration_count)+""");"""
        crrC.execute(query)
        cnnC.commit()
    #meshing data into SQL 
    query = """UPDATE arun SET MeshFile = '"""+str(MeshFile)+"""'\
            WHERE (part = '"""+part+"""') and (project = '"""+project+"""')\
            and (iteration_count = """+str(Iteration_count)+""");"""
    crrC.execute(query)
    cnnC.commit()
    #close SQL handles 
    dc_X('NCC',cnnC,crrC)
    
    print("Meshing module finished "+MeshFile+", commencing Braiding module")
    
    
    
    if BraidFile =="new":
        #Success check, if braiding below allowed braid angle the 
        #braid sim has to be re-run.
        
        #use this as selection later?
        braid = "P"
        if braid == "P":
            BraidFile = Braid_CMD_P.baseBraid(varVal,CADfile,MeshFile)
        elif braid == "C":
            MS = varVal['mandrel_speed']  # relic from original braiding simulation
            success = 0
            while success ==0:
                os.startfile(r"C:\Program Files\Dassault Systemes\B27\win_b64\code\bin\CNEXT.exe")  
                BraidFile, success, MS = Braid_CMD_C.baseBraid(CADfile,MS,varVal)
                os.system("TASKKILL /F /IM Cnext.exe")
    else:
        #Reuse root_perimeter if braiding simulation is not run.
            #Open and close MySQL connection.
        cnnC,crrC = cnt_X('NCC')
        query = """SELECT root_perimeter FROM arun where Cadfile = '"""\
                +CADfile+"""' and root_perimeter is not null;"""
        crrC.execute(query)
        rows = crrC.fetchall()
        root_perimeter = 0
        for row in rows:
            root_perimeter = float(row[0])
        query = """UPDATE arun SET root_perimeter = '"""+str(root_perimeter)\
                +"""' WHERE (part = '"""+part+"""') and (project = '"""\
                +project+"""') and (iteration_count = """\
                +str(Iteration_count)+""");"""
        crrC.execute(query)
        cnnC.commit()
        #Populate the SQL row with suitable braid data.
    
        #close SQL handles 
        dc_X('NCC',cnnC,crrC)
        #give it time to close pulse
        time.sleep(5)
        
    #Open and close MySQL connection.
    cnnC,crrC = cnt_X('NCC')
    
    
    query = """UPDATE arun SET BraidFile = '"""+str(BraidFile)+"""'"""\
            """WHERE (part = '"""+part+"""') and (project = '"""+project+"""')"""\
            """and (iteration_count = """+str(Iteration_count)+""");"""
    crrC.execute(query)
    cnnC.commit()
    #close SQL handles 
    dc_X('NCC',cnnC,crrC)
    
    
    with open(lPath+"\\temporary\\underground.txt", "a") as text_file:
        text_file.write("Meshing.\n")
    print("Braiding module finished "+BraidFile+", commencing FE module")
    

    maxDeflection,mass, FeFile = abaMain(BraidFile,MeshFile,CADfile,varVal,meshType,xs_seed)
    print("Maximum deflection with current setup is "+str(maxDeflection))
    
    pher = AgentTyrael(maxDeflection,mass)
    
    #FE SQL entry
    cnnC,crrC = cnt_X('NCC')                             
    
    query = """UPDATE arun SET FeFile = '"""+str(FeFile)+"""'\
            WHERE (part = '"""+part+"""') and (project = '"""+project+"""')\
            and (iteration_count = '"""+str(Iteration_count)+"""');"""
    crrC.execute(query)
    cnnC.commit()
    
    query = """UPDATE arun SET date = GetDate() WHERE (part = '"""+part+"""')\
            and (project = '"""+project+"""') and (iteration_count = """\
            +str(Iteration_count)+""");"""
    crrC.execute(query)
    cnnC.commit()
    
    query = """UPDATE arun SET pher = '"""+str(pher)+"""' \
            WHERE (part = '"""+part+"""') and (project = '"""+project+"""')\
            and (iteration_count = """+str(Iteration_count)+""");"""
    crrC.execute(query)
    cnnC.commit()
    
    query = """SELECT idARUN FROM arun where Cadfile = '"""+CADfile+"""'\
            and (iteration_count = """+str(Iteration_count)+""");"""
    crrC.execute(query)
    rows = crrC.fetchall()
    root_perimeter = 0
    for row in rows:
        arunID = int(row[0])
    
    #close SQL handles 
    dc_X('NCC',cnnC,crrC)
    
    #Abaqus analysis finished, commencing infusion simulation.
    #______insert RTM_main here .... (number of layers, name of part)
    #toggle if I want to run RTM simulation (maybe set a fitness treshold?)
    if pher > 0.9:
        RTMsim = True
    else:
        RTMsim = False
    if RTMsim == True:
        os.startfile(r"C:\Program Files\Dassault Systemes\B27\win_b64\code\bin\CNEXT.exe") 
        hold = varVal["mesh_size"]
        if varVal["mesh_size"] < 5:
            varVal["mesh_size"] = 5
        MeshFile, span_ele_size, xs_seed = MultiMesh(CADfile,varVal)
        os.system("TASKKILL /F /IM Cnext.exe")
        varVal["mesh_size"] = hold
        with open(lPath+"\\temporary\\underground.txt", "a") as text_file:
            text_file.write("Running flow simulation.\n")
        print("FE module finished "+FeFile+", commencing infusion module")
        #you need a resin for both structural and rtm analysis... no data yet
        RTMfile = mRTM(MeshFile,BraidFile,"Hexion_9600" ,varVal)
        
    
        cnnC,crrC = cnt_X('NCC')                             
        
        query = """UPDATE arun SET RTMfile = '"""+str(RTMfile)+"""'\
                WHERE (part = '"""+part+"""') and (project = '"""+project+"""')\
                and (iteration_count = """+str(Iteration_count)+""");"""
        crrC.execute(query)
        cnnC.commit()
        #close SQL handles 
        dc_X('NCC',cnnC,crrC)
    
    simulation_time = time.time()-st999         
    cnnC,crrC = cnt_X('NCC') 
    query = """UPDATE arun SET simulation_time = """+str(simulation_time)\
                +""" WHERE (part = '"""+part+"""') and (project = '"""\
                +project+"""') and (iteration_count = """\
                +str(Iteration_count)+""");"""
    
    crrC.execute(query)
    cnnC.commit()  
    dc_X('NCC',cnnC,crrC)
    simulation_time = time.time()-st999
    #time also into sql
    print("Combined simulation time:--- %s seconds ---" % (simulation_time))
    #add overall fitness result to the SQL
    with open(lPath+"\\temporary\\underground.txt", "a") as text_file:
        text_file.write("atm:"+str(datetime.datetime.now())+"\n")
    #If pre-GUI scripts are used MS should be passed back as well
    
    #Switch on the below to avoid running in certain hours
    
    #datetime.datetime.today()
    #datetime.datetime(2012, 3, 23, 23, 24, 55, 173504)
    #dtt = datetime.datetime.today().weekday()
    #now = datetime.datetime.now()
    #
    #while dtt == 4 and (6 < now.hour < 17):
    #    print("day:"+str(dtt))
    #    print("hour:"+str(now.hour))
    #    time.sleep(300)
    
    
    return(pher,arunID)
#SingleLoop(1,1,1,1,17)

def fixloop():
    #This loop is used instead of the above function when only few parts 
    #are required.
    #This is only used for testing purposes, no recording of data.
    BraidFile = "IDP_Spar_A207_B001"
    MeshFile = "IDP_Spar_A207_N001"
    CADfile = "IDP_Spar_A207_JK"
    meshType = "numimesh"
    varVal, varMin,varMax = getBase()
    
    print("Braiding module finished, commencing FE module")
    maxDeflection,mass, FeFile = abaMain(BraidFile,MeshFile,CADfile,varVal,meshType)
    print("Maximum deflection with current setup is "+str(maxDeflection))
#fixloop()
    
