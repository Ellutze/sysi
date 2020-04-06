from vecEX2_C import wrmmm
import win32com.client.dynamic
import sys, os 
import numpy as np
import win32gui
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import time
from math_utils import GlobalToLocal
from IDP_databases import cnt_X, dc_X
#from mysql.connector import MySQLConnection, Error
#from python_mysql_dbconfig import read_db_config
import math
#import sys 
from IDP_cheats import togglePulse

def centPTS_C(BraidFile, span, secs):
    #this script finds points/positions on centreline for reference of locations relative to centreline
    #obtain the pitch data based on BraidFile
    cnnE,crrE = cnt_X('NCC')
    #(change when the CATIA terminology is changed)
    
    #tdm = str(time.strftime("%m"))
    #tdy = str(time.strftime("%y"))
    
    Cfile = BraidFile.split("_")[0] +"_"+ BraidFile.split("_")[1] +"_"+BraidFile.split("_")[2]+"_JK"
    query = "Select half_span, twist from "+Cfile
    crrE.execute(query)
    #get results
    sd = np.zeros([1,2])
    rows = crrE.fetchall()
    #creates a list of version numbers
    for row in rows:
        try:
            sdx = np.zeros([1,2])
            sdx[0,0],sdx[0,1] = float(row[0]),float(row[1])
            sd = np.concatenate((sd,sdx),axis=0)
            #break
        except TypeError:
            print("x")
    sd = np.delete(sd, (0), axis=0)
    #close SQL handles 
    dc_X('NCC',cnnE,crrE)
    
    
    #creates empty matrix based on number of sections ==> number of reference points required
    secPTS = np.zeros([secs,3])
    secVECz = np.zeros([secs,3])
    secVECy = np.zeros([secs,3])
    #section lenght calculate
    secLen = span/secs
    
    CATIA = win32com.client.dynamic.Dispatch("CATIA.Application")
    CATIA.RefreshDisplay = False
    
    #location of CATIA braid-file 
    str15 = "D:\\IDPcode\\CatiaFiles\\BraidFiles\\"+BraidFile+".CatPart"
    partDocument1 = CATIA.Documents.Open(str15)
    part1 = partDocument1.Part
    HSF1 = part1.HybridShapeFactory
    hbs1 = part1.HybridBodies
    
    #Catia reference set - geometries fixed names - created by braid scripts
    hb1 = hbs1.Item("CentrelineGeo")
    hb2 = hbs1.Item("CentreSpline")
    hs1 = hb2.HybridShapes
    hss1 = hs1.Item("Centreline")
    ref2 = part1.CreateReferenceFromObject(hss1)
    hb3 = hbs1.Add()
    hb3.Name="CentrelinePoints"
    
    #create a reference from one of the origin planes
    originElements1 = part1.OriginElements
    plane1 = originElements1.PlaneXY
    ref1 = part1.CreateReferenceFromObject(plane1)

    i = 0 
    #loop through sections
    while i < secs:
        #the coordinate systems are based in the middle of section (hence 0.5)
        rang1 = (i+0.5)*secLen
        #offset and intersection to create 0 point for new coo system
        off1 = HSF1.AddNewPlaneOffset(ref1, rang1, False)
        hb1.AppendHybridShape(off1)
        ref3 = part1.CreateReferenceFromObject(off1)
        ref2 = part1.CreateReferenceFromObject(hss1)
        hsi1 = HSF1.AddNewIntersection(ref2, ref3)
        hsi1.PointType = 0
        hb3.AppendHybridShape(hsi1)
        #create a second point to generate vector line
        #this is stored in hidden geometry
        #the 5 is 5mm of step on centreline to create the base vector
        off2 = HSF1.AddNewPlaneOffset(ref1,(rang1+5),False)
        hb1.AppendHybridShape(off2)
        ref4 = part1.CreateReferenceFromObject(off2)
        hsi2 = HSF1.AddNewIntersection(ref2,ref4)
        hsi2.PointType = 0
        hb1.AppendHybridShape(hsi2)
        
        #creating straight line between two lines on centreline 
        ref5 = part1.CreateReferenceFromObject(hsi1)
        ref6 = part1.CreateReferenceFromObject(hsi2)
        hslx = HSF1.AddNewLinePtPt(ref5,ref6)
        hb3.AppendHybridShape(hslx)
        part1.Update()
        #obtain the vector using wrmmm script
        partDocument1.ExportData("D:\\IDPcode\\Temporary\\xxx.wrl", "wrl")
        vec, point = wrmmm()
            
        #hide unused geomtry
        selection1 = partDocument1.Selection
        selection1.Clear 
        visPropertySet1 = selection1.VisProperties
        selection1.Add(hslx)
        visPropertySet1 = visPropertySet1.Parent
        visPropertySet1.SetShow(1)
        selection1.Clear 
        
        #output point and z vector
        secPTS[i,0] = point[0,0]
        secPTS[i,1] = point[0,1]
        secPTS[i,2] = point[0,2]
        
        secVECz[i,0] = vec[0,0]
        secVECz[i,1] = vec[0,1]
        secVECz[i,2] = vec[0,2]
        
        ii = 0
        s2 = 0
        while rang1 > s2:
            s1 = sd[ii,0]
            s2 = sd[ii+1,0]
            # this minus is used to match angle of attack effect with the vector transform.... verify
            t1 = -sd[ii,1]
            t2 = -sd[ii+1,1]
            ii = ii + 1
        #interpolation to find local twist
        prog = (rang1-s1)/(s2-s1)
        twist = t1 + (t2-t1)*prog
        #print(twist)
        
        #position of third point for surface creation (~~~~ eventually provide drawing of this ?~~~~)
        buildPointZ = point[0,2]
        buildPointY = point[0,1]+100
        buildPointX = point[0,0] + 100*math.tan(twist*math.pi/180)
        
        #direction of angle is to be checked later ~~~~~~~~~~~~~~~~~
        hspc = HSF1.AddNewPointCoord(buildPointX, buildPointY, buildPointZ)
        hb1.AppendHybridShape(hspc)
        ref7 = part1.CreateReferenceFromObject(hspc)
        
        #plane made of three points
        PP1 = HSF1.AddNewPlane3Points(ref5, ref6, ref7)
        hb1.AppendHybridShape(PP1)
        
        #create a line on the plane at 90 degrees to z direction vector 
        ref8 =hslx
        ref9 = PP1
        sla1 = HSF1.AddNewLineAngle(ref8, ref9, ref5, False, 0.000000, 20.000000, 90.000000, False)
        hb3.AppendHybridShape(sla1)
        #update, export, obtain vector
        part1.Update()
        partDocument1.ExportData("D:\\IDPcode\\Temporary\\xxx.wrl", "wrl")
        vec, point = wrmmm()
        
        #hide useless geometry
        selection1 = partDocument1.Selection
        selection1.Clear 
        visPropertySet1 = selection1.VisProperties
        selection1.Add(sla1)
        selection1.Add(hsi1)
        visPropertySet1 = visPropertySet1.Parent
        visPropertySet1.SetShow(1)
        selection1.Clear 
        #export second vector
        secVECy[i,0] = vec[0,0]
        secVECy[i,1] = vec[0,1]
        secVECy[i,2] = vec[0,2]
        
        i = i + 1
        
    #These hashed lines can be used to visualize the operations in CATIA:
    #silo = "D:\\IDPcode\\CatiaFiles\\TEST.CATPART"
    #partDocument1.SaveAs(silo)
    #breakthis   

    partDocument1.Close()
    CATIA.RefreshDisplay = True
    #print(secVECy)
    #print(secPTS,secVECy,secVECz)
    return(secPTS, secVECy, secVECz)
    
