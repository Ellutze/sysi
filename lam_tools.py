import numpy as np
from numpy import matrix
import math
from IDP_databases import cnt_X,dc_X
#from mysql.connector import MySQLConnection, Error
#from IDP_cheats import togglePulse
#from python_mysql_dbconfig import read_db_config


def RoM(Vff,Ef1,Ef2,Em,Gf,Gm,vf,vm):
    #rule of mixtures
    E1 = Ef1*Vff+Em*(1-Vff)
    E2 = 1/(((1-Vff)/Em)+(Vff/Ef2))
    v12 = Vff*vf + (1-Vff)*vm
    G = Gf*Gm/(Vff*Gm+(1-Vff)*Gf)
    #print(E1,E2,v12,G)
    return(E1,E2,v12,G)
    
#print(E1,E2)
    
def Vf_opt2(alpha,p,Fr):
    #takes Angle in radians, Pitch in mm, and Fibre radius in mm
    
    #for volume fraction calculations 35deg and 65 are the same, the diagram
    #has been created for above 45 degrees, hence lower angles than 45 are 
    #translated to their above 90 equivalents.
    if alpha < (math.pi/4):
        u = math.pi/4-alpha
        alpha = u + math.pi/4
    
    #total rectangel size 
    
    beta = math.pi/2 - alpha
    #side of rectangle S
    S = p/math.cos(beta)
    #rectangle diagonal H
    H = S/math.sin(beta)
    #Top side of rectangel T
    T = H*math.cos(beta)
    #top view area of rectangle
    Atot = T*S
    
    #the unit cell is split into 3 area types, yarns crossing (1),single yarn(2), no-yarn (3)
    zeta = math.pi-2*alpha
    omega = math.pi/2-zeta
    #x,m,L,K,K2,N,V are calculation lines on diagram
    x = Fr*2/math.cos(omega)
    m = Fr*2*math.tan(omega)
    A11 = m*Fr*2
    L = x*math.sin(beta)
    N = math.sqrt(abs((L*2)**2-(Fr*2)**2))
    A12 = N*Fr*2
    A1 = A12 + A11
    A1t = A1*2
    #above corresponds to segment type 1
    
    #segment type 2
    V = 2*Fr/math.tan(zeta)
    K2 = (p-(2*Fr))/math.cos(omega)
    K = K2-V
    A21 = V*Fr*2
    A22 = K*Fr*2
    A2 = A21+A22
    A2t = A2*4
    
    #segment type 3
    A3t = Atot - A2t -A1t


    #introducing eliptical yarn
    #b is the new width radius
    b = Fr*2
    Area = math.pi*((Fr)**2)
    #new thickness is the height of the elipse, which keeps same area
    newThick = Area/(math.pi*b)
    
    #area of fibre maintained just encompasing rectangle is created in place of square
    Vf1 = Area/(2*b*newThick*2)
    Vf2 = Vf1*0.66 #an estimate of the volume fraction with angled yarn going through thickness
    #this should eventually be improved if this method is to be used
    Vf3 = 0
    Vf = (A3t/Atot)*Vf3+(A2t/Atot)*Vf2+(A1t/Atot)*Vf1
    return(Vf)

def VolumesF(pitch1,pitch2,fR,angle1,angle2):
    #print("pitch1", pitch1, "pitch2",pitch2)
    #for now assume fibre to be circle
    
    #pitch cannot be smaller than 2 radii of fibre
    #(assumption about lack of fibre deformation?)
    
    
    #introducing eliptical yarn
    #b is the new width radius
    b = fR*2
    Area = math.pi*fR**2
    #new thickness is the height of the elipse, which keeps same area
    newThick = Area/(math.pi*b)
    
    
    if pitch1 < 2*b:
        pitch1 = 2*b
    if pitch2 < 2*b:
        pitch2 = 2*b
    fA = math.pi*newThick*b
    tA1 = 2*newThick*pitch1
    Vf1 = fA/tA1
    tA2 = 2*newThick*pitch2
    Vf2 = fA/tA2
    #Cap imposed on volume fraction
    cap = 0.7
    t1 = newThick*2
    if Vf1 > cap:
        diff = Vf1-cap
        t1 = diff/t1+t1
        Vf1 = cap
        print("volume fraction capped") 
    t2 = newThick*2
    if Vf2 > cap:
        diff = Vf2-cap
        t2 = diff/t2+t2
        Vf1 = cap
        print("volume fraction capped")
        
    t = t1+t2
    
    #testing out method 2 for Vf
    aav = (angle1+angle2)/2
    pav = (pitch1+pitch2)/2
    Vf_comp = Vf_opt2(aav,pav,fR)
    Vf = (Vf1+Vf2)/2
    print("comparison of Vf methods, Vf1:",Vf,"Vf2:",Vf_comp)
    
    #swap the Vf options here
    #return (Vf_comp,Vf_comp,t) # New method
    return (Vf1,Vf2,t) #Old method

