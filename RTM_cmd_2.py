
import numpy as np
import RTM_postProc
import time
import subprocess
    
def cmd2(command,RTMFile):
    #Passes command to command line.
    #Required due to Visual-RTM having it's own library of python packages.
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, cwd="C:\\Program Files\\ESI Group\\Visual-Environment\\15.0\\Windows-x64")
    proc_stdout = process.communicate()#[0].strip()
    print(command)
    print(proc_stdout)
    
    
    #After running the command, wait for results.
    results = False
    while results == False:
        try: 
            maxFill,I_time = RTM_postProc.outputS1(RTMFile)
            results = True
            subprocess.Popen.terminate()
        except:
            print("Result not available yet, waiting")
            time.sleep(20)
            pass
    return(maxFill,I_time)

#cmd("VEBatch -activeconfig Trade:CompositesandPlastics -activeapp VisualRTM -sessionrun D:\\IDPcode\\SpecialRTMTestIDP\\IDP_zip_2.0\\IDPcode\\RTM_testing.py")