def centPTS_P(BraidFile, span, secs):
    #this script finds points/positions on centreline for reference of locations relative to centreline
    #obtain the pitch data based on BraidFile
    cnnE,crrE = cnt_X('NCC')
    #(change when the CATIA terminology is changed)
    
    #tdm = str(time.strftime("%m"))
    #tdy = str(time.strftime("%y"))
    
    Cfile = BraidFile.split("_")[0] +"_"+ BraidFile.split("_")[1] +"_"+BraidFile.split("_")[2]+"_JK"
    query = "Select half_span, twist from "+Cfile
    crrE.execute(query)
    #get results
    sd = np.zeros([1,2])
    rows = crrE.fetchall()
    #creates a list of version numbers
    for row in rows:
        try:
            sdx = np.zeros([1,2])
            sdx[0,0],sdx[0,1] = float(row[0]),float(row[1])
            sd = np.concatenate((sd,sdx),axis=0)
            #break
        except TypeError:
            print("x")
    sd = np.delete(sd, (0), axis=0)
    #close SQL handles 
    dc_X('NCC',cnnE,crrE)
    
    
    #creates empty matrix based on number of sections ==> number of reference points required
    secPTS = np.zeros([secs,3])
    secVECz = np.zeros([secs,3])
    secVECy = np.zeros([secs,3])
    #section lenght calculate
    secLen = span/secs
    
    cdArr = np.load("D:\\IDPcode\\temporary\\cdArr.npy")

    i = 0 
    #loop through sections
    while i < secs:
        #the coordinate systems are based in the middle of section (hence 0.5)
        rang1 = (i+0.5)*secLen
        #offset and intersection to create 0 point for new coo system

        # OBTAIN X,Y,Z POINT BASED ON cdArr
        ii = 0
        z = 0
        while z < rang1:
            z = cdArr[ii,3]
            ii = ii + 1  

        #secPTS  
        secPTS[i,0] = (cdArr[ii,1]-cdArr[ii-1,1])*((rang1-cdArr[ii-1,3])/(cdArr[ii,3]-cdArr[ii-1,3]))+cdArr[ii-1,1]
        secPTS[i,1] = (cdArr[ii,2]-cdArr[ii-1,2])*((rang1-cdArr[ii-1,3])/(cdArr[ii,3]-cdArr[ii-1,3]))+cdArr[ii-1,2]
        secPTS[i,2] = (cdArr[ii,3]-cdArr[ii-1,3])*((rang1-cdArr[ii-1,3])/(cdArr[ii,3]-cdArr[ii-1,3]))+cdArr[ii-1,3]

        # OBtain a vector on centreline
        #secVECz
        #t-shoot 18/03/2020 unverified : not avergage but subtract
        secVECz[i,0] = (cdArr[ii,1]-cdArr[ii-1,1])
        secVECz[i,1] = (cdArr[ii,2]-cdArr[ii-1,2])
        secVECz[i,2] = (cdArr[ii,3]-cdArr[ii-1,3])
        
        ii = 0
        s2 = 0
        while rang1 > s2:
            s1 = sd[ii,0]
            s2 = sd[ii+1,0]
            # this minus is used to match angle of attack effect with the vector transform.... verify
            t1 = -sd[ii,1]
            t2 = -sd[ii+1,1]
            ii = ii + 1
        #interpolation to find local twist
        prog = (rang1-s1)/(s2-s1)
        twist = t1 + (t2-t1)*prog
        #print(twist)
        
        #(also add dihedral at some point)
        #position of third point for surface creation (~~~~ eventually provide drawing of this ?~~~~)

        #export second vector
        secVECy[i,0] = 0
        secVECy[i,1] = 100
        secVECy[i,2] = 100*math.tan(twist*math.pi/180)
        
        i = i + 1
        
    #These hashed lines can be used to visualize the operations in CATIA:
    #silo = "D:\\IDPcode\\CatiaFiles\\TEST.CATPART"
    #partDocument1.SaveAs(silo)
    #breakthis   

    #print(secVECy)
    #print(secPTS,secVECy,secVECz)
    return(secPTS, secVECy, secVECz)

