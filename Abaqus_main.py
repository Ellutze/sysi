from abaqus_cmd import cmd
#from mysql.connector import MySQLConnection, Error
from IDP_databases import cnt_X,dc_X
#from python_mysql_dbconfig import read_db_config
#from IDP_cheats import togglePulse
import shutil
import os
import time
import cnn_main

def is_empty(any_structure):
    #this functions checks if a list (or suchlike) is empty, used below in abaMain
    if any_structure:
        return False
    else:
        return True

def abaMain(BraidFile,MeshFile,CADfile,varVal,meshType,XSS):
    lPath = os.path.dirname(os.path.abspath(__file__))
    st986 = time.time()
    #runs from python, it is used to run other abaqus related scripts through command line
    #SQL is used here to store iteration data, while the inputs and outputs to command line scripts are done through temporary text files
    NL = varVal['no_layers']
    
    #the setup - variables etc.
    matrix = varVal["matrix"]
    fibre =varVal["reinforcement"]
    Material = matrix +"||"+fibre
    spanwise_sections = cnn_main.aba_inputProp(BraidFile,CADfile,varVal)
    #other variables
    fN = -1 #total Newton force applied at the tip
    
    #the input to sim, through SQL
    cnnA,crrA = cnt_X('NCC')
    
    #looks for other analysis of the same source geomertry
    here = """'%"""+MeshFile+"""%'"""
    here1 = """'%"""+BraidFile+"""%'"""
    query = "SELECT version FROM fe_inst where MeshFile like "+here+" and BraidFile like "+here1
    #print(query)
    crrA.execute(query)
    #get results
    sd = []
    rows = crrA.fetchall()
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
    
    #file definition based on version number
    if version < 10:
        vn = "00"+str(int(version))
    elif version <100:
        vn = "0"+str(int(version))
    else:
        vn = str(int(version))
    BraidSection = BraidFile.split("_")[3]
    FeFile = MeshFile+"_"+BraidSection+"_F"+ vn
    
    #input information into SQL
    query = "INSERT INTO fe_inst(MeshFile,BraidFile,material,FeFile,version,no_layers,force_N) VALUES("
    query += """'"""+MeshFile+"""','"""+BraidFile+"""','"""+Material+"""','"""+FeFile+"""',"""+str(version)+""","""+str(NL)+""","""+str(fN)+""")"""
    crrA.execute(query)
    cnnA.commit()
    #close SQL handles 
    dc_X('NCC',cnnA,crrA)
    
    #all input information for pre-processing passed through this text file
    STRx = MeshFile +"---"+FeFile+"---"+str(NL)+"---"+str(fN)+"---"+meshType+"---"+str(varVal["mesh_size"])+"---"+str(XSS)
    with open("Temporary\\fe_in.txt", "w") as text_file:
        text_file.write(STRx)
    
    #run pre-processing abaqus script
    cmd("abaqus cae noGUI=abaqus_inst.py")
    
    #move generated files into temporary folder, from the script folder
    #path = 'D:\\IDPcode\\'
    for i in os.listdir(lPath):
        if os.path.isfile(os.path.join(lPath,i)) and 'Task-1.odb' in i:
            shutil.move(os.path.join(lPath+"\\",i), os.path.join(lPath+"\\Temporary\\", i))
    
    #run post-processing abaqus script
    cmd("abaqus cae noGUI=abaqus_postProc.py")
    
    #obtains relevant information from abaqus results
    fl = open(lPath+"\\Temporary\\fe_out.txt", "rt")
    flstr = fl.read() 
    flval = float(flstr)
    flval = round(flval, 3)
    fl = open(lPath+"\\Temporary\\mass_out.txt","rt")
    flstr = fl.read() 
    flval2 = float(flstr)
    mass = flval2
    
    cnnA,crrA = cnt_X('NCC')
    
    #stores relevant results of the FE analysis
    query = "UPDATE fe_inst SET max_deflection = "+str(flval)+""" WHERE (MeshFile = '"""+MeshFile+"""') and version = """+str(version)+";"
    crrA.execute(query)
    cnnA.commit()
    query = "UPDATE fe_inst SET mass = "+str(flval2)+""" WHERE (MeshFile = '"""+MeshFile+"""') and version = """+str(version)+";"
    crrA.execute(query)
    cnnA.commit()
    query = "UPDATE fe_inst SET spanwise_sections = "+str(spanwise_sections)+""" WHERE (MeshFile = '"""+MeshFile+"""') and version = """+str(version)+";"
    crrA.execute(query)
    cnnA.commit()
    query = "UPDATE fe_inst SET simulation_time = "+str((time.time() - st986))+""" WHERE (MeshFile = '"""+MeshFile+"""') and version = """+str(version)+";"
    crrA.execute(query)
    cnnA.commit()
    
    #delete the output, to prevent it from showing on the next analysis if error occurs
    with open("Temporary\\fe_out.txt", "w") as text_file:
        text_file.write("")
    
    #close SQL handles 
    dc_X('NCC',cnnA,crrA)
    
    #move task-, .rpy, .sat and .rec files from script folder - empty trash folder manually (dont want to accidnetally move a script)
    for i in os.listdir(lPath):
        if os.path.isfile(os.path.join(lPath,i)) and '.rec' in i:
            shutil.move(os.path.join(lPath+"\\",i), os.path.join(lPath+"\\trash\\", i))
    for i in os.listdir(lPath):
        if os.path.isfile(os.path.join(lPath,i)) and '.rpy' in i:
            shutil.move(os.path.join(lPath+"\\",i), os.path.join(lPath+"\\trash\\", i))
    for i in os.listdir(lPath):
        if os.path.isfile(os.path.join(lPath,i)) and '.sat' in i:
            shutil.move(os.path.join(lPath+"\\",i), os.path.join(lPath+"\\trash\\", i))
    for i in os.listdir(lPath):
        if os.path.isfile(os.path.join(lPath,i)) and 'Task-' in i:
            shutil.move(os.path.join(lPath+"\\",i), os.path.join(lPath+"\\trash\\", i))
            
    path2 = lPath+'\\Temporary\\'
    for i in os.listdir(path2):
        if os.path.isfile(os.path.join(path2,i)) and 'Task-' in i:
            shutil.move(os.path.join(lPath+"\\Temporary\\",i), os.path.join(lPath+"\\trash\\", i))
    
    print("Total FEA time:--- %s seconds ---" % (time.time() - st986))
    return(flval,mass,FeFile)
    
#CADfile = "IDP_spariteration_A114_JK"
#BraidFile = "IDP_spariteration_A114_B001"
#MeshFile = "IDP_spariteration_A114_M001"
#abaMain(BraidFile,MeshFile,CADfile,1)
    
    

