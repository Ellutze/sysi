import win32com.client.dynamic
import sys, os 
import numpy as np
import win32gui
import math
import time
from datetime import date
from MySQL_utils import storeCADinstance
from general_utils import foil_to_spar


def test():
    CATIA = win32com.client.Dispatch("CATIA.Application")
    documents1 = CATIA.Documents
    partDocument1 = documents1.Add("Part")
    #part1 = partDocument1.Part

def compost():
    # Binding python session into CATIA    
    CATIA = win32com.client.Dispatch("CATIA.Application")
    documents1 = CATIA.Documents # CATIA object for managing documents
    partDocument1 = documents1.Open("\CatiaFiles\TP_savetest_1811_A015_JK.CATPart")
    part1 = partDocument1 
#compost()
    
def ex1(project,file,varVal, version):
    start_time = time.time()
    scns = 4 #np.size(sectioned,0)
    
    chord_min = varVal['c_min']
    chord_max = varVal['c_max']
    
    #Setting up CATIA modelling environment
    CATIA = win32com.client.Dispatch("CATIA.Application")
    #record deletion of product....

    documents1 = CATIA.Documents
    partDocument1 = documents1.Add("Part")
    part1 = partDocument1.Part
    #Shape factory provides generating of shapes
    ShFactory = part1.HybridShapeFactory
    # Starting new body (geometrical set) in part1
    bodies1 = part1.HybridBodies
    # Adding new body to part1
    body1 = bodies1.Add()
    # Naming new body as "wireframe"
    body1.Name="Wireframe"
    # Surfaces group
    body3 = bodies1.Add()
    body3.Name="Surfaces"
    body007 = bodies1.Add()
    body007.Name="SourceLoft"
    
    #Loop through sections to create cross section geometries
    ii = 0
    while ii < (scns):
        #Section specific airfoil details.
        halfSpan= float(varVal['span']/(scns-1)*ii)
        chord = float(varVal['chord_'+str(ii)])
        twist= float(varVal['twist_'+str(ii)])
        dihedral = float(varVal['dihedral_'+str(ii)])
        
        #Creating a new geometry set for this cross-section.
        striga = str(ii)
        bodies2 = body1.hybridBodies # Starting new geometrical set in Wireframe
        body2 = bodies2.Add() # Adding new body to Wireframe
        body2.Name="Section"+striga # Naming new body
        
        #Run utilities function which translates airfoil data into spar 
        #relevant set of points.
        Airfoil = foil_to_spar(varVal['airfoil_'+str(ii)],chord_min,chord_max) 
        #(coordinates in unit chord scale are too small for CATIA)

        #Reference point for scaling and rotations.
        xAnchor = (chord_max+chord_min)/2
        #Significantly cambered aerofoils might require yAnchor to be calculated
        yAnchor = 0
        
        #Adjusting airfoil points, based on section parameters.
        i = 0
        af = np.zeros([np.size(Airfoil,0),2])
        while i < np.size(Airfoil,0):
            
            #translate choordinate system for correct scaling
            x = Airfoil[i,0]-xAnchor
            y = Airfoil[i,1]-yAnchor
            #scale the part
            x = chord*x
            y = chord*y
            
            #rotation before translation
            r = math.sqrt(y**2+x**2)
            epsi = math.asin(y/r)
            epsiD = epsi*180/math.pi
            #the ifs adjust for math.sin only working with half a circle
            if x < 0 and y >0:
                epsiD = 180-epsiD
            if x < 0 and y <0:
                epsiD = (180-abs(epsiD))*-1
            epsiD = twist+epsiD
            epsi = epsiD*math.pi/180
            y = r*math.sin(epsi)
            x = math.sqrt(r**2-y**2)
            if - 90 < epsiD <90:
                x = abs(x)
            if 90 < epsiD or epsiD < -90:
                x = abs(x)*-1
            
            #sweep, x-translation
            xT =(halfSpan)*math.tan(float(varVal['sweep_'+str(ii)])*math.pi/180)
            x = x  + xT
            #dihedral, y -translation
            yT =(halfSpan)*math.tan(float(dihedral)*math.pi/180)
            y = y + yT
            
            #New set of points.
            af[i,0] = x
            af[i,1] = y
            i = i + 1
        
        #c is the gradient of line dividing top and bottom surface points.
        c = xT*math.sin(twist*math.pi/180)
        top = np.zeros([1, 2])
        bot = np.zeros([1, 2])
        rTemp = np.zeros([1,2])
        #Spliting points between top and bottom surfaces.
        #Gradient line is used for the split, adjusted for twist, sweep and
        #dihedral.
        for row in af:
            if row[1] < (yAnchor-c+yT+math.tan(twist*math.pi/180)*(row[0]-xAnchor)):
                rTemp[0,0] = row[0]
                rTemp[0,1] = row[1]
                bot = np.concatenate((bot,rTemp),axis = 0)
            else:
                rTemp[0,0] = row[0]
                rTemp[0,1] = row[1]
                top = np.concatenate((top,rTemp),axis = 0)
        bot = np.delete(bot,0,axis=0)
        top = np.delete(top,0,axis=0)
        
        # Starting the top surface spline
        spline1 = ShFactory.AddNewSpline()
        spline1.SetSplineType(0)
        spline1.SetClosing(0)
        #Add points to splines
        xmaxT = np.matrix([[-1000,0]])
        xminT = np.matrix([[1000,0]])
        iiii = 0
        for row in top:        
            x = top[iiii,0]
            y = top[iiii,1]
            point=ShFactory.AddNewPointCoord(x,y,halfSpan)
            spline1.AddPoint(point)
            #Find the maximum x position for top surface.
            if x > xmaxT[0,0]:
                xmaxT = np.matrix([row[0],row[1]])
                rfp4 = part1.CreateReferenceFromObject(point)
            if x < xminT[0,0]:
                xminT = np.matrix([row[0],row[1]])
                rfp1 = part1.CreateReferenceFromObject(point)
            iiii = iiii + 1     
        #Submit the spline, and create the reference.
        rs1 = part1.CreateReferenceFromObject(spline1) 
        body2.AppendHybridShape(spline1)
        
        # Starting new spline for bottom section.
        spline2 = ShFactory.AddNewSpline()
        spline2.SetSplineType(0)
        spline2.SetClosing(0)
        
        #Add points to the spline
        xmaxB = np.matrix([[-1000,0]])
        xminB = np.matrix([[1000,0]])
        iiii = 0
        for row in bot:        
            x = bot[iiii,0]
            y = bot[iiii,1]
            point=ShFactory.AddNewPointCoord(x,y,halfSpan)
            spline2.AddPoint(point)
            #Find the max/min x point for bottoms surface.
            if x > xmaxB[0,0]:
                xmaxB = np.matrix([row[0],row[1]])
                rfp3 = part1.CreateReferenceFromObject(point)
            if x < xminB[0,0]:
                xminB = np.matrix([row[0],row[1]])
                rfp2 = part1.CreateReferenceFromObject(point)
            iiii = iiii + 1  
        #Submit the spline and create reference.
        body2.AppendHybridShape(spline2) 
        rs2 = part1.CreateReferenceFromObject(spline2) 
        
        #Adjust default radius based on the size of the local section.
        R = varVal['RAD']*float(varVal['chord_'+str(ii)])/float(varVal['chord_0'])
        
        #Identify the extreme positions of top and bottom surface in terms of
        #x position. 
        h1 = np.matrix([[xmaxT[0,0]+R,xmaxT[0,1]-R]])
        h3 = np.matrix([[xmaxB[0,0]+R,xmaxB[0,1]+R]])
        L1 = np.matrix([[xminB[0,0]-R,xminB[0,1]+R]])
        L3 = np.matrix([[xminT[0,0]-R,xminT[0,1]-R]])
        
        #Create the 4 points that define spar front and aft walls.
        pt1=ShFactory.AddNewPointCoord(L3[0,0],L3[0,1],halfSpan)
        body2.AppendHybridShape(pt1)    
        rpt1 = part1.CreateReferenceFromObject(pt1)
        pt2=ShFactory.AddNewPointCoord(L1[0,0],L1[0,1],halfSpan)
        body2.AppendHybridShape(pt2) 
        rpt2 = part1.CreateReferenceFromObject(pt2)  
        pt3=ShFactory.AddNewPointCoord(h3[0,0],h3[0,1],halfSpan)
        body2.AppendHybridShape(pt3)    
        rpt3 = part1.CreateReferenceFromObject(pt3)
        pt4=ShFactory.AddNewPointCoord(h1[0,0],h1[0,1],halfSpan)
        body2.AppendHybridShape(pt4) 
        rpt4 = part1.CreateReferenceFromObject(pt4)  
    
        #Create spar walls as lines.
        l1 = ShFactory.AddNewLinePtPt(rpt1, rpt2)
        body2.AppendHybridShape(l1)
        rl1 = part1.CreateReferenceFromObject(l1)  
        l2 = ShFactory.AddNewLinePtPt(rpt3, rpt4)
        body2.AppendHybridShape(l2)
        rl2 = part1.CreateReferenceFromObject(l2)  
        
        #Create corners by points and directions (from the spar walls).
        spline3 = ShFactory.AddNewSpline()
        spline3.SetSplineType(0)
        spline3.SetClosing(0)
        spline3.AddPointWithConstraintFromCurve(rfp1, rs1, 1.000000, 1, 1)
        spline3.AddPointWithConstraintFromCurve(rpt1, rl1,1.0,1,1)
        body2.AppendHybridShape(spline3) 
        rs3 = part1.CreateReferenceFromObject(spline3) 
        #Corner 2.
        spline4 = ShFactory.AddNewSpline()
        spline4.SetSplineType(0)
        spline4.SetClosing(0)
        spline4.AddPointWithConstraintFromCurve(rpt2, rl1, 1.000000, 1, 1)
        spline4.AddPointWithConstraintFromCurve(rfp2, rs2,1.0,1,1)
        body2.AppendHybridShape(spline4) 
        rs4 = part1.CreateReferenceFromObject(spline4) 
        #Corner 3.
        spline5 = ShFactory.AddNewSpline()
        spline5.SetSplineType(0)
        spline5.SetClosing(0)
        spline5.AddPointWithConstraintFromCurve(rfp3, rs2, 1.000000, 1, 1)
        spline5.AddPointWithConstraintFromCurve(rpt3, rl2,1.0,1,1)
        body2.AppendHybridShape(spline5) 
        rs5 = part1.CreateReferenceFromObject(spline5) 
        #Corner 4.
        spline6 = ShFactory.AddNewSpline()
        spline6.SetSplineType(0)
        spline6.SetClosing(0)
        spline6.AddPointWithConstraintFromCurve(rpt4, rl2, 1.000000, 1, 1)
        spline6.AddPointWithConstraintFromCurve(rfp4, rs1,1.0,1,1)
        body2.AppendHybridShape(spline6) 
        rs6 = part1.CreateReferenceFromObject(spline6) 
        
        #Assemble the cross section.
        AA = ShFactory.AddNewJoin(rs1, rs3)
        AA.AddElement(rl1)
        AA.AddElement(rs4)
        AA.AddElement(rs2)
        AA.AddElement(rs5)
        AA.AddElement(rl2)
        AA.AddElement(rs6)
        
        #The naming of the cross section is important! Used in braid. sim.
        AeroShape = "AeroShape"
        AeroShape += striga
        AA.Name= AeroShape 
        body2.AppendHybridShape(AA)
        ii = ii + 1
  
    #Creating lofts.
    #Currently each segment is lofted separately, to prevent extreme overshoots
    #of spline behaviour with large taper.
    bodiesx = part1.HybridBodies
    bodyx = bodiesx.Item("Wireframe")
    bodiesx2 = bodyx.HybridBodies
    #Loop to connect sections.
    iii = 0
    while iii < (scns-1):
        loft1 = ShFactory.AddNewLoft()
        loft1.SectionCoupling = 1
        loft1.Relimitation = 1
        loft1.CanonicalDetection = 2
        o = str(iii)
        bodyx2 = bodiesx2.Item("Section"+o)
        shapes1 = bodyx2.HybridShapes
        translate1 = shapes1.Item("AeroShape"+o)
        ref1 = part1.CreateReferenceFromObject(translate1)
        loft1.AddSectionToLoft(ref1, 1,None)
        iii = iii+1
        o = str(iii)
        bodyx2 = bodiesx2.Item("Section"+o)
        shapes1 = bodyx2.HybridShapes
        translate1 = shapes1.Item("AeroShape"+o)
        ref1 = part1.CreateReferenceFromObject(translate1)
        loft1.AddSectionToLoft(ref1, 1,None)
        bodyx4 = bodiesx.Item("SourceLoft")
        bodyx4.AppendHybridShape(loft1)
        part1.InWorkObject = loft1
        loft1.Name = "loft"+o
    #make the loft sections hidden
    selection1 = partDocument1.Selection
    selection1.Clear() # added recently delete if error
    visPropertySet1 = selection1.VisProperties
    part1 = partDocument1.Part
    hybridBodies1 = part1.HybridBodies
    hybridBody1 = hybridBodies1.Item("SourceLoft")
    #hybridBodies1 = hybridBody1.Parent
    selection1.Add(hybridBody1)
    visPropertySet1 = visPropertySet1.Parent
    visPropertySet1.SetShow(1)
    selection1.Clear()
    
    #Making sure the part as a whole is visible.
    selection1 = partDocument1.Selection
    visPropertySet1 = selection1.VisProperties
    part1 = partDocument1.Part
    selection1.Add(part1)
    visPropertySet1 = visPropertySet1.Parent
    bSTR1 = visPropertySet1.Name
    bSTR2 = visPropertySet1.Name
    visPropertySet1.SetShow(0)
    selection1.Clear()
    
    #assembly of loft sections
    body007 = bodiesx.Item("Surfaces")
    hybridShapes1 = bodyx4.HybridShapes
    hybridShapeLoft1 = hybridShapes1.Item("loft1")
    reference1 = part1.CreateReferenceFromObject(hybridShapeLoft1)
    hybridShapeLoft2 = hybridShapes1.Item("loft2")
    reference2 = part1.CreateReferenceFromObject(hybridShapeLoft2)
    hybridShapeAssemble1 = ShFactory.AddNewJoin(reference1, reference2)
    hybridShapeLoft3 = hybridShapes1.Item("loft3")
    reference3 = part1.CreateReferenceFromObject(hybridShapeLoft3)
    hybridShapeAssemble1.AddElement(reference3)
    #These settings might be the same as default, try without?:
    hybridShapeAssemble1.SetConnex(1)
    hybridShapeAssemble1.SetManifold(1)
    hybridShapeAssemble1.SetSimplify(0)
    hybridShapeAssemble1.SetSuppressMode(0)
    hybridShapeAssemble1.SetDeviation(0.001000)
    hybridShapeAssemble1.SetAngularToleranceMode(0)
    hybridShapeAssemble1.SetAngularTolerance(0.500000)
    hybridShapeAssemble1.SetFederationPropagation(0)
    body007.AppendHybridShape(hybridShapeAssemble1)
    part1.InWorkObject = hybridShapeAssemble1
    mainloft = "MainLoft"
    hybridShapeAssemble1.Name = mainloft

    part1.Update()
    #partDocument1 = CATIA.ActiveDocument

    #Save the CAD file generated.
    if version < 10:
        vn = "00"+str(version)
    elif version <100:
        vn = "0"+str(version)
    else:
        vn = str(version)
    version = "A"+vn
    name = project+"_"+file+"_"+version+"_JK"
    
    lPath = os.path.dirname(os.path.abspath(__file__))
    silo = lPath+"\\CatiaFiles\\SourceFiles\\"+name+".CatPart"
    print(silo)
    partDocument1.SaveAs(silo)
    #storeCAD instance to recored iteration of cad parameters in MySQL
    storeCADinstance(varVal,name,chord_min,chord_max,dihedral)
    #iges save
    silo2 = lPath+"\\CatiaFiles\\SourceFiles\\"+name+".igs"
    partDocument1.ExportData(silo2, "igs")
    partDocument1.Close()
    print("--- %s seconds ---" % (time.time() - start_time))
    return(name)
    