#secPTS = centPTS("IDP_spariteration_A105_B001",400,16) 
#secPTS = centPTS("IDP_SparIteration0305_A026_B004",500,8) 
#print(secPTS)
# get centreline points


def braidAV(secPTS,secVECy,secVECz, BraidFile,secs,varVal):
    secLen = varVal['span']/secs
    #the output is warp-angle, weft-angle, warp-pitch, weft-pitch for 
    output = np.zeros([(secs*12),5])
    

    
    #WW corresponds to warp-weft binary options
    WW = 0
    #boundary conditions matrix to be populated
    segBC = np.zeros([1,7])
    while WW < 2:
        i = 0 
        #i loops through sections, warp, then weft
        while i < secs:
            #SQL connection create
            cnnF,crrF = cnt_X('NCC')
            
            # select min-max y and x
            
            #z direction boundary conditions, defined in original coordinate system
            low = i*secLen
            high = (i+1)*secLen
            mid = (low+high)/2
            #obtain relevant braiding data for the 12 sections around the x-section
            query = "SELECT * FROM "+BraidFile+" where (z < "+str(high)+") and (z > "+str(low)+") and (warpORweft ="+str(WW)+" )"
            #print(query)
            crrF.execute(query)
            #get results
            rows = crrF.fetchall()
            #reference points on centreline
            xAnchor = float(secPTS[i,0])
            yAnchor = float(secPTS[i,1])
            zAnchor = float(secPTS[i,2])

            
            
            dc_X('NCC',cnnF,crrF)
            secMATlocal = np.zeros([1,6])         
            #get all the braiding data and translate them to local coordinate systems
            for row in rows:
                r = np.zeros([1,6])                
                #create the translated coordinates 
                
                #new y and new z coordinate systems are imported to this script, new x is calculated
                secVECx = np.cross(secVECy[i,:],secVECz[i,:])
                #vectors of new coordinate system
                cSYS2 = np.array(([secVECx[0],secVECx[1],secVECx[2]],[secVECy[i,0],secVECy[i,1],secVECy[i,2]],[secVECz[i,0],secVECz[i,1],secVECz[i,2]]))
                
                point1 = np.array([0,0,0])
                #3d coordinates of new coordinate system
                point2 = np.array([xAnchor,yAnchor,zAnchor])
                #corresponds to default coordinate system
                cSYS1 = np.array(([1,0,0],[0,1,0],[0,0,1]))
                #GCP is the point with braiding information imported, referenced in global coordinate system
                GCP = np.array([float(row[2]),float(row[3]),float(row[4])])
                
                #use the function to translate coordinates 

                
                LCP = GlobalToLocal(point1,point2, cSYS1,cSYS2,GCP)

                #populate matrix for further processing 
                r[0,0],r[0,1],r[0,2],r[0,3],r[0,4],r[0,5] = row[1],LCP[0],LCP[1],LCP[2],row[5],row[9]
                #append all the processed data into one matrix
                secMATlocal = np.concatenate((secMATlocal,r),axis=0)
            #delete the first row, initial zeroes
            secMATlocal = np.delete(secMATlocal, (0), axis=0)
    

            #min-max should be calculated in secondary coordinate system
            xMAX = max(secMATlocal[:,1])
            yMAX = max(secMATlocal[:,2])
            xMIN = min(secMATlocal[:,1])
            yMIN = min(secMATlocal[:,2])           
            
            
            #THIS SECTION IS NEW - ADJUST - AND TEST
            
            #section treshold ~~ one day include as a parameter
            #Calculate treshold requirement based on RAD, large radius means greater portion is part of the section
            s = varVal['span']

            c_L = 150 #default chord_0 size
            yu = 0
            while yu < 3:
                c1= varVal['chord_'+str(yu)]
                c2= varVal['chord_'+str(yu+1)]
                s1 = yu*s/3
                s2 = (yu+1)*s/3
                if s1 < mid < s2:
                    c_L = ((mid-s1)/(s2-s1))*(c2-c1)+c1
                yu = yu + 1
            c_R = c_L/varVal['RAD']
            #the 0.7 can be different for x and y...this should be done based on the width of the spar eventually
            #50 is the base ratio c/R --subject to change if default values change
            if c_R < 50:
                #From last checs it appears that the gradients, eg. 0.2/350, can be a bit increased
                sty = 0.55 + (0.2/200)*(c_R-50)
                stx = 0.65 + (0.2/200)*(c_R-50)
            else:
                sty = 0.55 + (0.2/40)*(c_R-50)
                stx = 0.65 + (0.2/40)*(c_R-50)
            #sty = 0.7
            #stx = 0.6

            
            #segBC columns: section ID, xMax,xMIn,yMax,yMin,zMax,zMin
            #run only for warp, no point duplicating data
            
            #This section is part specific.
            if WW < 1:
                segBC = np.concatenate((segBC,(np.matrix([(i*12+1),9999999,stx*xMAX,9999999,sty*yMAX,high,low]))),0)
                segBC = np.concatenate((segBC,(np.matrix([(i*12+2),9999999,stx*xMAX,sty*yMAX,0,high,low]))),0)
                segBC = np.concatenate((segBC,(np.matrix([(i*12+3),9999999,stx*xMAX,0,sty*yMIN,high,low]))),0)
                segBC = np.concatenate((segBC,(np.matrix([(i*12+4),9999999,stx*xMAX,sty*yMIN,-999999,high,low]))),0)
                segBC = np.concatenate((segBC,(np.matrix([(i*12+5),stx*xMAX,0,sty*yMIN,-999999,high,low]))),0)
                segBC = np.concatenate((segBC,(np.matrix([(i*12+6),0,stx*xMIN,sty*yMIN,-999999,high,low]))),0)
                segBC = np.concatenate((segBC,(np.matrix([(i*12+7),stx*xMIN,-999999,sty*yMIN,-999999,high,low]))),0)
                segBC = np.concatenate((segBC,(np.matrix([(i*12+8),stx*xMIN,-999999,0,sty*yMIN,high,low]))),0)
                segBC = np.concatenate((segBC,(np.matrix([(i*12+9),stx*xMIN,-999999,sty*yMAX,0,high,low]))),0)
                segBC = np.concatenate((segBC,(np.matrix([(i*12+10),stx*xMIN,-999999,9999999,sty*yMAX,high,low]))),0)
                segBC = np.concatenate((segBC,(np.matrix([(i*12+11),0,stx*xMIN,9999999,sty*yMAX,high,low]))),0)
                segBC = np.concatenate((segBC,(np.matrix([(i*12+12),stx*xMAX,0,9999999,sty*yMAX,high,low]))),0)

            #~~~~ there might be more efficient way of assigning these, future work~~~~
            #ac1,ac2,ac3,ac4 = [],[],[],[]
            #pc1,pc2,pc3,pc4 = [],[],[],[]        
            af1, af2, af3, af4, af5, af6, af7, af8, af9, af10, af11,af12 = [],[],[],[],[],[],[],[],[],[],[],[]
            pf1, pf2, pf3, pf4, pf5, pf6, pf7, pf8, pf9, pf10, pf11, pf12 = [],[],[],[],[],[],[],[],[],[],[],[]

            sz = np.size(secMATlocal,0)
            #print(sz)
            #go through each set of values within the spanwise zone
            #assign each set of values to one of the 12 sectiosn (4 corners, and 8 straight sectiosn)
            iii = 0
            while iii < sz:
                if secMATlocal[iii,1] > (stx*xMAX) and secMATlocal[iii,2] >(sty*yMAX):
                    #top right corner
                    af1.append(float(secMATlocal[iii,4]))
                    pf1.append(float(secMATlocal[iii,5]))
                elif secMATlocal[iii,1] > (stx*xMAX) and secMATlocal[iii,2] < (sty*yMIN):
                    #bottom right corner
                    af4.append(float(secMATlocal[iii,4]))
                    pf4.append(float(secMATlocal[iii,5]))
                elif secMATlocal[iii,1] < (stx*xMIN) and secMATlocal[iii,2] < (sty*yMIN):
                    #bottom left corner
                    af7.append(float(secMATlocal[iii,4]))
                    pf7.append(float(secMATlocal[iii,5]))  
                elif secMATlocal[iii,1] < (stx*xMIN) and secMATlocal[iii,2] > (sty*yMAX):
                    #top left corner
                    af10.append(float(secMATlocal[iii,4]))
                    pf10.append(float(secMATlocal[iii,5]))
                elif secMATlocal[iii,1] > (stx*xMAX) and secMATlocal[iii,2] < (sty*yMAX) and secMATlocal[iii,2] > 0:
                    #right side, upper straight section
                    af2.append(float(secMATlocal[iii,4]))
                    pf2.append(float(secMATlocal[iii,5]))   
                elif secMATlocal[iii,1] > (stx*xMAX) and secMATlocal[iii,2] > (sty*yMIN) and secMATlocal[iii,2] < 0:
                    #right side, lower straight section
                    af3.append(float(secMATlocal[iii,4]))
                    pf3.append(float(secMATlocal[iii,5]))
                elif secMATlocal[iii,1] < (stx*xMAX) and secMATlocal[iii,2] < (sty*yMIN) and secMATlocal[iii,1] > 0:
                    #bottom side, right straight section
                    af5.append(float(secMATlocal[iii,4]))
                    pf5.append(float(secMATlocal[iii,5]))
                elif secMATlocal[iii,1] > (stx*xMIN) and secMATlocal[iii,2] < (sty*yMIN) and secMATlocal[iii,1] < 0:
                    #bottom side, left straight section
                    af6.append(float(secMATlocal[iii,4]))
                    pf6.append(float(secMATlocal[iii,5]))
                elif secMATlocal[iii,1] < (stx*xMIN) and secMATlocal[iii,2] > (sty*yMIN) and secMATlocal[iii,2] < 0:
                    #left side, bottom straight section
                    af8.append(float(secMATlocal[iii,4]))
                    pf8.append(float(secMATlocal[iii,5]))        
                elif secMATlocal[iii,1] < (stx*xMIN) and secMATlocal[iii,2] < (sty*yMAX) and secMATlocal[iii,2] > 0:
                    #left side, top straight section
                    af9.append(float(secMATlocal[iii,4]))
                    pf9.append(float(secMATlocal[iii,5]))        
                elif secMATlocal[iii,1] > (stx*xMIN) and secMATlocal[iii,2] > (sty*yMAX) and secMATlocal[iii,1] < 0:
                    #top side, left straight section
                    af11.append(float(secMATlocal[iii,4]))
                    pf11.append(float(secMATlocal[iii,5]))
                elif secMATlocal[iii,1] < (stx*xMAX) and secMATlocal[iii,2] > (sty*yMAX) and secMATlocal[iii,1] > 0:
                    #top side, right straight section
                    af12.append(float(secMATlocal[iii,4]))
                    pf12.append(float(secMATlocal[iii,5]))  
                iii = iii + 1
            
                    
            #the output is warp-angle, weft-angle, warp-pitch, weft-pitch for
            #WW serves as a toggle between warp and weft
            ii = 0
            while ii < 12:
                #the reference point
                BuildCommand = "output[(i*12)+"+str(ii)+",0] = (i*12)+"+str(ii+1)+""
                exec(BuildCommand)
                #angle 
                BuildCommand = "output[(i*12)+"+str(ii)+",(1+WW)] = mean(af"+str(ii+1)+")"
                exec(BuildCommand)
                #pitch
                BuildCommand = "output[(i*12)+"+str(ii)+",(3+WW)] = mean(pf"+str(ii+1)+")"
                exec(BuildCommand)        
                ii = ii + 1
            i = i + 1
            
        WW = WW + 1
    
         
    #if data is missing for a section, average the values based on neighbouring sections
    #loop through all braid data rows
    iv = 0 
    count = 0
    while iv < output.shape[0]:
        #loop through all potential 0 values
        iiv = 1
        while iiv < 5:
            #in an event of zero value being present
            if output[iv,iiv] == 0:
                c = 0
                v = 0
                #for the last of the xs-wise sections (12th)
                if (iv+1)/12 == int((iv+1)/12):
                    #add to division count for averaging
                    c = c + 2
                    #add the value of before and after sections
                    v = v + output[iv-1,iiv] +output[iv-11,iiv]
                #for the first of the xs-wise sections (1st)
                elif (iv)/12 == int((iv)/12):
                    c = c + 2
                    v = v + output[iv+1,iiv] + output[iv+11,iiv]
                #for all but the first and last of the xs-sections
                else:
                    c = c + 2
                    v = v + output[iv+1,iiv] + output[iv-1,iiv]
                # for all but tip section of the spar
                if (iv+12) < output.shape[0]:
                    #add to division count for averaging
                    c = c + 1
                    #add the next spanwise section for averaging
                    v = v + output[iv+12,iiv]
                #for all but the root section of the spar
                if (iv-12) >0:
                    c = c + 1
                    v = v + output[iv-12,iiv]
                print("0 value encountered, average of neighbouring sections is used:",output[iv,iiv])       
                count = count + 1
                if count > 100:
                    print("100 materials were replaced, TROUBLESHOOT!")
                    print("___simulation being crashed __")
                    np.set_printoptions(threshold=sys.maxsize)
                    print(output)
                    breakhere
            iiv = iiv + 1
        iv = iv + 1
    segBC = np.delete(segBC, (0), axis=0)

    
    #Troubleshooting section, enable in case of suspected error:
    #np.set_printoptions(threshold=sys.maxsize)
    variable7 = output
    with open("Temporary\\Tshoot_segmentation_output.txt", "w") as text_file:
        text_file.write(str(variable7))
        
    #segBC in transformed coordinates 
    #print("",secPTS,"")
    #print("",secVECy,"")
    #print("",secVECz,"")
    return(output,segBC,secPTS,secVECy,secVECz)
    
def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)
