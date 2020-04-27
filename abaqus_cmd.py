
import subprocess
#import os
### GOBO #### this runs command line to run python (3.6==> 3.6)
def cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()#[0].strip()
    print(command)
    print(proc_stdout)
    

#cmd("abaqus cae noGUI=abaqus_inst.py")