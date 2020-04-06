#Uses cmd instead of cmd2 to prevent circular imports.
from RTM_cmd import cmd
import numpy as np
from math_utils import GlobalToLocal

#From stack-overflow
def Round_To_n(x, n):
    return round(x, -int(np.floor(np.sign(x) * np.log10(abs(x)))) + n)



##########################################
def outputS1(RTMfile):
    #This is the most basic post-processing tool, providing the fill time, and 
    #overall fill percentage. It also serves as a result availability check for
    #cmd2.
    fif = RTMfile+".log"
    
    #Open the standard .log file available with every visual-rtm simulation.
    eef = open("D:\\IDPcode\\pamrtm\\mainSimFiles\\"+fif, "rt")
    ee = eef.read() 
    prc = ee.count('%')
    i = 0
    maxFill=0
    #Loops through all the iterating fill information, finding the highest 
    #value reached.
    while i < (prc):
        eSTR = ee.split("%")[i]
        percentage = eSTR[-5:]
        percentage = float(percentage)
        if percentage > maxFill:
            maxFill = percentage
        i = i + 1
    print("filled:",maxFill,"%")
    
    #account for failed filling, but succesful simulation
    if ("filling stopped at" in ee) is True:
        #This is what happens when there is oscillating flow front or air 
        #entrapments.
        I_time = ee.split("filling stopped at ")[1]
        I_time = I_time.split(" seconds due ")[0]   
        print("Issue time:",I_time)
    elif (" Error " in ee) is True: 
        #This is what happens when there is visual-rtm error.
        I_time = "9999999999"   
        print("Sim fineshed due to error...")
        print("Issue time:",I_time)
    elif ("Filling finished at "in ee) is True:
        I_time = ee.split("Filling finished at ")[1]
        I_time = I_time.split(" seconds.")[0]   
        print("filling time:",I_time)  
    
    elif ("exe FINISHED "in ee) is True:
        I_time = "9999999999"
        print("The sim finished without full fill time.")
        print("Issue time:",I_time)
    else:   
        #This is what happens when filling is successful.
        #Also purposefully causes error when the above isn't satisfied but sim hasnt finished yet, improve!
        I_time = ee.split("Filling finished at ")[1]
        I_time = I_time.split(" seconds.")[0]   
        print("filling time:",I_time)
    eef.close()  
    return(maxFill,I_time)
    
    
    
    
    
def cmdReach(RTMfile):
    #cmdReach is used to get fill factors exported from post-processing menus
    #in visual-environment. Command line has to be used to access the data 
    #within the simulation.
    STRx = RTMfile+"---"+"getPhill(RTMfile)"
    with open("Temporary\\PP_request.txt", "w") as text_file:
        text_file.write(STRx)
    cmd("VEBatch -activeconfig Trade:CompositesandPlastics -activeapp VisualRTM -sessionrun D:\\IDPcode\\RTM_PPcmd.py")
    
    
