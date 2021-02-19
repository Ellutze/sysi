# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 13:09:16 2021

@author: jjjku
"""
import numpy as np


def forceDist():
    #Extract data from output file from AVL run
    Cl = np.zeros([1,2])
    o = 0
    with open('temporary\\output3.txt', 'r') as AVLtxt:
        
        for line in AVLtxt:
            #used as start and finishe of area of interest
            if " Strip Forces referred to Strip Area, Chord" in line or "  Surface # 2     Wing (YDUP)" in line:
                o = o + 1
            if 0 < o < 2 and "e" not in line:
                #obtain cl and location from the line
                try:
                    t = str(line)
                    cl = float(t.split("   ")[8])
                    ds = float(t.split("  ")[3])        
        
                    Cl_temp = np.matrix([ds,cl])
                    Cl = np.concatenate((Cl,Cl_temp),axis=0)
                except:
                    print("empty")
    return(Cl)