def ABD(seq,sym,lamina1,lamina2,angle1,angle2):

    #material data
    E11 = lamina1[0] #Mpa
    E22 = lamina1[1] #Mpa
    v12 = lamina1[2]
    if v12 < 0:
        print("poisson from lamina negative")
    G12 = lamina1[3] #Mpa
    t = lamina1[4] #mm
    
    #q matrix for the particular material (include loop if more materials)
    Q11 = (E11**2)/(E11-v12*E22)
    Q12 = (v12*E11*E22)/(E11 - E22*(v12**2))
    Q22 = (E11*E22)/(E11-E22*(v12**2))
    Q66 = G12
    Qwarp = matrix([[Q11,Q12,(0)],[Q12,Q22,(0)],[0,0,Q66]])
    
    E11 = lamina2[0] #Mpa
    E22 = lamina2[1] #Mpa
    v12 = lamina2[2]
    if v12 < 0:
        print("poisson from lamina negative")
    G12 = lamina2[3] #Mpa
    t = lamina2[4] #mm
    
    #q matrix for the particular material (include loop if more materials)
    Q11 = (E11**2)/(E11-v12*E22)
    Q12 = (v12*E11*E22)/(E11 - E22*(v12**2))
    Q22 = (E11*E22)/(E11-E22*(v12**2))
    Q66 = G12
    Qweft = matrix([[Q11,Q12,(0)],[Q12,Q22,(0)],[0,0,Q66]])
    
    R = matrix([[1,0,0],[0,1,0],[0,0,2]])
    #if symetric only half needs specifying 
    #symmertry usage can probably be taken out for braiding?~~~~~~~~~~~~~~~
    if sym == "yes":
        le = seq.size
        j = 0
        seq2 = np.zeros([1,le])
        #print(seq2)
        while j < le:
            seq2[0,j] = seq[0,(le-(1+j))]
            j = j + 1
        seq = np.hstack((seq,seq2))
        #print(seq)
    matl = seq.size
    #print(seq)
    #print(matl)
    ttot = matl*t
    
    # assuming symetry for now --- question it later
    #ntot = matl*2
    h0 = -(matl/2)*t+0.5*t
    ABD = np.zeros([6,6])
    
    h = h0
    u = 0
    while u < matl:
        #Qbar for this particular layer 
       
        angle = seq[0,u]
        angle = angle*(math.pi)/180
        
        T = np.zeros([3,3])
        T[0,0] = math.cos(angle)**2
        T[0,1] = math.sin(angle)**2
        T[1,1] = T[0,0]
        T[1,0] = T[0,1]
        T[0,2] = 2*math.sin(angle)*math.cos(angle)
        T[1,2] = -2*math.sin(angle)*math.cos(angle)
        T[2,0] = -math.sin(angle)*math.cos(angle)
        T[2,1] = math.sin(angle)*math.cos(angle)
        T[2,2] = math.cos(angle)**2 - math.sin(angle)**2
        #print(T)
        if seq[0,u] == angle1:
            Qbar = np.linalg.inv(T)*Qwarp*R*T*np.linalg.inv(R)
        elif seq[0,u] == angle2:
            Qbar = np.linalg.inv(T)*Qweft*R*T*np.linalg.inv(R)
        else:
            print("Houston, we got a problem")
        #print(Qbar)
                          
        i = 0
        while i < 3:
            j = 0
            while j < 3:
                ABD[i,j]= ABD[i,j]+Qbar[i,j]*t
                   
                ABD[(i+3),j] = ABD[(i+3),j] + Qbar[i,j]*t*h
                ABD[(i),(j+3)] = ABD[(i+3),j] 
                
                ABD[(i+3),(j+3)] = ABD[(i+3),(j+3)] + Qbar[i,j]*((t**3)/12 + t*h**2)
                j = j + 1   
            i = i + 1
        
        h = h + t
        u = u + 1
        
    np.set_printoptions(precision=3)
    
    #print(u)
    #print(ABD)   
    np.savetxt("foo.csv", ABD, delimiter=",")
    
    
    A = np.matrix([[ABD[0,0],ABD[0,1],ABD[0,2]],[ABD[1,0],ABD[1,1],ABD[1,2]],[ABD[2,0],ABD[2,1],ABD[2,2]]])
    #print(A)
    #B = numpy.matrix([[ABD[3,0],ABD[3,1],ABD[3,2]],[ABD[4,0],ABD[4,1],ABD[4,2]],[ABD[5,0],ABD[5,1],ABD[5,2]]])
    #print(B)
    D = np.matrix([[ABD[3,3],ABD[3,4],ABD[3,5]],[ABD[4,3],ABD[4,4],ABD[4,5]],[ABD[5,3],ABD[5,4],ABD[5,5]]])
    #print(D)
    a = np.linalg.inv(A)
    #b = numpy.linalg.inv(B)
    d = np.linalg.inv(D)
    
    #membrane = used for closed sections
    Exm = 1/(ttot*a[0,0])
    Eym = 1/(ttot*a[1,1])
    Gxym = 1/(ttot*a[2,2])
    vxym = -a[0,1]/a[0,0]
    vyxm = -a[0,1]/a[1,1]
    mxm = -a[0,2]/a[0,0]
    mym = -a[1,2]/a[1,1]
    membrane = [Exm,Eym,Gxym,vxym,vyxm,mxm,mym]
    #print(membrane)
    
    #bending formulas in phone (from textbook- reference?) --- check with elamx when source file found
    Exb = 12/(ttot**3*d[0,0])
    Eyb = 12/(ttot**3*d[1,1])
    Gxyb = 12/(ttot**3*d[2,2])
    vxyb = -d[0,1]/d[0,0]
    vyxb = -d[0,1]/d[1,1]
    mxb = -d[0,2]/d[0,0]
    myb = -d[1,2]/d[1,1]
    #print(Exb, Eyb,Gxyb, vxyb,vyxb,mxb,myb)
    
    #from NASA paper calculation (Nettles,1994) - used to verify the calculations
    Ex = A[0,0]/ttot+(A[0,1]/ttot)*((A[1,2]*A[0,2]-A[0,1]*A[2,2])/(A[1,1]*A[2,2]-A[1,2]**2))+(A[0,2]/ttot)*(-A[0,2]/A[2,2]+(A[1,2]*A[0,1]*A[2,2]-A[0,2]*A[1,2]**2)/(A[1,1]*A[2,2]**2-A[2,2]*A[1,2]**2))
    
    Ey = A[1,1]/ttot+(A[0,1]/ttot)*((A[1,2]*A[0,2]-A[0,1]*A[2,2])/(A[0,0]*A[2,2]-A[0,2]**2))+(A[1,2]/ttot)*(-A[1,2]/A[2,2]+(A[0,2]*A[0,1]*A[2,2]-A[1,2]*A[0,2]**2)/(A[0,0]*A[2,2]**2-A[2,2]*A[0,2]**2))
    
    Gxy = A[2,2]/ttot -A[1,2]**2/(ttot*A[1,1])+(2*A[0,2]*A[0,1]*A[1,1]*A[1,2]-(A[0,1]**2)*(A[1,2]**2)-(A[0,2]**2)*(A[1,1]**2))/(ttot*((A[0,0]*(A[1,1]**2)-(A[0,1]**2)*A[1,1])))
    vxy = (A[0,1]-A[0,2]*A[1,2]/A[2,2])/(A[1,1]-A[1,2]**2/A[2,2])
    vyx = (-A[0,1]+A[0,2]*a[1,2]/A[2,2])/(-A[0,0]+A[0,2]**2/A[2,2])
    #print("new properties")
    #print(Ex,Ey,Gxy,vxy,vyx)
    #G is slightly different, e2 is probably wrong
    
    return (ABD, membrane)