def ifUnfi(RTMfile):
    #ifUnfi is a specilized post processign script for mesh-addition-iteration.
    with open("D:\\IDPcode\\pamrtm\\mainSimFiles\\FILLING_FACTOR124.txt", "r") as fin:
        data = fin.read().splitlines(True)
    with open('D:\\IDPcode\\pamrtm\\mainSimFiles\\FILLING_FACTOR125.txt', 'w') as fout:
        fout.writelines(data[14:])
        
    #Load the trimmed version of filling factors at last frame.
    matrix = np.loadtxt('D:\\IDPcode\\pamrtm\\mainSimFiles\\FILLING_FACTOR125.txt',usecols=range(2))
    i = 0 
    vrba = np.zeros([1,2])
    while i < np.size(matrix,0):
        #The filling factors between the two values before are considered the 
        #flow front.
        if 0.01 < matrix[i,1] < 0.95:
            vrba = np.concatenate((vrba,np.matrix([matrix[i,0],matrix[i,1]])),0)
        i = i + 1

    
    locaV = np.zeros([np.size(vrba,0),3])
    vrba = np.concatenate((vrba,locaV),1)
    vrba = np.delete(vrba, (0), axis=0)
    #import node matrix - with locations and match nodes ... 
    with open("D:\\IDPcode\\pamrtm\\mainSimFiles\\"+RTMfile+".inp") as nds:
        fl = nds.read()
        ff = fl.split("*NODE")[1]
        coord_mat = np.zeros([1,4])
        temp_mat = np.zeros([1,4])
        iiy = 0
        coms = ff.count(',')
        while iiy < coms:
            if iiy != 0:
                ex = ff.split(',')[iiy]
                ex = float(ex.split()[1])
            else:
                ex = ff.split(',')[iiy]
            #node number
            temp_mat[0,0] = float(ex)
            ex = ff.split(',')[iiy+1]
            #x value
            temp_mat[0,1] = float(ex)
            ex = ff.split(',')[iiy+2]
            #y value
            temp_mat[0,2] = float(ex)       
            if iiy != coms-3:
                ex = ff.split(',')[iiy+3]
                ex = float(ex.split()[0])
            else:
                ex = ff.split(',')[iiy+3]
                ex = float(ex)
            #z value
            temp_mat[0,3] = float(ex)
            coord_mat = np.concatenate((coord_mat, temp_mat), axis=0)
                
            #add to coord mat matrix
            iiy = iiy + 3
        #delete the first row of coord mat
        coord_mat = np.delete(coord_mat, (0), axis=0)

    #Match the coordinates to selected nodes.
    i = 0
    while i < np.size(vrba,0):
        ii = 0
        NODE = vrba[i,0]
        while ii < np.size(coord_mat,0):
            if NODE == coord_mat[ii,0]:
                #vrba[i,2:4] = coord_mat[ii,1:3]
                vrba[i,2] = coord_mat[ii,1]
                vrba[i,3] = coord_mat[ii,2]
                vrba[i,4] = coord_mat[ii,3]
                ii = ii + 99999999            
            ii = ii + 1
        i = i + 1

    #Find the minimal z coordinate node which is not fully filled.
    #This typically corresponds to the first air pocket.
    FF = min(vrba[:,4])
    
    #IP are the coordinates of the surface which requires mesh extension to.
    i = 0
    while i < np.size(vrba,0):
        if FF == vrba[i,4]:
            IP = vrba[i,2:]
            i = i + 9999999
        i = i + 1 
    
    #Importing the surface coordinate information
    surf_mat = np.load(r"D:\\IDPcode\\temporary\\RTM_surfaces.npy")
    print(np.size(surf_mat,0),"original surface matrix")

    surf_Alist = np.zeros([1,4])
    #Flow mesh is extended over the problematic area by 20mm.
    IP[0,2] = IP[0,2] + 20
    print(IP)
    i = 0 
    z = 400
    #n is the distance of elements searched for. If no elements are found, this
    #distance is extended. This should prevent diagonal elements to be found 
    #before direction z-direction elements.
    n = 3
    while z > 6:
        #Calculate the distance between a surface and current mesh path.
        dist = np.sqrt((surf_mat[i,1]-IP[0,0])**2 +(surf_mat[i,2]-IP[0,1])**2 +(surf_mat[i,3]-IP[0,2])**2 )
        #If the closest element in negative z-direction is found, add the surface
        #to matrix.
        if (dist < n) and (surf_mat[i,3] < IP[0,2]-2) and ((surf_mat[i,1]-IP[0,0])<2) and ((surf_mat[i,2]-IP[0,1])<2):
            print(surf_mat[i,:],"new surface")
            surf_Alist = np.concatenate((surf_Alist,np.matrix(surf_mat[i,:])),0)
            #surf_Alist.append(surf_mat[i,:])
            IP[0] = surf_mat[i,1:]
            surf_mat = np.delete(surf_mat, (i), axis=0)
            i = 0
            z= IP[0,2]
            n = 3
        i = i + 1
        #i needs to keep iterating until the mesh extends below z = 6.
        if i > (np.size(surf_mat,0)-2):
            i = 0
            n = n + 1
    surf_Alist = np.delete(surf_Alist, 0,axis=0)
    print(np.size(surf_Alist,0),"flow mesh surfaces")
    print(np.size(surf_mat,0),"new surface matrix")
    #Output new surfaces with mesh and the original surface matrix with the 
    #mesh surfaces taken out. 
    np.save("D:\\IDPcode\\temporary\\RTM_surfaces_2.npy", surf_mat)
    np.save("D:\\IDPcode\\temporary\\FM_surfaces.npy", surf_Alist)
    
