import Segmentation
import lam_tools
import numpy as np
import time
#import MySQL_utils

def aba_inputProp(BraidFile,CADfile,varVal):
    print(BraidFile)
    print(CADfile)
    #this function segments the part into uniform material propertis areas
    #then it calculates the appropriate properties from the results of braiding analysis
    st496 = time.time() 
    
    #np import spheres
    II = np.load('D:\\IDPcode\\Temporary\\for_spheres.npy')
    i = 0
    while i < II.shape[0]:
        #process the acquired values
        span_ele_size = II[i,1]
        #diagonal value
        diag = np.sqrt(2*(span_ele_size**2))
        #1.45 is extension of sphere so that it encloses element even if the point is slightly off the centre
        sphere_rad = diag*1.45/2
        II[i,1] = sphere_rad
        
        i = i + 1
    #saves required sphere assignments
    np.savetxt("D:\\IDPcode\\Temporary\\spheres.csv", II, delimiter=",")
        
    #the next is not really required is it...since the numpy saving
    with open("Temporary\\sphere_rad.txt", "w") as text_file:
        text_file.write(str(sphere_rad))

    #span
    span = varVal["span"]
    #number of spanwise section ~~~~ eventually turn into variable (stored in?)
    secs = 20
    secPTS, secVECy,secVECz = Segmentation.centPTS_P(BraidFile,span,secs) 
    output, segBC,secPTS,secVECy,secVECz = Segmentation.braidAV(secPTS,secVECy,secVECz,BraidFile,secs,varVal)
    
    #save the boundary condition info, and info about local coordinate systems
    np.savetxt("D:\\IDPcode\\Temporary\\output.csv", output, delimiter=",")
    np.savetxt("D:\\IDPcode\\Temporary\\BraidSegments.csv", segBC, delimiter=",")
    np.savetxt("D:\\IDPcode\\Temporary\\secPTS.csv", secPTS, delimiter=",")
    np.savetxt("D:\\IDPcode\\Temporary\\secVECy.csv", secVECy, delimiter=",")
    np.savetxt("D:\\IDPcode\\Temporary\\secVECz.csv", secVECz, delimiter=",")
    matXX = np.zeros([1,14])

    #print(output)
    for row in output:
        #fibre radius, pitch1, pitch2, angle1, angle2, ....+ material properties
        #mat properties 239.5Gpa E1f, 13.5Gpa E2f, 3.3Gpa Em, 6.81Gpa G12f, shear str matrix 41.03 Mpa, and some poisson ratios...
        #,239500,13400,3300,6810,41.03,0.2,0.35)
        memProps, dens, TL, K1, K2, Vf, t = lam_tools.ps(row[3],row[4],row[1],row[2],varVal)
        Exm,Eym,Gxym,vxym,vyxm,mxm,mym = memProps            
        matYY = np.matrix([row[0],Exm,Eym,Gxym,vxym,vyxm,mxm,mym,dens,TL,K1,K2,Vf,t])
        matXX = np.concatenate((matXX,matYY),axis=0)
    matXX = np.delete(matXX, (0), axis=0)
    
    np.savetxt("D:\\IDPcode\\Temporary\\BraidData.csv", matXX, delimiter=",")
    print("Total segmentation time:--- %s seconds ---" % (time.time() - st496))
    spanwise_sections = secs
    return(spanwise_sections)
        
#matrix = "Bakelite EPR-L20"
#fibre ="AKSAca A-42"

#from default_var_dict import getBase
#
#varVal, varMin,varMax = getBase()
#varVal["mesh_size"] = 7.35
#aba_inputProp("IDP_spar_A451_B001","IDP_spar_A451_JK",varVal)