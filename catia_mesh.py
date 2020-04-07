import win32com.client.dynamic
import math
import numpy as np
import time 
import os

def paraRedef(md,sd):
    #processes the input to the CATIA mesh functions below
    #currently inefficient but will help in case of increased number of inputs, for the MD matrix management
    
    #MD[0] is the number of cells lengtwise
    MD = np.zeros(3)
    MD[0] = round(sd[0]/md[0])
    #MD[1] is the number of cells round the spar
    MD[1] = md[1]
    #MD[2] is the length of the spar
    MD[2] = sd[0]
    return(MD)  
    
def openPart(CADfile):
    lPath = os.path.dirname(os.path.abspath(__file__))
    #This functions opens relevant CATIA files and returns core handles for the file 
    CATIA = win32com.client.Dispatch("CATIA.Application")
    #documents1 = CATIA.Documents # this line is not currently in use
    CATIA.RefreshDisplay = False
    
    #location of CATIA file to be meshed
    str15 = lPath+"\\CatiaFiles\\SourceFiles\\"+CADfile+".CatPart"
    partDocument1 = CATIA.Documents.Open(str15)
    part1 = partDocument1.Part
    HSF1 = part1.HybridShapeFactory
    bodies1 = part1.HybridBodies
    
    #Create geometrical sets for management of generated geometries (functions below)
    body1 = bodies1.Add()
    body1.Name="MeshGeo"
    body3 = bodies1.Add() # Adding new body
    body3.Name="Elements" # Naming new body as "Surfaces"
    print("Part opened")
    return(part1, HSF1,partDocument1)
    
#TESTING LINE BELOW
#part1, HSF1 = openPart("IDP_SparIteration0203_1901_A001_JK")
   
def planes(part1,HSF1,MD,rnc):
    #generates span-wise planes for sectioning
    originElements1 = part1.OriginElements
    PlaneExplicit1 = originElements1.PlaneXY
    ref1 = part1.CreateReferenceFromObject(PlaneExplicit1)
    hbs1 = part1.HybridBodies
    hb1 = hbs1.Item("MeshGeo")
    i = 0
    #the planes are distributed to create number of span-wise mesh-elements required, as specified in MD matrix
    while i < MD.shape[0]:
        y = MD[i,0]
        offset1 = HSF1.AddNewPlaneOffset(ref1,y,False)
        hb1.AppendHybridShape(offset1)
        i = i + 1
    part1.Update()
    print("Cutting planes created")
#TESTING LINE BELOW
#planes(part1, HSF1,MD)

def insects(part1,HSF1,MD,rnc):
    #The planes above are intersected with the spar
    hbs1 = part1.HybridBodies
    hb1 = hbs1.Item("MeshGeo")
    hb2 = hbs1.Item("Surfaces")
    hs1 = hb1.HybridShapes
    hs2 = hb2.HybridShapes
    y = 1
    while y < (MD.shape[0]+0.1):
        ystr = str(y)
        #It is crucial that no planes are manually introduced to the part before, as the numbering assumes planes created only within automation routines
        planeSTR = "Plane."+ystr
        offset1 = hs1.Item(planeSTR)
        ref1 = part1.CreateReferenceFromObject(offset1)
        #the main surface, "MainLoft" is the name of the surface in all automatically genereted splines (see catia.py)
        hsl1 = hs2.Item("MainLoft")
        ref2 = part1.CreateReferenceFromObject(hsl1)
        hsi1 = HSF1.AddNewIntersection(ref1,ref2)
        hsi1.PointType = 0
        hb1.AppendHybridShape(hsi1)
        y = y + 1
    part1.Update()
    print("Intersects created")
#TESTING LINE BELOW
#insects(part1,HSF1,MD)

def pts(part1, HSF1,MD,rnc):
    #generates points around the intersection lines, based on number of chord-wise elments, as defined by MD matrix
    time2 = time.time()
    hbs1 = part1.HybridBodies
    hb1 = hbs1.Item("MeshGeo")
    hs1 = hb1.HybridShapes
    intr = 1 
    i=300
    while intr < (MD.shape[0]+0.1):
        x = 0 
        step = 1/rnc
        #the 0.99... is used in order to prevent rounding issue where point is created as a duplicate with 0 (or 1)
        while x < 0.99999999:
            hsd1 = HSF1.AddNewDirectionByCoord(1,2,3)
            str1 = str(intr)
            hsi1 = hs1.Item("Intersect."+str1+"")
            ref1 = part1.CreateReferenceFromObject(hsi1)
            hse1 = HSF1.AddNewExtremum(ref1,hsd1,1)
            hb1.AppendHybridShape(hse1)
            ref2 = part1.CreateReferenceFromObject(hsi1)
            ref3 = part1.CreateReferenceFromObject(hse1)
            hspc1 = HSF1.AddNewPointOnCurveWithReferenceFromPercent(ref2,ref3,x,False)
            hb1.AppendHybridShape(hspc1)
            hspc1.Name="MeshPoint"+str(i)
            i = i + 1
            HSF1.GSMVisibility(ref3,0)
            x = x + step
        intr = intr + 1
    print("--- Points generation: %s seconds ---" % (time.time() - time2))
    part1.Update()
  
    
#TESTING LINE BELOW
#pts(part1,HSF1,MD)

