# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 12:33:53 2021

@author: jjjku
"""
import matplotlib.pyplot as plt

import subprocess
from AVL_postProc import forceDist
import numpy as np
#import os
### GOBO #### this runs command line to run python (3.6==> 3.6)

from default_var_dict import getBase

def avl_main(varVal,name):
    #values that are set, but might became iterated variables in future
    #velocity of key manoeuvre m/s
    v = 40
    #density of air kg/m3
    ro = 1.225
    #key manoeuvre load factor
    lf = 2.5
    

    varVal["name"] = name
    np.save("temporary\\varVal.npy", varVal)
    t_cmd = "conda run python AVL_inputs.py"
    cmd(t_cmd)
    
    Cl = forceDist()
    
    #this section could potentially be in Abaqus
    #The Cl is used to to define the forces on each segment
    span = varVal["span"]
    sg = span/20
    
    chord = np.matrix([[0,varVal["chord_0"]*(varVal["c_max"]-varVal["c_min"])],
                      [span/3,varVal["chord_1"]*(varVal["c_max"]-varVal["c_min"])],
                      [2*span/3,varVal["chord_2"]*(varVal["c_max"]-varVal["c_min"])],
                      [span,varVal["chord_3"]*(varVal["c_max"]-varVal["c_min"])]])
    print(chord)
    
    F = np.zeros([20,2])
    print(F)
    i = 0 
    while i < 20:
        ii= 0
        spd = (sg/2 + i*sg)/1000
        print(spd)
        while ii < Cl.shape[0]-1:
            if Cl[ii,0] <= spd < Cl[ii+1,0]:
                loc_cl = Cl[ii,1] + (spd-Cl[ii,0])/(Cl[ii+1,0]-Cl[ii,0])*(Cl[ii+1,1]-Cl[ii,1])
            ii = ii + 1
        ii = 0 
        while ii < chord.shape[0]-1:
            if chord[ii,0] <= spd < chord[ii+1,0]:
                loc_chord = chord[ii,1] + (spd-chord[ii,0])/(chord[ii+1,0]-chord[ii,0])*(chord[ii+1,1]-chord[ii,1])
            ii = ii + 1        
        
        S = loc_chord*sg/1000000 # in m2
        #lift coefficient formula (N)
        L = lf*loc_cl*S*ro*v**2
        F[i,0] = spd
        F[i,1] = L
        
        i = i + 1
        
    #output CL and F to a SQL table
    np.save("avl_files\\"+name+".npy", F, allow_pickle=True, fix_imports=True)
    np.savetxt("avl_files\\"+name+".csv", F, delimiter=",")
    return(Cl,F)
    
def cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()#[0].strip()
    print(command)
    print(proc_stdout)

#varVal, xxx,yyy = getBase()
#name = "testX2"
#Cl,F = avl_main(varVal,name)

#plt.plot(Cl[:,0],Cl[:,1])
#plt.plot(F[:,0],F[:,1])