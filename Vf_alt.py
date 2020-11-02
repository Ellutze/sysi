# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 11:54:43 2020

@author: jakub.kucera
"""
import math

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
    N = math.sqrt((L*2)**2-(Fr*2)**2)
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
    print(A1t)
    print(A2t)
    print(A3t)

    #introducing eliptical yarn
    #b is the new width radius
    b = Fr*2
    Area = math.pi*((Fr)**2)
    #new thickness is the height of the elipse, which keeps same area
    newThick = Area/(math.pi*b)
    
    #area of fibre maintained just encompasing rectangle is created in place of square
    Vf1 = Area/(2*b*newThick*2)
    print("VF1",Vf1)
    Vf2 = Vf1*0.66 #an estimate of the volume fraction with angled yarn going through thickness
    #this should eventually be improved if this method is to be used
    Vf3 = 0
    Vf = (A3t/Atot)*Vf3+(A2t/Atot)*Vf2+(A1t/Atot)*Vf1
    return(Vf)


angle = 35*math.pi/180
Vf = Vf_opt2(angle,4,1)
print(Vf)
    
    
    