#ABD()
    

 
def ps(pitch1, pitch2,angle1,angle2,varVal):
    
    #get matrix and fibre properties from SQL
    cnnG,crrG = cnt_X('NCC')
    #finds the matrix material
    matrix = varVal['matrix']
    query = """SELECT E,poisson,G,density from matrix_properties where  material_name = '"""+matrix+"""';"""
    crrG.execute(query)
    rows = crrG.fetchall()
    sd = []
    for row in rows:
        sd.append((row))
    #extract the matrix properties
    Em = float(sd[0][0])
    vm = float(sd[0][1])
    Gm = float(sd[0][2])
    Dm = float(sd[0][3])
    #find the fibre material
    fibre = varVal['reinforcement']
    query = """SELECT E1,E2,G12,v12,fibre_dia,density,perme_coeff from fibre_properties where  material_name = '"""+fibre+"""';"""
    crrG.execute(query)
    rows = crrG.fetchall()
    sd = []
    for row in rows:
        sd.append((row))
    #extract the fibre properties
    Ef1 = float(sd[0][0])
    Ef2 = float(sd[0][1])
    Gf = float(sd[0][2])
    vf = float(sd[0][3])
    fR = float(sd[0][4])/2
    Df = float(sd[0][5])
    CII = float(sd[0][6])
    #close SQL handles 
    dc_X('NCC',cnnG,crrG)
    
    seq = np.matrix([angle1,angle2])
    sym = "yes"
    #eliptical thickness now outputted 
    Vf1,Vf2,t = VolumesF(pitch1,pitch2,fR,angle1,angle2)
    #density calculation
    density1 = Df*Vf1 + Dm*(1-Vf1)
    density2 = Df*Vf2 + Dm*(1-Vf2)
    #assuming both layers are the same thickness ~~~~~~~~
    dens = (density1 + density2) /2
    Vf = (Vf1+Vf2)/2
    #print("temporary check, Vf1:",Vf1,"average Vf:",Vf)
    E1,E2,v12,G = RoM(Vf,Ef1,Ef2,Em,Gf,Gm,vf,vm)
    
    #thickness is not too relevant for classical laminate analysis, doubling stacking with same symetry is going to result in same output values
    #t = 2*fR
    lamina1 = [E1,E2,v12,G,t]
    #print("l1",lamina1)

    #second direction
    E1,E2,v12,G = RoM(Vf2,Ef1,Ef2,Em,Gf,Gm,vf,vm)
    #print("output variables 2")
    
    #t = 2*fR
    lamina2 = [E1,E2,v12,G,t]
    #print("l2",lamina2)
    #print(lamina2,"lamina2")
    #print("A1",angle1,"A2",angle2)
    mABD, memProp = ABD(seq, sym,lamina1,lamina2,angle1,angle2)
    #print("memProp",memProp)
    Vf_av = (Vf1 + Vf2)/2
    K1,K2 = permeability(Vf_av,angle1,angle2,CII)
    
    #troubleshooting negative values - delete once sorted
    
    #i=0
    #while i < 5:
    #    if memProp[i] < 0:
    #        print("lamina1",lamina1)
    #        print("lamina2",lamina2)
    #        print(memProp)
     #   i = i + 1


    return(memProp,dens,t,K1,K2,Vf_av,t)
    
