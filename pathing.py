# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 10:17:22 2020

@author: jakub.kucera
"""

#This script adjusts paths in scripts that are run from Abaqus and PAM-RTM
import os

def adj():
    lPath = os.path.dirname(os.path.abspath(__file__))
    
    #list of scripts run from unaccessible software
    sfl = ["RTM_toolbox","RTM_surfaces","RTM_run","RTM_PPcmd","RTM_lil_toolbox","abaqus_inst","Abaqus_postproc"]
    for script in sfl:
        f=open(lPath+"\\"+script+".py",'r')
        text = f.readlines()
        f.close()
        
        fw=open(lPath+"\\"+script+".py", 'w')
        for line in text:   
            if 'lPath_auto=' in line:
                line = line.replace(line, """lPath_auto=r'"""+lPath+"""'\n""")
        
            fw.write(line)
        fw.close()