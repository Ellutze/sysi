from abaqus import *
from abaqusConstants import *
from odbMaterial import *
from odbSection import *

#automatically adjusted path
lPath_auto='D:\sysi'

# Open the odb
myOdb = session.openOdb(name=lPath_auto+'\\Temporary\\Task-1.odb')
frames = myOdb.steps["Step-1"].frames
numFrames = len(frames)
# Isolate the instance, get the number of nodes and elements

#instance is made capital by Abaqus, can be checked by running following 2 lines in command line:
#myInstance = myOdbrootAssembly.instances
#print(myInstance)

myInstance = myOdb.rootAssembly.instances['N2']
numNodes = len(myInstance.nodes)
numElements = len(myInstance.elements)

#stres string used to build up understandable output file
STRSTR1 = str(numElements) +"_________"
for el in range(0,numElements):
    #"S4R" refers to shell element, other elements require different keyword
   
    #centroid to integration point change
    #"-1 find what means, "S" dmeans stresses", ....
    Stress=myOdb.steps["Step-1"].frames[-1].fieldOutputs['S'].getSubset(region=myInstance.elements[el],position=CENTROID, elementType='S4R').values
    
    #for each element get all integration point in range(5):
    sz = len(Stress)
    for ip in range(0,sz):
        #stresses relevant for given elment
        Sxx = Stress[ip].data[0]
        Syy = Stress[ip].data[1]
        Szz = Stress[ip].data[2]
        Sxy = Stress[ip].data[3]
        #Sxz = Stress[ip].data[4]
        #Syz = Stress[ip].data[5]
        
        #Build up the stress file (this should be reformated based on requirements later)
        STRSTR1 = STRSTR1+","+str(Sxx)+"||"
        
#deflection outputs 
Deflections=myOdb.steps["Step-1"].frames[-1].fieldOutputs["U"].values
TDM = 0
df = len(Deflections)
#build up string for deflections
STR2 = ""
for ipp in range(0,df):
    #x,y,z deflections as follows
    dx = Deflections[ipp].data[0]
    dy = Deflections[ipp].data[1]
    dz = Deflections[ipp].data[2]
    #building up the string for the text format 
    STR2 =STR2 + str(dx) + ","+str(dy) + ","+str(dz) + "\n"
    TD = (dx**2 + dy**2 + dz**2)**(0.5)
    #save the string in the fe_out text file - x,y,z deflections in each row
    with open("Temporary\\abaq_def_out.txt", "w") as text_file:
        text_file.write(STR2)
    #finding the maximum deflection
    if TDM < TD:
        TDM = TD

#textfile outputting all the stresses 
#with open("export_trial.txt", "w") as text_file:
    #text_file.write(STRSTR1)
  
#textfile outputing maximum total deflection only
with open("Temporary\\fe_out.txt", "w") as text_file:
    text_file.write(str(TDM))
myOdb.close()