def permeability(Vf_av,a1,a2,CII):
    
    #this thing is wrong - when sheared the pitch does not decrease as it does in woven fabric, hence perm. is increased...
    
    #CII will require testing - it is a material property of te reinforcing fibre

    #formula for in plane permeability from unit 5
    KII = (CII*(1-Vf_av)**3)/Vf_av**2 
    sa = 90 - (a1-a2)
    
    #TEST NP.PI FIRST
    Beta = np.pi/4
    sa = sa*np.pi/180
    Fgeo1 = 1/math.cos(np.pi/2-Beta)
    Fgeo2 = math.cos(sa)/math.sin(Beta)
    Fgeo3 = math.cos(sa)/math.sin(Beta-sa)
    Fgeo = (1-Fgeo1+Fgeo2)/(1-Fgeo1+Fgeo3)
    
    K1 = (KII/math.cos(sa))*((math.cos(sa)-Vf_av)/(1-Vf_av))*Fgeo**2
    K2 = (KII/math.cos(sa))*((math.cos(sa)-Vf_av)/(1-Vf_av))*Fgeo**4
    
    return(K1,K2)
    
    
    
    #if sa +, than K1 increaseses and K2 decreases
    #if sa -, than K1 decreases and K2 increases 
    
    
    

#properties from Wang.C, 2016
#Turn the property into name of fibre and name of resin -- script to retreive the values from SQL later
#ps(1,2,2,20, -20,239500,13400,3300,6810,41.3,0.2,0.35)