def ff_check(RTMFile, I_time, UNmoved,RTMF):
    #This function uses last simulation results to adjust flow rates from
    #various inlets to create smoother flow front.
    
    #imports the previous iteration of flow matrix
    frMAT = np.load(r"D:\\IDPcode\\temporary\\flowMAT.npy")
    
    #Uses result of last executed simulation to find the number of frames
    #present in the result files.
    cmdReach(RTMFile)   
    with open("D:\\IDPcode\\pamrtm\\mainSimFiles\\FILLING_FACTOR124.txt", "r") as fin:
        data = fin.read().splitlines(True)
    nS = data[12]
    nS = int(nS.split()[1])  
    
    #Creates fill-factor output file for each available results frame.
    STRx = RTMFile+"---"+"getALLff(RTMfile,nS)"+"---"+str(nS)
    with open("Temporary\\PP_request.txt", "w") as text_file:
        text_file.write(STRx)
    cmd("VEBatch -activeconfig Trade:CompositesandPlastics -activeapp VisualRTM -sessionrun D:\\IDPcode\\RTM_PPcmd.py")
        
    #Check each result frame.
    #If flow front is non-uniform, flow rate matrix is adjusted.
    Y = 0
    while Y < nS:
        #Import filling factors for the particular time step.
        with open("D:\\IDPcode\\pamrtm\\mainSimFiles\\FILLING_FACTOR"+str(Y)+".txt", "r") as finn:
            data = finn.read().splitlines(True)
        with open('D:\\IDPcode\\pamrtm\\mainSimFiles\\FILLING_FACTOR_TEMP.txt', 'w') as fout:
            fout.writelines(data[14:])
        matrix = np.loadtxt("D:\\IDPcode\\pamrtm\\mainSimFiles\\FILLING_FACTOR_Temp.txt",usecols=range(2))
        
        #Filter the current timestep data for the not-fully-filled nodes.
        i = 0 
        vrba = np.zeros([1,2])
        while i < np.size(matrix,0):
            if 0.01 < matrix[i,1] < 0.95:
                vrba = np.concatenate((vrba,np.matrix([matrix[i,0],matrix[i,1]])),0)
            i = i + 1
    
        #Enlarge the matrix to allow for coordinate import
        locaV = np.zeros([np.size(vrba,0),3])
        vrba = np.concatenate((vrba,locaV),1)
        vrba = np.delete(vrba, (0), axis=0)
        #import node matrix - with locations and match nodes ... 
        with open("D:\\IDPcode\\pamrtm\\mainSimFiles\\"+RTMF+".inp") as nds:
            fl = nds.read()
            ff = fl.split("*NODE")[1]
            ff = ff.split("*SHELL")[0]
            coord_mat = np.zeros([1,4])
            temp_mat = np.zeros([1,4])
            iiy = 0
            coms = ff.count(',')
            while iiy < coms:
                if iiy != 0:
                    ex = ff.split(',')[iiy]
                    ex = float(ex.split()[1])
                else:
                    ex = ff.split(',')[iiy]
                #node number
                temp_mat[0,0] = float(ex)
                ex = ff.split(',')[iiy+1]
                #x value
                temp_mat[0,1] = float(ex)
                ex = ff.split(',')[iiy+2]
                #y value
                temp_mat[0,2] = float(ex)       
                if iiy != coms-3:
                    ex = ff.split(',')[iiy+3]
                    ex = float(ex.split()[0])
                else:
                    ex = ff.split(',')[iiy+3]
                    ex = float(ex)
                #z value
                temp_mat[0,3] = float(ex)
                coord_mat = np.concatenate((coord_mat, temp_mat), axis=0)       
                #add to coord mat matrix
                iiy = iiy + 3
            #delete the first row of coord mat
            coord_mat = np.delete(coord_mat, (0), axis=0)
    
        #Merge the node matrix and the fill factor matrix.
        i = 0
        while i < np.size(vrba,0):
            ii = 0
            NODE = vrba[i,0]
            while ii < np.size(coord_mat,0):
                if NODE == coord_mat[ii,0]:
                    #vrba[i,2:4] = coord_mat[ii,1:3]
                    vrba[i,2] = coord_mat[ii,1]
                    vrba[i,3] = coord_mat[ii,2]
                    vrba[i,4] = coord_mat[ii,3]
                    ii = ii + 99999999            
                ii = ii + 1
            i = i + 1
         
        #threshold is adjusted if a section cannot be resolved
        th = 40 + 5*(int(UNmoved/3))
            
        #Check if there is too large flow front disturbance.
        FF_check = True
        i = 0
        while i < np.size(vrba,0):
            ii = 0
            while ii <np.size(vrba,0):
                diff = abs(vrba[i,4] - vrba[ii,4])
                #30mm is the current treshold 
                if diff > th:
                    FF_check = False
                ii = ii + 1
            i = i + 1
        
        #If FF_check indicates an issue the below block is used to adjust
        #the flow rate input matrix.
        if FF_check ==False:
            #Find the time the flow front disturbance reached the treshold.
            print("Y:",Y,"I_time:",I_time,"nS:",nS)
            rT = int((float(I_time)/nS)*Y)
            print("rT, verify:",rT)
            #The flow rate is to be adjusted from rTmin to rTmax
            rTmin = rT - (int((float(I_time)/nS))*3)
            rTmax = rT
            
            if sum((frMAT[rT,:])) != sum((frMAT[rT+1,:])):
                UNmoved = UNmoved + 1
            
            #The segmentation is performed in local coordinates, where the 
            #local origin is a point on centerline.
            #Therefore the nodes are translated to their respective local 
            #coordinates.
            BCs = np.loadtxt(open("D:\\IDPcode\\temporary\\braidsegments.csv", "rb"), delimiter=",")
            refPTS = np.loadtxt(open("D:\\IDPcode\\temporary\\secPTS.csv","rb"), delimiter=",")
            secVECz = np.loadtxt(open("Temporary\\secVECz.csv","rb"), delimiter=",")
            secVECy = np.loadtxt(open("Temporary\\secVECy.csv","rb"), delimiter=",")
            secPTS = refPTS
            

            #Translation using GlobalToLocal script generated for FE originally.
            #Each x,y coordinate is altered to correspond to local refernce point.
            #z coordinates are unaltered as the segmentation file sticks to 
            #global coordinates for simplicity.
            i = 0
            step = refPTS[0,2]
            while i < np.size(vrba,0):
                ii = 0
                while ii < np.size(secPTS,0):
                    if (refPTS[ii,2]-step) <= vrba[i,4] < (refPTS[ii,2]+step):
                        secVECx = np.cross(secVECy[ii,:],secVECz[ii,:])
                        cSYS2 = np.array(([secVECx[0],secVECx[1],secVECx[2]],[secVECy[ii,0],secVECy[ii,1],secVECy[ii,2]],[secVECz[ii,0],secVECz[ii,1],secVECz[ii,2]]))
                        point1 = np.array([0,0,0])
                        point2 = np.array([secPTS[ii,0],secPTS[ii,1],secPTS[ii,2]])
                        cSYS1 = np.array(([1,0,0],[0,1,0],[0,0,1]))
                        GCP = np.array([vrba[i,2],vrba[i,3],vrba[i,4]])
                        kopyto = GlobalToLocal(point1,point2,cSYS1,cSYS2,GCP)
                        vrba[i,2] = kopyto[0]
                        vrba[i,3] = kopyto[1]
                    ii = ii + 1
                i = i + 1
            np.savetxt("Temporary\\verify.csv",vrba,delimiter=",")
            
            
            #Empty matrix for average z location of nodes within each segment.
            #(12 segments around the cross-section are considered)
            avZ = np.zeros([12,1])
            #Number of nodes allocated to each segment, used for averaging.
            avCount = np.zeros([12,1])
            #Overall average of the z coordinates of all partially filled nodes.
            AV  = np.average(vrba[:,4])
            #Distance between local average and global average.
            Df = np.zeros([12,1])
            
            #Build up average of each of the 12 sections.
            i = 0
            while i < np.size(vrba,0):
                iii = 0
                while iii < np.size(BCs,0):
                    if  (BCs[iii,6]<= vrba[i,4] < BCs[iii,5]) and (BCs[iii,4] <= vrba[i,3] < BCs[iii,3]) and (BCs[iii,2] <= vrba[i,2] < BCs[iii,1]):
                        #found the segment
                        circS = int(BCs[iii,0] % 12)-1
                        avCount[circS,0] = avCount[circS,0] + 1
                        avZ[circS,0] = (avZ[circS,0]*(avCount[circS,0]-1)+vrba[i,4])/avCount[circS,0]
                    iii = iii + 1
                i = i + 1
            i = 0
            while i < 12:
                Df[i,0] = avZ[i,0] - AV
                i = i + 1
                
            #Sum up the distance of all local averages to global average, in 
            #absolute terms.
            DT = np.sum(abs(Df[:,0]))
            print("DT =",DT)
            print("diff mat =",Df)
            i = 0
            totalShift = 0.0000000001*20
            while i < 12:
                ii = 0
                while ii < rTmax + 1:
                    if rTmin < ii:
                        frMAT[ii,i] = frMAT[ii,i] + totalShift*((-1)*Df[i,0]/DT)
                        #testing if the issues with failed table import has to do with sig-fig
                        frMAT[ii,i] = Round_To_n(frMAT[ii,i],3)
                        if frMAT[ii,i] < (1.0*10**(-10)):
                            frMAT[ii,i] = (1.0*10**(-10))

                    ii = ii + 1
                i = i + 1
            np.save("D:\\IDPcode\\temporary\\flowMAT.npy", frMAT)
            Y = 9000
        Y = Y + 1
    return(FF_check, UNmoved)
            
#cmdReach("IDP_spar_A147_M001_B001_R001")
#FF_check = ff_check("IDP_spar_A147_M001_B001_R001",42.5)
#print(FF_check)
    
    
#input file - instead function arguments - which are not possible due to the command line passing
#fl = open("D:\\IDPcode\\Temporary\\fe_in.txt", "rt")
#flstr = fl.read() 
#RTMfile = flstr.split("---")[1]
#MeshFile = flstr.split("---")[0]
#ST = flstr.split("---")[8]
#vn = flstr.split("---")[9]
#filename = MeshFile+".igs"
#maxFill,I_time = outputS1(RTMfile,MeshFile,ST,vn)