def ref(part1,HSF1,MD,rnc):
    #creates a reference point in the middle of root cross-section
    #this point can be anywhere, as long as it does not lie on the surface

    hbs = part1.HybridBodies
    hb = hbs.Item("MeshGeo")
    hs = hb.HybridShapes
    hse = hs.Item("Extremum.1")
    ref1 = part1.CreateReferenceFromObject(hse)
    midpoint = str(int(300+rnc/2))
    spc = hs.Item("MeshPoint"+midpoint+"")
    ref2 = part1.CreateReferenceFromObject(spc)
    hsl = HSF1.AddNewLinePtPt(ref1,ref2)
    hb.AppendHybridShape(hsl)
    ref3 = part1.CreatereferenceFromObject(hsl)
    spc2 = HSF1.AddNewPointOnCurveFromPercent(ref3,0.5,False)
    hb.AppendHybridShape(spc2)
    part1.Update()
    print("Reference point created")
#TESTING LINE BELOW
#ref(part1,HSF1,MD)


def cnxl(part1,HSF1,MD,rnc):
    #the intersection lines are segmented by split function
    #uses the reference point to create splines which aid with cutting, creating perfect intersection at cutting points
    hbs = part1.HybridBodies
    hb = hbs.Item("MeshGeo")
    hs = hb.HybridShapes

    cnt = 1
    #changed from 96 to 78, this needs to be automated at some point... - name the points as you create them?
    start = 299
    #creates lins around cross section of part
    while cnt < ((rnc*MD.shape[0]+1)):
        pt1 = start +cnt
        str1 = str(int(pt1))
        hpo1 = hs.Item("MeshPoint"+str1+"")
        ref1 = part1.CreateReferenceFromObject(hpo1)
        if ((pt1-299)/rnc) == round((pt1-299)/rnc):
            pt2 = pt1 - (rnc-1)
        else:
            pt2 =pt1 + 1
        str2 = str(int(pt2))
        #print(str2)
        hpo2 = hs.Item("MeshPoint"+str2+"")
        ref2 = part1.CreateReferenceFromObject(hpo2)
        hslx = HSF1.AddNewLinePtPt(ref1, ref2)
        hb.AppendHybridShape(hslx)
        cnt = cnt + 1

    #creates spanwise lines 
    cnt = 1
    while cnt < (rnc*(MD.shape[0]-1)+1):
        pt1 = start + cnt
        str1 = str(int(pt1))
        hpo1 = hs.Item("MeshPoint"+str1+"")
        ref1 = part1.CreateReferenceFromObject(hpo1)
        pt2 =pt1 + rnc
        str2 = str(int(pt2))
        hpo2 = hs.Item("MeshPoint"+str2)
        ref2 = part1.CreateReferenceFromObject(hpo2)
        hslx = HSF1.AddNewLinePtPt(ref1,ref2)
        hb.AppendHybridShape(hslx)
        cnt = cnt + 1
    
    part1.Update()
    print("Element lines created")
#cnxl(part1,HSF1,MD)
        
def sweep(part1,HSF1,MD,rnc):
    #number of circ lines
    cl = (rnc*MD.shape[0]) #+rnc?

    #number of lines at the start
    #Shouldn't change unless shape generation reorganised 
    #Last reorganisation 20/01/2020 from 0 lines to 8
    il = 8
    
    #creating the surface of each element in the mesh
    #very computationally heavy and potentially unnecessary - review alternatives?
    hbs = part1.HybridBodies
    hb = hbs.Item("MeshGeo")
    hs = hb.HybridShapes
    hb2 = hbs.Item("Elements")
    ct = 1
    
    while ct < (MD.shape[0]*rnc+1-rnc):
        #below if function helps resolve the issuew sith reusing start spline, at the end of the cross section loop
        if (ct/rnc)==round(ct/rnc):
            sp1 = il + cl + ct
            sp2 = sp1 - (rnc-1)
        else:
            sp1 = il + cl +ct
            sp2 = sp1 + 1
        ct1 = il + ct
        ct2 = ct1 + rnc
        
        #the sweep definition using two splits and two splines as guide curves
        hsl = HSF1.AddNewLoft()
        hsl.SectionCoupling = 1
        hsl.Relimitation = 1
        hsl.CanonicalDetection = 2
        sp1s = str(int(sp1))
        hss1 = hs.Item("Line."+sp1s)
        ref1 = part1.CreateReferenceFromObject(hss1)
        hsl.AddGuide(ref1)
        sp2s = str(int(sp2))
        hss2 = hs.Item("Line."+sp2s)
        ref2 = part1.CreateReferenceFromObject(hss2)
        hsl.AddGuide(ref2)
        ct1s = str(int(ct1))
        ssp1 = hs.Item("Line."+ct1s)
        ref3 = part1.CreateReferenceFromObject(ssp1)
        hsl.AddSectionToLoft(ref3,1,None)
        ct2s = str(int(ct2))
        ssp2 = hs.Item("Line."+ct2s)
        ref4 = part1.CreateReferenceFromObject(ssp2)
        hsl.AddSectionToLoft(ref4,1,None)
        hb2.AppendHybridShape(hsl)
        ct = ct + 1
    
    #hides geometry, leaving only the mesh elements displayed (required for IGES export)
    CATIA = win32com.client.Dispatch("CATIA.Application")
    partDocument1 = CATIA.ActiveDocument
    selection1 = partDocument1.Selection
    visPropertySet1 = selection1.VisProperties
    hb1 = hbs.Item("Wireframe")
    #hbs = hb1.Parent 
    hb2 = hbs.Item("MeshGeo")
    hb3 = hbs.Item("Surfaces")
    selection1.Add(hb1)
    selection1.Add(hb2)
    selection1.Add(hb3)
    visPropertySet1 = visPropertySet1.Parent
    visPropertySet1.SetShow(1)
    selection1.clear
    print("Element surfaces created")
    CATIA.RefreshDisplay = True
    part1.Update()

#sweep(part1,HSF1,MD)
        
#print("--- %s seconds ---" % (time.time() - time1))