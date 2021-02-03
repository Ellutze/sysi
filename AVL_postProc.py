# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 13:09:16 2021

@author: jjjku
"""
import numpy as np


def forceDist():

    Cl = np.zeros([1,2])
    o = 0
    with open('D:\\pythonic\\testing AVL\\output3.txt', 'r') as AVLtxt:
    
        for line in AVLtxt:
            if " Strip Forces referred to Strip Area, Chord" in line or "  Surface # 2     Wing (YDUP)" in line:
                o = o + 1
            if 0 < o < 2 and "e" not in line:
                print(line)
                #f = line.split("1")[0]
                #h = "t"+f+"t"
                #print(h)
                #breakhere
                try:
                    t = str(line)
                    cl = float(t.split("   ")[8])
                    print(cl)
                    ds = float(t.split("  ")[3])
                    print(line)
        
        
                    Cl_temp = np.matrix([ds,cl])
                    Cl = np.concatenate((Cl,Cl_temp),axis=0)
                except:
                    print("empty")
    print(Cl)
    return(Cl)