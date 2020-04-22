import time
import os
import shutil
import numpy as np

#ACTIVATE FOR SQL USAGE:
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from IDP_databases import cnt_X, dc_X

from RTM_cmd import cmd
from RTM_cmd_2 import cmd2
import RTM_postProc
import time

def is_empty(any_structure):
    #this functions checks if a list (or suchlike) is empty, used below in abaMain
    if any_structure:
        return False
    else:
        return True

def mRTM(MeshFile,BraidFile,resin,varVal):
    lPath = os.path.dirname(os.path.abspath(__file__))
    #This function prepares input information for RTM simulation and then
    #runs the simulation.
    #In many places phrase "ACTIVATE FOR SQL USAGE:" is used. Those sections 
    #are required for interface with MySQL database.
    REP = 1
    st393 = time.time()
    
    #ACTIVATE FOR SQL USAGE:
    conn,cursor = cnt_X('NCC')
    query = """SELECT span_ele_size, xs_seed FROM mesh_list where MeshFile = '"""+MeshFile+"""' ;"""
    print(query)
    cursor.execute(query)
    
    #get mesh related info
    sd = np.zeros(2)
    
    #ACTIVATE FOR SQL USAGE:
    rows = cursor.fetchall()
    #REPLACE THE sd[] VALUES 
    
    for row in rows:
    #for no. 147
        sd[0] = row[0] #130
        sd[1] = row[1]
    #for nu. 158:
    #sd[0] = 126
    #sd[1] = 38
    
    #ACTIVATE FOR SQL USAGE:
    dc_X('NCC',conn,cursor)
    print(sd)
    
    #One of the input files for visual-rtm scripts
    np.save(lPath+"\\temporary\\mesh_info.npy", sd)
    
    #Flow matrix baseline
    flowM = np.zeros([1000,12])
    flowM = flowM + (varVal['flow_rate'])*varVal['no_layers']
    np.save(lPath+"\\temporary\\flowMAT.npy", flowM)
    
    #find the highest iteration in the MySQL table
    #the input to sim, through SQL
    conn,cursor = cnt_X('NCC')
    #looks for other analysis of the same source geomertry
    here = """'%"""+MeshFile+"""%'"""
    here1 = """'%"""+BraidFile+"""%'"""
    query = "SELECT version FROM rtm_main where MeshFile like "+here+" and BraidFile like "+here1
    cursor.execute(query)
    #get results
    sd = []
    rows = cursor.fetchall()
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
    
    #Next version number - used for this analysis. Can be taken from MySQL, if
    #active.
    version = maxNo#32
    print(version)
    #File definition based on version number.
    if version < 10:
        vn = "00"+str(int(version))
    elif version <100:
        vn = "0"+str(int(version))
    else:
        vn = str(int(version))
    #Define the name of new RTM iteration.
    BraidSection = BraidFile.split("_")[3]
    RTMF = MeshFile+"_"+BraidSection+"_R"+vn
    RTMFile = RTMF+"_"+str(REP)
    
    #Upload input data
    query = "INSERT INTO rtm_main(MeshFile,BraidFile,RTMFile,resin,version,Injection_T,Tool_T,Injection_P,Vent_P,Flow_rate) VALUES("
    query += """'"""+MeshFile+"""','"""+BraidFile+"""','"""+RTMFile+"""','"""+resin+"""',"""+str(version)+""","""+str(varVal['inlet_temp'])+""","""+str(varVal['tool_temp'])+""","""+str(varVal['inlet_pressure'])+""","""+str(varVal['vent_pressure'])+""","""+str(varVal['flow_rate'])+""")"""
    print(query)
    cursor.execute(query)
    conn.commit()
    
    #close SQL handles 
    dc_X('NCC',conn,cursor)
    
    #Create main input file for visual-RTM.
    STRx = MeshFile+"---"+RTMFile+"---"+resin+"---"+str(varVal['inlet_temp'])+"---"+str(varVal['tool_temp'])+"---"+str(varVal['inlet_pressure'])+"---"+str(varVal['vent_pressure'])+"---"+str(varVal['flow_rate'])+"---"+str(st393)+"---"+str(vn)+"---"+str("0")+"---"+str(RTMF)+"---"+str(varVal['no_layers'])+"---"+str(varVal['span'])
    with open("Temporary\\RTM_in.txt", "w") as text_file:
        text_file.write(STRx)
        
    
    #The list of surfaces is created with their 3D coordinates.
    #Can be hashed if the same part is being re-analysed.
    cmd("VEBatch -activeconfig Trade:CompositesandPlastics -activeapp VisualRTM -sessionrun "+lPath+"\\RTM_surfaces.py")
    

    #Only for troubleshooting.
    surf_mat = np.load(lPath+"\\temporary\\RTM_surfaces.npy")
    c = np.size(surf_mat,0)
    print(c,"how many elements?")
    
    #This is the main section, runs the visual-rtm model generation script.
    cmd("VEBatch -activeconfig Trade:CompositesandPlastics -activeapp VisualRTM -sessionrun "+lPath+"\\RTM_toolbox.py")
    cmd2("VEBatch -activeconfig Trade:CompositesandPlastics -activeapp VisualRTM -sessionrun "+lPath+"\\RTM_run.py",RTMFile)
    
    #For shorter runs RTM_lil_toolbox can be used. (#REP must be adjusted manually)
    #REP=6
    #RTMFile = RTMF+"_"+str(REP)
    #cmd2("VEBatch -activeconfig Trade:CompositesandPlastics -activeapp VisualRTM -sessionrun D:\\IDPcode\\SpecialRTMTestIDP\\IDP_zip_2.0\\IDPcode\\RTM_lil_toolbox.py",RTMFile)

    
    #Do post processing
    results = False
    while results == False:
        try: 
            maxFill,I_time = RTM_postProc.outputS1(RTMFile)
            results = True
        except:
            print("Result not available yet x, waiting")
            time.sleep(30)
            pass
        

    #When flow rate adjustments do not improve flow front, "Unmoved" is increased
    #which makes the simulaiton progress with imperfect flow front.
    #UNmoved = 0
    
    #the following section is used for flow front improvement, isn't really needed
    '''
    # Add the looping in case of unfilled.
    # Current method attempts to make the flow front more uniform.
    if maxFill < 99:
        FF_check = False
    else:
        FF_check = True
    while FF_check == False:
        RTMFile = RTMF+"_"+str(REP)
        print(type(RTMFile),"RTMFile",RTMFile)
        print(type(I_time),"I_time",I_time)
        FF_check, UNmoved = RTM_postProc.ff_check(RTMFile,I_time,UNmoved,RTMF)
        print("Unmoved:",UNmoved)
        if FF_check == False:
            #if ff_check revealed issue the simulation is to be re-run with new flow_front velocities
            
            #delete old flow result file here:
            fif = RTMFile+".log"          
            path = 'D:\\IDPcode\\pamrtm\\mainSimFiles\\'
            for i in os.listdir(path):
                if os.path.isfile(os.path.join(path,i)) and str(fif) in i:
                    shutil.move(os.path.join("D:\\IDPcode\\pamrtm\\mainSimFiles\\",i), os.path.join("D:\\IDPcode\\pamrtm\\mainSimFiles\\trash\\", i))
            REP = REP + 1
            RTMFile = RTMF+"_"+str(REP)
            #Create main input file for visual-RTM.
            STRx = MeshFile+"---"+RTMFile+"---"+resin+"---"+str(I_T)+"---"+str(T_T)+"---"+str(I_P)+"---"+str(V_P)+"---"+str(FR)+"---"+str(st393)+"---"+str(vn)+"---"+str("0")+"---"+str(RTMF)
            with open("Temporary\\RTM_in.txt", "w") as text_file:
                text_file.write(STRx)
            for i in os.listdir(path):
                if os.path.isfile(os.path.join(path,i)) and 'FILLING_FACTOR' in i:
                    shutil.move(os.path.join("D:\\IDPcode\\pamrtm\\mainSimFiles\\",i), os.path.join("D:\\IDPcode\\pamrtm\\mainSimFiles\\trash\\", i))
            #Run the same simulation with altered flow-rate matrix.
            cmd2("VEBatch -activeconfig Trade:CompositesandPlastics -activeapp VisualRTM -sessionrun D:\\IDPcode\\RTM_lil_toolbox.py",RTMFile)
            results = False
            while results == False:
                try: 
                    maxFill,I_time = RTM_postProc.outputS1(RTMFile)
                    results = True
                except:
                    print("Result not available yet, waiting")
                    time.sleep(30)
                    pass
    '''        

    simTime = time.time() - st393
    cnnW,crrW = cnt_X('NCC')
    #stores relevant results of the FE analysis
    query = "UPDATE rtm_main SET sim_runtime = "+str(simTime)+""" WHERE (MeshFile = '"""+MeshFile+"""') and version = """+vn+";"
    crrW.execute(query)
    cnnW.commit()
    query = "UPDATE rtm_main SET infusionTime = "+str(I_time)+""" WHERE (MeshFile = '"""+MeshFile+"""') and version = """+vn+";"
    crrW.execute(query)
    cnnW.commit()
    query = "UPDATE rtm_main SET infusionPercentage = "+str(maxFill)+""" WHERE (MeshFile = '"""+MeshFile+"""') and version = """+vn+";"
    crrW.execute(query)
    cnnW.commit()
    #close SQL handles 
    dc_X('NCC',cnnW,crrW)
    
    print("Total RTM sim time:--- %s seconds ---" % (time.time() - st393))
    #mf,time = outputS1()
    #print("Fill:",mf)
    #print("Infusion time:",time)
    #
    
    #unused?
    #RTM_postProc.cmdReach(RTMFile)
    #with open(lPath+"\\pamrtm\\mainSimFiles\\FILLING_FACTOR124.txt", "r") as fin:
    #    data = fin.read().splitlines(True)
    #with open(lPath+'\\pamrtm\\mainSimFiles\\FILLING_FACTOR125.txt', 'w') as fout:
    #    fout.writelines(data[14:])
    
    return(RTMFile)

#mRTM("IDP_spar_A036_M001","IDP_spar_A036_B001","Hexion_9600" ,410,300,float(200000000),10,0.000001,10)

