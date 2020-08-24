from catia import ex1
import time
import numpy as np
import catia_mesh
from IDP_databases import cnt_X,dc_X
#from mysql.connector import MySQLConnection, Error
#from python_mysql_dbconfig import read_db_config
#from IDP_cheats import togglePulse
import os

def is_empty(any_structure):
    #this functions checks if a list (or suchlike) is empty, used below in abaMain
    if any_structure:
        return False
    else:
        return True
    
def SingleCAD(project,part,varVal):
    st1 = time.time()
    #chord_min = 0.175
    #chord_max = 0.4
    #tdm = str(time.strftime("%m"))
    #tdy = str(time.strftime("%y"))
    
    liikkee = project+"_"+part+"_"
    
    #Find previous versions of CAD for the same project, part and date
    #the input to sim, through SQL
    cnnB,crrB = cnt_X('NCC')
    #looks for other meshes with the same source geomertry
    here = """'%"""+liikkee+"""%'"""
    query = "SELECT iteration FROM SIM_CAD_iterations where RefInput like "+here
    #print(query)
    crrB.execute(query)
    #get results
    sd = []
    rows = crrB.fetchall()
    dc_X('NCC',cnnB,crrB)
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
    vni = maxNo + 1
    #2 stands for default radius of corners, should be made into iteratable variable
    #each "sectioned" defined by: span position, aerofoil, size multiplier (taper...), sweep, twist, dihedral
    CADfile = ex1(project,part,varVal,vni)

    print("--- %s seconds ---" % (time.time() - st1))
    return(CADfile)
    
def loopCAD():
    st1 = time.time()


    chord_min = 0.15
    chord_max = 0.3
    part = "SparIteration"
    project = "IDP"
    tdm = str(time.strftime("%m"))
    tdy = str(time.strftime("%y"))
    
    liikkee = project+"_"+part+"_"+tdy+tdm+"_"
    
    #Find previous versions of CAD for the same project, part and date
    #the input to sim, through SQL
    cnnB,crrB = cnt_X('NCC')
    #looks for other meshes with the same source geomertry
    here = """'%"""+liikkee+"""%'"""
    query = "SELECT version FROM mesh_list where CADfile like "+here
    #print(query)
    crrB.execute(query)
    #get results
    sd = []
    rows = crrB.fetchall()
    dc_X('NCC',cnnB,crrB)
    
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
    vni = maxNo + 1
    
    x = 1
    while x < 20:
        y = 0
        while y < 8:
            #each section defined by: span position, aerofoil, size multiplier (taper...), sweep, twist, dihedral
            sectioned = np.matrix([[0,"AerofoilCollection\\clarkYdata.dat",150,0,0,0],[(150),"AerofoilCollection\\clarkYdata.dat",150,2,0,0],[400,"AerofoilCollection\\clarkYdata.dat",100,0,(y/2),0],[500,"AerofoilCollection\\clarkYdata.dat",80,2,y,x]]) 
            ex1(project,part,sectioned,vni,chord_min,chord_max)
            vni = vni + 1
            y = y + 2
        x = x + 5
    print("--- %s seconds ---" % (time.time() - st1))
    
#below line for testing
#loopCAD()
def MeshOne(CADfile,spn,rnc):
    lPath = os.path.dirname(os.path.abspath(__file__))
    #this function assembles all meshing steps
    time1 = time.time()
    
    #next section only when run from here md0 = size cell lengthwise, md1 number of cells round the spar, 
    md = np.zeros(2)
    md[0] = spn

    #spar definition, passed from Mysql, for the particular automatically generated CAD
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
    
    np.save(lPath+'\\Temporary\\for_spheres', MD)
    
    print("---Meshing this part took: %s seconds ---" % (time.time() - time1))
    return(partDocument1,cse)
    
#Below line for testing
#MeshOne("IDP_SparIteration0204_1901_A001_JK",20,10)
    
def MultiMesh(CADfile,varVal):
    lPath = os.path.dirname(os.path.abspath(__file__))
    #configure SQL connection
    st118 = time.time()
    cnnB,crrB = cnt_X('NCC')
    #the loop is dormant - can be used to mesh multiple files after one-another
    #while x < 28:
    #the if function translates numbers into corresponding file name parts

    #pass in file name and mesh characteristics (size of elements span-wise and number of elements around cross section)
    #the two variables should change based on mesh sensitivity analysis? (maybe add at some point)
    
    # USE PERIMETER INFO TO SETUP THE MESH SIZE 
    
    query = """SELECT root_perimeter FROM arun where Cadfile = '"""+CADfile+"""' and root_perimeter is not null;"""
    crrB.execute(query)
    rows = crrB.fetchall()
    for row in rows:
        try:
            fd = float(row[0])
            #break
        except TypeError:
            print("We are DOOMED")
        
    
    span_ele_size = varVal['mesh_size'] #7 base for all optimisations before 13/09/2019 # originally span_ele_size
    # ROUND THIS TO CLOSEST FACTOR OF 2
    
    ned = fd/span_ele_size
    #round to closest multiplication of 2, has to be even for the number is halfed within the meshing simulation
    xs_seed = int(ned/2)*2
    partDocument1, count_span_el = MeshOne(CADfile,span_ele_size,xs_seed)
    
    #Find previous mesh verstions of the same CAD
    #the input to sim, through SQL
    
    #looks for other meshes with the same source geomertry
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
    #core part of CADfile name
    trimfile = CADfile.split("_")[0]+"_"+CADfile.split("_")[1]+"_"+CADfile.split("_")[2]+"_"
    
    #file definition based on version number
    if version < 10:
        vn = "00"+str(int(version))
    elif version <100:
        vn = "0"+str(int(version))
    else:
        vn = str(int(version))
    #create a MeshFile name from CadFile and mesh version
    MeshFile = trimfile +"M"+ vn
    
    #correct for calc error in number of spanwise elements
    count_span_el = count_span_el - 1
    #store Mesh information in SQL
    
    mTime = time.time() - st118
    query = "INSERT INTO mesh_list(CADfile,MeshFile,xs_seed,span_ele_size,version,meshing_time) VALUES("
    query += """'"""+CADfile+"""','"""+MeshFile+"""',"""+str(xs_seed)+""","""+str(count_span_el)+""","""+str(version)+""","""+str(mTime)+""")"""
    crrB.execute(query)
    cnnB.commit()
    
    #close SQL handles 
    dc_X('NCC',cnnB,crrB)
    #save the CADfile of the mesh (might not be necessary)
    silo = lPath+"\\CatiaFiles\\MeshFiles\\"+MeshFile+"_JK.CatPart"
    partDocument1.SaveAs(silo)
    #save the IGES file
    silo2 = lPath+"\\CatiaFiles\\MeshFiles\\"+MeshFile+"_JK.igs"
    partDocument1.ExportData(silo2, "igs")
    
    
    #x = x + 1
    return(MeshFile,span_ele_size,xs_seed)  
#MultiMesh("IDP_Spar_A136_JK")



    
    