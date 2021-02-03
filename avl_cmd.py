# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 12:33:53 2021

@author: jjjku
"""

import subprocess
from AVL_postProc import forceDist
import numpy as np
#import os
### GOBO #### this runs command line to run python (3.6==> 3.6)

def avl_main(varVal):


    np.save("D:\\pythonic\\testing avl\\temporary\\varVal.npy", varVal)
    t_cmd = "conda run python AVL_inputs.py"
    cmd(t_cmd)
    
    Cl = forceDist()
    
    return(Cl)
    
def cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()#[0].strip()
    print(command)
    print(proc_stdout)

