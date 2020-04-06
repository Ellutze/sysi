# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 11:43:16 2018

@author: jk17757
"""

def replace():
    with open('tobereplaced.txt','r') as file:
        filedata = file.read()
        filedata = filedata.replace('''’''',"""'""")
        print(filedata)

import numpy as np
def foil_to_spar(foil,spar1,spar2):
    #load airfoil from scripting folder
    airfoil=np.loadtxt("aerofoilcollection\\"+foil,skiprows=1)
    
    spar = np.zeros([2,2])
    #loop through points around airfoil
    #filter for points within given spar range
    for i in range(0,len(airfoil)):
        #check for transition points that might need generating
        if airfoil[(i-1),0] < spar1 or spar2 < airfoil[(i-1),0]:
            x = False
        else:
            x = True
        if airfoil[(i),0] < spar1 or spar2 < airfoil[(i),0]:
            y = False
        else:
            y = True     

        if y == True and x == False:
            #previous point was outside spar, current point is spar
            #creates additional point for the precise edge of spar
            if airfoil[(i-1),0] < airfoil[(i),0]:
                xi = spar1
                diffx1 = spar1 - airfoil[(i-1),0]
                diffx2 = airfoil[i,0] - spar1
                diffy = airfoil[i,1] - airfoil[(i-1),1]
                prop = diffy*(diffx2/(diffx1+diffx2))
                yi = airfoil[(i-1),1] + prop
                sparx = np.array([xi,yi])
                spar = np.vstack((spar,sparx))
            else:
                xi = spar2 
                diffx1 = spar2 - airfoil[i,0]
                diffx2 = airfoil[(i-1),0] - spar2 
                diffy = airfoil[(i-1),1] - airfoil[(i),1]
                prop = diffy*(diffx2/(diffx1+diffx2))
                yi = airfoil[(i),1] + prop
                sparx = np.array([xi,yi])
                spar = np.vstack((spar,sparx))

        if y == False and x == True:
            #previous point was spar, current point is outside the boundary
            #creates additional point for precise edge of spar
            if airfoil[(i-1),0] < airfoil[(i),0]:
                xi = spar2
                diffx1 = spar2 - airfoil[(i-1),0]
                diffx2 = airfoil[i,0] - spar2
                diffy = airfoil[i,1] - airfoil[(i-1),1]
                prop = diffy*((diffx2/(diffx1+diffx2)))
                yi = airfoil[(i-1),1] + prop
                check = xi - spar2
                #check for points that are too close to existing points, and ignore those
                 #potential imprecision caused?
                if 0.01 < abs(check):
                    sparx = np.array([xi,yi])
                    spar = np.vstack((spar,sparx))
            else:
                xi = spar1
                diffx1 = spar1 - airfoil[i,0]
                diffx2 = airfoil[(i-1),0] - spar1
                diffy = airfoil[(i-1),1] - airfoil[(i),1]
                prop = diffy*((diffx2/(diffx1+diffx2)))
                check = xi - spar1
                #check for points that are too close to existing points, and ignore those
                #potential imprecision caused?
                if 0.01 < abs(check):
                    sparx = np.array([xi,yi])
                    spar = np.vstack((spar,sparx)) 
        if y == True and x ==True: 
            sparx = np.array([airfoil[i,0],airfoil[i,1]])
            spar = np.vstack((spar,sparx))          

    spar = spar[2:,:]
    #plt.plot(spar[:,0],spar[:,1])
    return(spar)

