import numpy as np
import subprocess

#This function allows for running a subprocess from python using cmd.
def cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True, cwd="C:\\Program Files\\ESI Group\\Visual-Environment\\15.0\\Windows-x64")
    proc_stdout = process.communicate()#[0].strip()
    print(command)
    print(proc_stdout)

#e.g.:
#cmd("VEBatch -activeconfig Trade:CompositesandPlastics -activeapp VisualRTM -sessionrun D:\\IDPcode\\SpecialRTMTestIDP\\IDP_zip_2.0\\IDPcode\\untitled9.py")