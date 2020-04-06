
import numpy as np
import math



def perpVectors(vector1, vector2):
    # this can produce two results!! .... control which one it creates???~~~~~~~~~~~~~~~~~~~~~~~~~
    vector3 = np.cross(vector1,vector2)
    #print(vector3)
    return(vector3)
    
def vecL(vector):
    #print(vector)
    vecLen = np.sqrt(vector[0]**2+vector[1]**2+vector[2]**2)
    return(vecLen)

def GlobalToLocal(point1,point2,cSYS1,cSYS2,GCP):
    #find position of a point (GCP) relative to an alternative coordinate system
    #cSYS1 is the original coordinate system in which GCP is stated
    #cSYS2 is the secondary coordinate system in which the point is to be expressed
    #print(point1,point2,cSYS1,cSYS2,GCP)
    i = 0
    p1 = point2
    #print("p1",p1)
    # i loops through first vectors 
    shift = np.zeros([3,3])
    while i<3:
        ii =0 
        # ii loops through second system of vectors
        while ii<3:
            p2 = p1 + cSYS2[ii,:]*10
            #print("p2",p2)
            #makes original vector into unit vector
            oV = cSYS1[i,:]
            oVmag = (oV[0]**2 +oV[1]**2 +oV[2]**2)**(1/2)
            unitV = oV/oVmag
            
            #the main math http://mathworld.wolfram.com/Point-LineDistance3-Dimensional.html
            p0 = p1 + unitV
            #print("p0",p0)
            d1 = vecL(np.cross((p0-p1),(p0-p2)))/vecL(p2-p1)
            #prevent errors offseting plane
            d1 = min(1,(d1))
            #print("d1",d1)
            effectD = math.sqrt(1-d1**2)
            if cSYS2[i,ii] < 0:
                effectD = effectD*-1

            #how much does unit vector of x1 influence vector x2, how much does unit vector x1 influence y2.... (first row)
            #how much does unit vector of y1 influence vector x2.... (second row...)
            shift[i,ii] = effectD

            ii = ii+1
        i=i+1
    #expression of point position relative to new refference point, with old coordinates
    diff = GCP - (point2-point1)
    
    #nice and neat, same as below, but cannot be used in python 2.7/Abaqus
    #LCP = np.matmul(shift,np.transpose(diff))
    
    #lenghty matrix multiplication
    x = shift[0,0]*diff[0]+shift[0,1]*diff[1]+shift[0,2]*diff[2]
    y = shift[1,0]*diff[0]+shift[1,1]*diff[1]+shift[1,2]*diff[2]
    z = shift[2,0]*diff[0]+shift[2,1]*diff[1]+shift[2,2]*diff[2]
    LCP = [x,y,z]
    #print(LCP)

    return(LCP)    
    #check that cross product works?
    

#manual input option:    
    
#cSYS2 = np.array(([1,0,0],[0,-0.1,0.1],[0,0.1,0.1]))
#point1 = np.array([0,0,0])
#point2 = np.array([0,15,100])
#GCP = np.array([10,20,120])
#cSYS1 = np.array(([1,0,0],[0,1,0],[0,0,1]))
#LCP = GlobalToLocal(point1,point2, cSYS1,cSYS2,GCP)
#print(LCP)
#print("Journey there...")
# to return to original coordinates ==> recalculate reference points into the secondary system and rewerse the input order
#point2 = GlobalToLocal(point1,point2, cSYS1,cSYS2,point1)
#point1 = GlobalToLocal(point1,point2, cSYS1,cSYS2,point2)
#invert the transformaiton vectors matrix 
#cSYS2 = np.linalg.inv(cSYS2)
#pass in tranformed points, inverted matrix, and the translated point in secondary coordinates
#GCP = GlobalToLocal(point1,point2,cSYS1,cSYS2,LCP)
#rint(GCP)    
#print("...and back again")
    
def orderByColumn(MATRIX,COLUMN,order):
    #This function sorts matrix by column.
    # order 1 or -1, 1 ascending, - 1 descending
    #For ascending order:
    if order == 1:
        F = np.size(MATRIX,1)
        #create new empty matrix
        ORDERED = np.zeros([2,F])
        #place extreme values in first second row
        ORDERED[0,COLUMN] = -1000000000
        ORDERED[1,COLUMN] = 1000000000
        i = 0
        #loop through imported matrix, and place row into new matrix based on defined column
        while i < np.size(MATRIX,0):
            #print(ORDERED)
            ii = 0
            while ii < np.size(ORDERED)-1:
                if ORDERED[ii,COLUMN] < MATRIX[i,COLUMN] <= ORDERED[ii+1,COLUMN]:
                    ORDERED = np.insert(ORDERED, (ii+1), MATRIX[i,:], axis=0)
                    ii = np.size(ORDERED)+1
                ii = ii + 1 
            i = i + 1
        #delete the extreme values created at the start
        ORDERED =np.delete(ORDERED,0,axis=0)
        ORDERED =np.delete(ORDERED,(np.size(ORDERED,0)-1),axis=0)
        #print(ORDERED)
    #For descending order :
    elif order == -1:
        F = np.size(MATRIX,1)
        ORDERED = np.zeros([2,F])
        ORDERED[0,COLUMN] = 1000000000
        ORDERED[1,COLUMN] = -1000000000
        i = 0
        while i < np.size(MATRIX,0):
            #print(ORDERED)
            ii = 0
            while ii < np.size(ORDERED)-1:
                if ORDERED[ii,COLUMN] >= MATRIX[i,COLUMN] > ORDERED[ii+1,COLUMN]:
                    ORDERED = np.insert(ORDERED, (ii+1), MATRIX[i,:], axis=0)
                    ii = np.size(ORDERED)+1
                ii = ii + 1 
            i = i + 1
        ORDERED =np.delete(ORDERED,0,axis=0)
        ORDERED =np.delete(ORDERED,(np.size(ORDERED,0)-1),axis=0)
        #print(ORDERED)      
        
    else:
        print("order variable can only be 1 or -1")
    return(ORDERED)
    
    
#test
#MATRIX = np.matrix([[1,2,3],[1,3,2],[1,53,23],[1,0.2,0.1],[13,32,13]])
#COLUMN = 1
#orderByColumn(MATRIX,COLUMN)