# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 12:54:41 2020

@author: jjjku
"""
import sys
import time
import subprocess
import os
from SUAVE.Methods.Aerodynamics.AVL.read_results import read_results
from SUAVE.Methods.Aerodynamics.AVL.purge_files  import purge_files
from SUAVE.Core                                  import redirect
import math


def sysiAVL(varVal,name):
    #remove previous output file if it exists
    try:
        os.remove("D:\\pythonic\\testing AVL\\output3.txt")
    except:
        print("___")

    Bsec = varVal['span']/3/1000
    c0 = varVal["chord_0"]/1000
    c1 = varVal["chord_1"]/1000
    c2 = varVal["chord_2"]/1000
    c3 = varVal["chord_3"]/1000
    t0 = varVal["twist_0"]
    t1 = varVal["twist_1"]
    t2 = varVal["twist_2"]
    t3 = varVal["twist_3"]
    #reference surface area
    Sref = 2*(Bsec*(c0+c1)/2)+(Bsec*(c1+c2)/2)+(Bsec*(c2+c3)/2)
    #reference span
    Bref = 2*varVal['span']/1000
    #reference cord
    Cref = Sref/Bref
    
    

    newFile = ""
    with open('D:\\pythonic\\testing AVL\\notSupergee.avl', 'r') as AVLtxt:
        for line in AVLtxt:
            if "! name" in line: #name  "! name"
                newFile = newFile + name + "! name" + """\n"""
            elif "Sref   Cref   Bref" in line: #span , surface refernces   "!   Sref   Cref   Bref   reference area, chord, span"
                newFile = newFile + str(Sref) + "   " +str(Cref) + "   " +str(Bref) + "   " + "!   Sref   Cref   Bref "+ """\n"""
            elif "_section_1" in line: #  !_section_1
                newFile = newFile + "0 0 0 " + str(c0) + " " + str(t0) + """\n"""
            elif "!_afil_1" in line: #  !_afil_1
                newFile = newFile + "D:\\pythonic\\testing AVL\\" + varVal["airfoil_0"] + """\n"""
            elif "!_section_2" in line: #  !_section_2
                zLoc = Bsec*math.tan(varVal["dihedral_1"]*math.pi/180)
                xLoc = 0.25*c0+Bsec*math.tan(varVal["sweep_1"]*math.pi/180)-0.25*c1
                newFile = newFile + str(xLoc)+ "   " + str(Bsec)+ "   " + str(zLoc)+ "   " + str(c1) + " " + str(t1) + """\n"""
            elif "!_afil_2" in line: #  !_afil_2
                newFile = newFile + "D:\\pythonic\\testing AVL\\" + varVal["airfoil_1"] + """\n"""
            elif "!_section_3" in line: #  !_section_3
                zLoc = zLoc + Bsec*math.tan(varVal["dihedral_2"]*math.pi/180)
                xLoc = xLoc + 0.25*c1+Bsec*math.tan(varVal["sweep_2"]*math.pi/180)-0.25*c2
                newFile = newFile + str(xLoc)+ "   " + str(2*Bsec)+ "   " + str(zLoc)+ "   " + str(c2) + " " + str(t2) + """\n"""
            elif "!_afil_3" in line: #  !_afil_3
                newFile = newFile + "D:\\pythonic\\testing AVL\\" + varVal["airfoil_2"] + """\n"""
            elif "!_section_4" in line: #  !_section_4
                zLoc = zLoc + Bsec*math.tan(varVal["dihedral_3"]*math.pi/180)
                xLoc = xLoc + 0.25*c2+Bsec*math.tan(varVal["sweep_3"]*math.pi/180)-0.25*c3
                newFile = newFile + str(xLoc)+ "   " + str(3*Bsec)+ "   " + str(zLoc)+ "   " + str(c3) + " " + str(t3) + """\n"""
            elif "!_afil_4" in line: #  !_afil_4
                newFile = newFile + "D:\\pythonic\\testing AVL\\" +varVal["airfoil_3"] + """\n"""  
            else:
                newFile = newFile + line
    
    print(newFile)
    # add line "#created by xxx at xxx on xxx "
    
    
    with open("D:\\pythonic\\testing AVL\\"+name+".avl", "w") as text_file:
        text_file.write(newFile)
    
    with open("D:\\pythonic\\testing AVL\\AVL_DECK.deck",'r') as commands:
        
            

        geometry = "D:\\pythonic\\testing AVL\\"+name+".avl"
        avl_call = "avl"
        avl_run = subprocess.Popen([avl_call,geometry],stdout=sys.stdout,stderr=sys.stderr,stdin=subprocess.PIPE)
        for line in commands:
            avl_run.stdin.write(line.encode('utf-8'))
            avl_run.stdin.flush()
            
          
name = "test1"            
varVal = {'span': 400,'twist_0': 0,'chord_0': 150,'no_layers': 8,'twist_1':0,'chord_1':150,'matrix':"Bakelite EPR-L20",'twist_2':0,'chord_2':150,'reinforcement':"AKSAca A-42",'twist_3':0,'chord_3':150,
      'mesh_size':2.3,'airfoil_0':"clarkYdata.dat",'sweep_0':0,'spools':168,'airfoil_1':"clarkYdata.dat",'sweep_1':0,'RAD':3, 'airfoil_2':"clarkYdata.dat",'sweep_2':0,'mandrel_speed':4,'airfoil_3':"clarkYdata.dat",'sweep_3':0,
      'dihedral_0':0,'dihedral_1':0,'dihedral_2':0,'dihedral_3':0,'c_min':0.30,'c_max':0.45,'guide_rad':700,'IMD':500,'inlet_temp':410,'tool_temp':300,
      'inlet_pressure':200000000,'vent_pressure':10,'flow_rate':(1.0*10**(-8))}
sysiAVL(varVal,name)

#for integration:
#new variables? into SQL, into dictionary
#