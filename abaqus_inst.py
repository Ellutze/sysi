import win32com.client.dynamic
import numpy as np
import shutil
from general_utils import foil_to_spar
import numpy as np
import os
import math
from math_utils import GlobalToLocal

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)
    
def ashape():
    from part import *
    from material import *
    from section import *
    from assembly import *
    from step import *
    from interaction import *
    from load import *
    from mesh import *
    from optimization import *
    from job import *
    from sketch import *
    from visualization import *
    from connectorBehavior import *
    
    with open("D:\\IDPcode\\temporary\\CAP.txt", "a") as text_file:
        text_file.write("Initiated abaqus model generation.\n")

    #input file - instead function arguments - which are not possible due to the command line passing
    fl = open("D:\\IDPcode\\Temporary\\fe_in.txt", "rt")
    flstr = fl.read() 
    FeFile = flstr.split("---")[1]
    MeshFile = flstr.split("---")[0]+"_JK"
    NL = int(float(flstr.split("---")[2]))
    fN = float(flstr.split("---")[3])
    meshType = flstr.split("---")[4]
    mesh_size= float(flstr.split("---")[5])
    XSS = int(flstr.split("---")[6])
    
    #open the iges file required for analysis
    if meshType == "CATIA":
        #this section only works when pre-mesh geometry is imported
        igs = "D:\\IDPcode\\CatiaFiles\\MeshFiles\\"+MeshFile+".igs"
        mdb.openIges(igs, msbo=False, scaleFromFile=OFF, trimCurve=DEFAULT)
        #mesh the part, only for purposes of abaqus, the shape should already be discretized into elements
        #the only reason to increase the element numbers here is for more precise assignment of material properties, the FE calculation itself should not improve
        mdb.models['Model-1'].PartFromGeometryFile(combine=False, convertToAnalytical=1, dimensionality=THREE_D, geometryFile=mdb.acis, name='x', stitchEdges=1, stitchTolerance=1.0, type=DEFORMABLE_BODY)
        #mesh division allows for more fidelity in assigning manufacturing material properties
        MeshDivision = 1  #changing this doesnt work now, the spheres allocation are defined  for default ("1") mesh division
        mdb.models['Model-1'].parts['x'].seedEdgeByNumber(constraint=FINER, edges=mdb.models['Model-1'].parts['x'].edges.getSequenceFromMask(('[#ffffffff:250 #3fffffff ]', ), ), number=MeshDivision)
        mdb.models['Model-1'].parts['x'].generateMesh()
    elif meshType == "numimesh":
        #the default version of mesh, faster than CATIA.
        #Orphan mesh is uploaded with this option.
        mdb.models['Model-1'].PartFromInputFile(inputFileName="D:\\IDPcode\\catiafiles\\meshfiles\\"+MeshFile+".inp")

    with open("D:\\IDPcode\\abaqusfiles\\cp.txt", "a") as text_file:
            text_file.write("File imported.\n")   
    #retreives the material properties calculated by cnn_main
    with open("Temporary\\BraidData.csv",'r')as ins:
        for line in ins:
             #membrane properties ==> format ==> [refNo,Exm,Eym,Gxym,vxym,vyxm,mxm,mym,dens]
             _matNO = float(line.split(",")[0])
             _matE1 = float(line.split(",")[1])
             _matE2 = float(line.split(",")[2])
             _matG = float(line.split(",")[3])
             _matPoi = float(line.split(",")[4])
             #these are assumed to be the same as G for now, makes minimal effect (checked)
             _matM1 = float(line.split(",")[3])
             _matM2 = float(line.split(",")[3])    
             #just for the shear modulus test, delete later:
             _matM1 = 1000
             _matM2 = 1000        
             
             #density
             _matD = float(line.split(",")[8])
             #thickness (currently constant)
             LT = float(line.split(",")[9])
             #variable in mdb.function - build function as script - create new material
             BuildMat1 = """mdb.models['Model-1'].Material(name='Material-"""+str(int(_matNO))+"""')"""   
             #exectue the script as mdb. function
             exec(BuildMat1)
             #assign new material properties to materiasl created
             BuildMat = '''mdb.models['Model-1'].materials['Material-'''+str(int(_matNO))+''''].Elastic(table=(('''+str(_matE1)
             BuildMat += ''', '''+str(_matE2)+''', '''+str(_matPoi)+''', '''+str(_matG)+''', '''+str(_matM1)+''', '''+str(_matM2)+'''), ), type=LAMINA)'''
             exec(BuildMat)
             BuildMat2 = """mdb.models['Model-1'].materials['Material-"""+str(int(_matNO))+"""'].Density(table=(("""+str(_matD)+""", ), ))"""
             exec(BuildMat2)

    #minimum of two layers have to be assignmed
    #therefore the braided layer is defined by two unidirectional layers of provided properties
    #oritentation is kept 0 - the braid angles are accounted for in the properties calculated for this (principle) direction
    
    #under construction: multi layer option addition
    with open("D:\\IDPcode\\abaqusfiles\\cp.txt", "a") as text_file:
        text_file.write("Materials defined.\n")
    
    #the layers inputed are always 2, so the number of layers and thickness are translated into total thickness which is halfed
    InThickness = LT*NL/2
    mdb.models['Model-1'].CompositeShellSection(idealization=NO_IDEALIZATION, integrationRule=SIMPSON, layup=(SectionLayer(thickness=InThickness, \
    orientAngle=0, material='Material-1'),SectionLayer(thickness=InThickness, \
    orientAngle=0, material='Material-1')), name='Section-1', \
    poissonDefinition=DEFAULT, preIntegrate=OFF, symmetric=False, temperature= GRADIENT, thicknessModulus=None, thicknessType=UNIFORM, useDensity=OFF)
    
    #creates instance (the reference is 'n2' in capitals ==> 'N2')
    mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
    mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='n2', part=mdb.models['Model-1'].parts['X'])
    #mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='X-1', part= mdb.models['Model-1'].parts['X'])

    
    #select all nodes as boundary condition - to extract the nodes through input file    
    #mdb.models['Model-1'].rootAssembly.Set(name='Set-1', vertices=mdb.models['Model-1'].rootAssembly.instances['n2'].vertices.getSequenceFromMask(('[#ffffffff:1500 #fffffff ]', ), ))
    #mdb.models['Model-1'].parts['X'].Set(name='Set-1', nodes= mdb.models['Model-1'].parts['X'].nodes[0:4655])
    mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
    mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='X-1', part=mdb.models['Model-1'].parts['X'])
            
    #set full boundary condition on everything - irrelevant - not used for final analysis
    #mdb.models['Model-1'].DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='BC-1', \
    #region=mdb.models['Model-1'].rootAssembly.sets['Set-1'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)
    
    mdb.models['Model-1'].rootAssembly.Set(name='Set-1', nodes=mdb.models['Model-1'].rootAssembly.instances['X-1'].nodes[0:4655])
    mdb.models['Model-1'].DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='BC-1', \
    region=mdb.models['Model-1'].rootAssembly.sets['Set-1'], u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)
        
    #any force applied - irrelevant - not used for final analysis - only used for input file nodal information extraction
    mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
    #if meshType == "CATIA":
    mdb.models['Model-1'].rootAssembly.Set(name='Set-2', vertices=mdb.models['Model-1'].rootAssembly.instances['n2'].vertices.findAt(((58.099072, 7.548677, 500.0), )))
    mdb.models['Model-1'].ConcentratedForce(cf2=-150.0, createStepName='Step-1', distributionType=UNIFORM, field='', localCsys=None, name='Load-1', region=\
    mdb.models['Model-1'].rootAssembly.sets['Set-2'])
     
    mdb.models['Model-1'].parts['X'].Set(elements=mdb.models['Model-1'].parts['X'].elements[0:4620], name='Set-4')
    mdb.models['Model-1'].parts['X'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=\
    mdb.models['Model-1'].parts['X'].sets['Set-4'], sectionName='Section-1', thicknessAssignment=FROM_SECTION)
    
    
    #create an input file, just so that node pos. informaiton can be extracted
    mdb.Job(atTime=None, contactPrint=OFF, description='ajob#', echoPrint=OFF, explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, \
    memory=90, memoryUnits=PERCENTAGE, model='Model-1', modelPrint=OFF, multiprocessingMode=DEFAULT, name='Task-BC', nodalOutputPrecision=SINGLE, \
    numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type= ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
    mdb.jobs['Task-BC'].submit(consistencyChecking=OFF)
    
    #under construction: multi layer option addition
    with open("D:\\IDPcode\\abaqusfiles\\cp.txt", "a") as text_file:
        text_file.write("Fake job created.\n")
   
    #use the input file for the job above to extract nodal information 
    #if meshType == "CATIA":
    fl = open("D:\\IDPcode\\Task-BC.inp", "rt")
    #if meshType == "numimesh":
    #    fl = open("D:\\IDPcode\\catiafiles\\meshfiles\\"+MeshFile+".inp","rt")
    flstr = fl.read() 
    #this gets the section of document with node numbers and x,y,z coordinates
    fl_node = flstr.split("*Node")[1]
    fl_node = fl_node.split("*Element")[0]
    
    #writes the section of input file into separate text file, with each line corresponding to a node
    with open("Temporary\\node_list.txt", "w") as text_file:
        text_file.write(fl_node)
        
    #if meshType == "CATIA":
        #delete all boudnary condition and corresponding set
    del mdb.models['Model-1'].boundaryConditions['BC-1']
    del mdb.models['Model-1'].rootAssembly.sets['Set-1']
    
    #deletes the original assignment of set and material, to be replaced by zones with varying material properties
    del mdb.models['Model-1'].parts['X'].sectionAssignments[0]
    
    #with+for loop create two matrices:
    #node_mat is a all node matrix
    #bc_mat is matrix of all nodes which lie at z=0
    node_mat = np.array([[0,0,0,0]])
    bc_mat = np.array([[0,0,0]])
    with open("Temporary\\node_list.txt",'r')as ins:
        for line in ins:
            if "," in line: 
                node_matNO = float(line.split(",")[0])
                node_matX = float(line.split(",")[1])
                node_matY = float(line.split(",")[2])
                node_matZ = float(line.split(",")[3])
                node_mat2 = np.array([[node_matNO,node_matX,node_matY,node_matZ]])
                node_mat = np.concatenate((node_mat, node_mat2), axis=0)
                #to account for small rounding error nodes are selected around the precise 0 location
                if -0.01 < node_matZ < 0.01:
                    node_mat3 = np.array([[node_matX,node_matY,node_matZ]])
                    bc_mat = np.concatenate((bc_mat, node_mat3), axis=0)
        #fixes the issue of first line being always (0,0,0) - non representative of model
        node_mat = np.delete(node_mat, (0), axis=0)
        bc_mat = np.delete(bc_mat, (0), axis=0)
    
    #uses the "fake" input file to obtain element numbers with node associations
    fl_element = flstr.split("type=S4R")[1]
    fl_element = fl_element.split("*Nset")[0]
    
    #stores the element list in text file
    with open("Temporary\\ele_list.txt", "w") as text_file:
        text_file.write(fl_element)
    
    #uses the element text file to create well ordered matrix
    ele_mat = np.array([[0,0,0,0,0]])
    with open("Temporary\\ele_list.txt",'r')as ins:
        for line in ins:
            #the "e" accounts for Schrodingers elements, the triangular elements that only exist/not-exist after being observed
            #Isn't Abaqus great?
            if "," in line and "e" not in line: 
                ele_matNO = float(line.split(",")[0])
                ele_mat1 = float(line.split(",")[1])
                ele_mat2 = float(line.split(",")[2])
                ele_mat3 = float(line.split(",")[3])
                ele_mat4 = float(line.split(",")[4])
                #creates one line of the element information matrix
                ele_matL = np.array([[ele_matNO,ele_mat1,ele_mat2,ele_mat3,ele_mat4]])
                ele_mat = np.concatenate((ele_mat, ele_matL), axis=0)
            #prevents for observation of Schrodingers element
            if "e" in line:
                break
        #delete the base line of ele_mat - zeros line
        ele_mat = np.delete(ele_mat, (0), axis=0)
        
    #under construction: multi layer option addition
    with open("D:\\IDPcode\\abaqusfiles\\cp.txt", "a") as text_file:
        text_file.write("Nodes and element matrices created.\n")

    elPOS = np.zeros([1,4])
    for row in ele_mat:
        #for each element ...
        i = 0 
        X = []
        Y = []
        Z = []
        node1 = row[1]
        node2 = row[2]
        node3 = row[3]
        node4 = row[4]
        #... find position of each node and average the coordinates
        for line in node_mat:
            if line[0] == node1 or line[0] == node2 or line[0] == node3 or line[0] == node4:
                X.append(line[1])
                Y.append(line[2])
                Z.append(line[3])
                
        elPOSloc = np.matrix([float(row[0]),mean(X),mean(Y),mean(Z)])
        elPOS = np.concatenate((elPOS,elPOSloc),0)
    #gives positions of elements in x,y,z (average of the corner coordinates)
    elPOS = np.delete(elPOS, (0), axis=0)

    #command is build to apply boundary condition on all nodes at z=0
    
    mdb.models['Model-1'].rootAssembly.Set(name='Set-3', nodes=\
    mdb.models['Model-1'].rootAssembly.instances['n2'].nodes[0:XSS]+\
    mdb.models['Model-1'].rootAssembly.instances['X-1'].nodes[0:XSS])
    mdb.models['Model-1'].DisplacementBC(amplitude=UNSET, createStepName='Step-1', \
    distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name=\
    'BC-569', region=mdb.models['Model-1'].rootAssembly.sets['Set-3'], u1=0.0, \
    u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0)
    #del mdb.models['Model-1'].boundaryConditions['BC-3']
    
    #under construction: multi layer option addition
    with open("D:\\IDPcode\\abaqusfiles\\cp.txt", "a") as text_file:
        text_file.write("Boundary condition defined.\n")
    
    #bring in the segmentation (boundaries) matrix -- section, x max, x min, y max, y min, z max, z min
    #these are provided in local coordinate systems, for each sections. 
    #The details of coordinate systems are provided separately, further below.
    seg_mat = np.loadtxt(open("Temporary\\BraidSegments.csv", "rb"), delimiter=",")
    
    with open("D:\\IDPcode\\temporary\\CAP.txt", "a") as text_file:
        text_file.write("Adjustment here:"+str(seg_mat)+"\n")
        
    #delete previous section assignment
    del mdb.models['Model-1'].sections['Section-1']
    
    #find local elPOS    
    #import centreline positions 
    secPTS = np.loadtxt(open("Temporary\\secPTS.csv", "rb"), delimiter=",")
  
    #import centreline z vectors
    secVECz = np.loadtxt(open("Temporary\\secVECz.csv", "rb"), delimiter=",")
  
    #import centreline y vectors   
    secVECy = np.loadtxt(open("Temporary\\secVECy.csv", "rb"), delimiter=",")

    #calculate the third vector for coordinate transform
    
    #sphere_rad is now variable based on span
    SPH = np.array([[0,0]])
    with open("Temporary\\spheres.csv",'r')as ins:
        for line in ins:
            SPHz = float(line.split(",")[0])
            SPHs = float(line.split(",")[1])
            SPH1 = np.matrix([SPHz,SPHs])
            SPH = np.concatenate((SPH, SPH1), axis=0)
        SPH = np.delete(SPH, (0), axis=0)    
    
    #used to inform on potential unused elements
    striga = "All elements found:"
    #the cnt is used to name sets, assign material and section
    cnt = 0
    offs = 300
    lenSM = np.size(seg_mat,0)
    lenEP = np.size(elPOS,0)
    ii = 0
    #ErrRat is a troubleshooting ratio - it helps fit elements that are problematic
    ErrRat = 1
    #builds faces list to be later used in a command
    while ii < lenSM:
        cnt = cnt + 1
        
        #Tranform into correct coordinate system
        v = math.floor(ii/12)
        secVECx = np.cross(secVECy[v,:],secVECz[v,:])
        cSYS2 = np.array(([secVECx[0],secVECx[1],secVECx[2]],[secVECy[v,0],secVECy[v,1],secVECy[v,2]],[secVECz[v,0],secVECz[v,1],secVECz[v,2]]))
        point1 = np.array([0,0,0])
        point2 = np.array([secPTS[v,0],secPTS[v,1],secPTS[v,2]])
        cSYS1 = np.array(([1,0,0],[0,1,0],[0,0,1]))
        
        #the lenEP changes as the elements are assigned, hence within the first loop
        #lenEP = np.size(elPOS,0)
        count = 0
        i = 0
        #this loop goes throug all elements and assigns the correct ones to the segment
        while i < lenEP:
            #the point to be translated to local coordinate system, which corresponds to provided segments
            GCP = np.array([float(elPOS[i,1]),float(elPOS[i,2]),float(elPOS[i,3])])
            elPOSlocal = GlobalToLocal(point1,point2, cSYS1,cSYS2,GCP)
            elPOSlocal[0] = elPOSlocal[0]*ErrRat
            elPOSlocal[1] = elPOSlocal[1]*ErrRat
                    
            #either assign element and delete row, or go to next element
            if (seg_mat[ii,2] <= elPOSlocal[0] < seg_mat[ii,1]) and (seg_mat[ii,4] <= elPOSlocal[1] < seg_mat[ii,3]) and (seg_mat[ii,6] < elPOS[i,3] <= seg_mat[ii,5]):
                #find the size of shphere at local span location
                iv = 1
                sphere_rad = 0
                while iv < SPH.shape[0]:
                    sph = SPH[iv-1,1]
                    if iv == (SPH.shape[0]-1):
                        sph = SPH[iv,1]
                    if SPH[iv-1,0] <= elPOS[i,3] <= SPH[iv,0] and sphere_rad < sph:
                        sphere_rad = sph
                    iv = iv+1
                
                if count == 0:
                    fcs = mdb.models['Model-1'].parts['X'].elements.getByBoundingSphere(center = (elPOS[i,1],elPOS[i,2],elPOS[i,3]), radius=sphere_rad)
                #all but the first face
                else:
                    fcs = fcs + (mdb.models['Model-1'].parts['X'].elements.getByBoundingSphere(center = (elPOS[i,1],elPOS[i,2],elPOS[i,3]), radius=sphere_rad))
                count = count + 1
                #delete the row
                elPOS = np.delete(elPOS, (i), axis=0) 
                lenEP = lenEP-1
            else:
                i = i + 1
                
        with open("D:\\IDPcode\\abaqusfiles\\cp.txt", "a") as text_file:
            text_file.write("Set "+str(ii)+" is being assigned.\n")
        #this if prevents reassignment of empty sets, when ErrRat forces new loop 
        if count != 0:
            #namin of sets starts at 300 to avoid cross-referencing 
            cnt300 = cnt + offs
            SetName = "Set-"+str(cnt300)
            #the faces group defined above is used to create set
            mdb.models['Model-1'].parts['X'].Set(elements = fcs, name=SetName)
        
            #build command to assign the set just created and create section
            amBuild = """mdb.models['Model-1'].CompositeShellSection(idealization=NO_IDEALIZATION, integrationRule=SIMPSON, layup=(SectionLayer(thickness="""+str(InThickness)+""","""
            amBuild += """orientAngle=0, material='Material-"""+str(cnt)+"""'),SectionLayer(thickness="""+str(InThickness)+""","""
            amBuild += """orientAngle=0, material='Material-"""+str(cnt)+"""')), name='Section-"""+str(cnt300)+"""',"""
            amBuild += "poissonDefinition=DEFAULT, preIntegrate=OFF, symmetric=False, temperature= GRADIENT, thicknessModulus=None, thicknessType=UNIFORM, useDensity=OFF)"
            exec(amBuild)
        
            #section and set assignment to part
            ssBuild = """mdb.models['Model-1'].parts['X'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region="""
            ssBuild += """mdb.models['Model-1'].parts['X'].sets['Set-"""+str(cnt300)+"""'], sectionName='Section-"""+str(cnt300)+"""', thicknessAssignment=FROM_SECTION)"""
            exec(ssBuild)
            #after assigning faces return ErrRat to base value
            ErrRat = 1
        ii = ii + 1
        if lenSM == ii:
            #this is used to correct for unassigned regions
            if np.size(elPOS,0) > 0:
                ii = 0
                offs = 600
                cnt = 0
                ErrRat = 1.1*ErrRat
    
    #this is used to check for unassigned elements, the unassigned elements will be shown in the troubleshooting.txt file
    STRx = str(lenEP)
    STRx += "________________________"+str(elPOS)
    striga = striga+str(elPOSlocal)
    STRx += "_______"+striga
    with open("Temporary\\TROUBLESHOOTING.txt", "w") as text_file:
        text_file.write(STRx)
      
    #if meshType == "CATIA":
        #the previously applied force and correspond set are deleted
    del mdb.models['Model-1'].loads['Load-1']
    del mdb.models['Model-1'].rootAssembly.sets['Set-2']
    
    with open("D:\\IDPcode\\abaqusfiles\\cp.txt", "a") as text_file:
        text_file.write("Deletion of unused settings.\n")
    
    #the all node matrix is filtered for nodes at the tip of the spar
    node_mat = np.delete(node_mat, (0), axis=1)
    span = max(node_mat[:,2])
    rows = node_mat.shape[0]
    f_mat = np.array([[0,0,0]])
    i = 0
    while i < rows:
        if (span-20) <node_mat[i,2] < (span+5):
            local_mat = np.array([[node_mat[i,0],node_mat[i,1],node_mat[i,2]]])
            f_mat = np.concatenate((f_mat,local_mat),axis=0)
        i = i + 1
    
    #force is applied on all nodes at the end of the spar
    rows = f_mat.shape[0]
    i = 0 
    while i < rows:
        if i == 0:
            vrc = mdb.models['Model-1'].rootAssembly.instances['n2'].nodes.getByBoundingSphere(center = ((f_mat[i,0]),(f_mat[i,1]),(f_mat[i,2])), radius=0.05)
        #all but the first face
        else:
            vrc = vrc + mdb.models['Model-1'].rootAssembly.instances['n2'].nodes.getByBoundingSphere(center = ((f_mat[i,0]),(f_mat[i,1]),(f_mat[i,2])), radius=0.05)
            count = count + 1
        i = i + 1
                
    mdb.models['Model-1'].rootAssembly.Set(name='Set-22', nodes=vrc)

    with open("D:\\IDPcode\\abaqusfiles\\cp.txt", "a") as text_file:
        text_file.write("Set for force application created.\n")
    #troubleshooting broken section 22
    #STRx = BuildCommand
    #with open("Temporary\\22command.txt", "w") as text_file:
    #    text_file.write(STRx)
    
    
    mass = mdb.models['Model-1'].parts['X'].getMassProperties()['mass']
    with open("Temporary\\mass_out.txt", "w") as text_file:
        text_file.write(str(mass))
        #text_file.write("%20s%20.6f" % ("Mass :", mass))
    
    #exec(BuildCommand)
    #applies force on the set created above
    mdb.models['Model-1'].ConcentratedForce(cf2=fN, createStepName='Step-1', distributionType=UNIFORM, field='', localCsys=None, name='Load-5', region=\
    mdb.models['Model-1'].rootAssembly.sets['Set-22'])
       
    #the actual job is run, with correct BC and force
    
    mdb.Job(atTime=None, contactPrint=OFF, description='ajob#', echoPrint=OFF, explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, \
    memory=90, memoryUnits=PERCENTAGE, model='Model-1', modelPrint=ON, multiprocessingMode=DEFAULT, name='Task-1', nodalOutputPrecision=SINGLE, \
    numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type= ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
    mdb.jobs['Task-1'].submit(consistencyChecking=OFF)
    
    with open("D:\\IDPcode\\abaqusfiles\\cp.txt", "a") as text_file:
        text_file.write("Job Created and submited.\n")
    
    #the mdb file is saved for reference, might not be required in the future (switch off during looping?)
    filesave = "D:\\IDPcode\\AbaqusFiles\\"
    filesave = filesave + FeFile +".cae"
    mdb.saveAs(filesave)
    fl.close()

#This function has to be run upon script opening as it is run through command line.
ashape()


