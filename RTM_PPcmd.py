#Import visual-rtm related libraries.
null='' 
from VgPoint3 import *
from VgPoint2 import *
from VgMatrix import *
import VScn
import VGuiUtl
import VBrowserManager
import VExpMngr
import VCmdGui
import VCmd
import VCmdFramework
import VMaterial
import VMeshMdlr
import VToolKit
import VistaDb
NULL=VistaDb.PythonCNULL() 
import VistaDb
import VHostManager
import VE

#Import common libraries
import numpy as np

#The functions below are used for post processing, where special need to use
#functions available in the GUI exists. 

#automatically adjusted path
lPath_auto='D:\sysi'

def getInit(RTMfile):
    #This is typically run before all the other functions in here to initiate
    #communication with the model.
    var1=VCmd.Activate( 1, r"VHostManagerPlugin.VhmInterface", r"VhmCommand" )
    var2=VCmd.Activate( 1, r"VSessionManager.Command", r"SessionCommand" )
    var3=VCmd.Activate( 1, r"VToolKit.VSectionCutInterface", r"VEAction" )
    ret=VE.ChangeContext( r"Visual-RTM" )
    VE.SetActiveWindow( r"p1w1" )
    ret=VExpMngr.LoadFile( r"D:\\IDPcode\\pamrtm\\mainSimFiles\\"+RTMfile+".vdb", 0 )
    VE.SetCurrentPage( 1 )
    ret=VE.ModelChange( "M  @0" )
    VScn.ExecutePythonInterpeter( r"C:\Program Files\ESI Group\Visual-Environment\15.0\COMMON\Resources\VisualProcessExec\user_scripts\CompositeLoadResult.py" )
    import Viewer
    Viewer.SetTHPdisplayOnOff( 0 )
    VE.Command( r">>> fpmmarkersize(3)" )
    Viewer.SetLogConstantInfo( 0.000000000100000000000000003643 , 1 )

def getPhill(RTMfile):
    #Assuming file is already open.
    
    #Exports file times for each node in the file.
    
    #This functions wasn't used for a while, while changes were made, might
    #not work.
    i = 124

    strX = lPath_auto+"\\pamrtm\\mainsimfiles\\"+str(RTMfile)+"_RESULTS.erfh5"
    #__________________ VtkContourDlg BEGIN __________________
    var4=VCmd.Activate( 1, r"VToolKit.VToolKitInterface", r"VtkContourDlg" )
    VCmd.SetStringValue( var4, r"FileName", strX )
    VCmd.SetStringValue( var4, r"ContourMethod", r"ByEntity" )
    VCmd.SetStringValue( var4, r"ContourParentName", r"NODE" )
    VCmd.SetStringValue( var4, r"ContourDisplayName", r"FILLING_FACTOR" )
    VCmd.SetStringValue( var4, r"Encoding", r"Scalar" )
    VCmd.SetIntValue( var4, r"ContourGrayFlag", 1 )
    ret=VCmd.ExecuteCommand( var4, r"ApplyContour" )
    VCmd.SetStringValue( var4, r"SpectrumDispMode", r"Smeared" )
    Viewer.AnimDisplayFrame( i )
    VCmd.SetStringValue( var4, r"ExportStates", r"CURRENT STATE" )
    VCmd.SetStringValue( var4, r"ExportAppliedOn", r"ON MODEL" )
    VCmd.SetStringValue( var4, r"ExportAsVectorScalar", r"SCALAR" )
    VCmd.SetStringValue(var4,r"ExportPath", lPath_auto+"\\pamrtm\\mainsimfiles\\Filling_factor"+str(i)+".txt")
    ret=VCmd.ExecuteCommand( var4, r"ExportContour" )

        
def getALLff(RTMfile,nS):
    #Assuming file is already open.
    
    #This function exports filling factors as text files for each analysis 
    #frame.
    
    strX = "D:\\IDPcode\\pamrtm\\mainSimFiles\\"+str(RTMfile)+"_RESULT.erfh5"   
    ii = int(0) 
    with open("D:\\IDPcode\\pamrtm\\mainSimFiles\\currentProgress.txt", "a") as text_file:
        text_file.write("tell me where is Gandalf "+str(nS)+"\n")
    while ii < int(nS):
        #__________________ VtkContourDlg BEGIN __________________
        var4=VCmd.Activate( 1, r"VToolKit.VToolKitInterface", r"VtkContourDlg" )
        VCmd.SetStringValue( var4, r"FileName", strX )
        VCmd.SetStringValue( var4, r"ContourMethod", r"ByEntity" )
        VCmd.SetStringValue( var4, r"ContourParentName", r"NODE" )
        VCmd.SetStringValue( var4, r"ContourDisplayName", r"FILLING_FACTOR" )
        VCmd.SetStringValue( var4, r"Encoding", r"Scalar" )
        VCmd.SetIntValue( var4, r"ContourGrayFlag", 1 )
        ret=VCmd.ExecuteCommand( var4, r"ApplyContour" )
        VCmd.SetStringValue( var4, r"SpectrumDispMode", r"Smeared" )
        Viewer.AnimDisplayFrame( ii )
        VCmd.SetStringValue( var4, r"ExportStates", r"CURRENT STATE" )
        VCmd.SetStringValue( var4, r"ExportAppliedOn", r"ON MODEL" )
        VCmd.SetStringValue( var4, r"ExportAsVectorScalar", r"SCALAR" )
        VCmd.SetStringValue( var4, r"ExportPath", r"D:\\IDPcode\\pamrtm\\mainSimFiles\\FILLING_FACTOR"+str(ii)+".txt" )
        ret=VCmd.ExecuteCommand( var4, r"ExportContour" )  
        ii = ii + 1
    

    
def getVisc(RTMfile):
    #creates a numpy file of all the states of viscosity during infusion (42 states, each node)
    
    #This function is currently not used within other scripts. It will require 
    #adjustments if included.
    with open("D:\\IDPcode\\pamrtm\\mainSimFiles\\currentProgress.txt", "a") as text_file:
        text_file.write("wegotsomewhere3\n")
    i= 0

    while i < 42:

        var4=VCmd.Activate( 1, r"VToolKit.VToolKitInterface", r"VtkContourDlg" )
        VCmd.SetStringValue( var4, r"FileName", r"D:\\IDPcode\\pamrtm\\mainSimFiles\\IDP_spar_A145_M001_B001_R002_RESULT.erfh5" )
        with open("D:\\IDPcode\\pamrtm\\mainSimFiles\\currentProgress.txt", "a") as text_file:
            text_file.write("wegotsomewhere88\n")
        VCmd.SetStringValue( var4, r"ContourMethod", r"ByEntity" )
        VCmd.SetStringValue( var4, r"ContourParentName", r"NODE" )
        VCmd.SetStringValue( var4, r"ContourDisplayName", r"VISCOSITY" )
        VCmd.SetStringValue( var4, r"Encoding", r"Scalar" )
        VCmd.SetIntValue( var4, r"ContourGrayFlag", 1 )
        ret=VCmd.ExecuteCommand( var4, r"ApplyContour" )
        VCmd.SetStringValue( var4, r"SpectrumDispMode", r"Smeared" )
        Viewer.AnimDisplayFrame( i )
        VCmd.SetStringValue( var4, r"ExportStates", r"CURRENT STATE" )
        VCmd.SetStringValue( var4, r"ExportAppliedOn", r"ON MODEL" )
        VCmd.SetStringValue( var4, r"ExportAsVectorScalar", r"SCALAR" )
        VCmd.SetStringValue( var4, r"ExportPath", r"D:\\IDPcode\\pamrtm\\mainSimFiles\\VISCOSITY.txt" )
        ret=VCmd.ExecuteCommand( var4, r"ExportContour" )
        with open("D:\\IDPcode\\pamrtm\\mainSimFiles\\currentProgress.txt", "a") as text_file:
            text_file.write("wegotsomewhere14\n")
     
        eef = open("D:\\IDPcode\\pamrtm\\mainSimFiles\\VISCOSITY.txt", "rt")
        ee = eef.read() 
        #doesnt work for non full infusion ... number 42 becomes number TOP, while top needs to be found
        numbers = ee.split("Number	42")[1]
        nc = numbers.count("\n")
        iii = 2
        nmat = np.zeros([1,2])
        nmat_temp = np.zeros([1,2])
        while iii < nc:
            n = numbers.split("\n")[iii]
            nmat_temp[0,0] = int(n.split()[0])
            nmat_temp[0,1] = float(n.split()[1])
            nmat = np.concatenate((nmat,nmat_temp),0)
            iii = iii + 1
        nmat = np.delete(nmat, (0), axis=0)
        print(nc)   
        print(nmat)
        eef.close()
        
        if i == 0:
            allmat = nmat
        else:
            allmat = np.concatenate((allmat,nmat),1)
        i = i + 1
    np.save(r"D:\\IDPcode\\pamrtm\\mainSimFiles\\"+RTMfile+"_VISCOSITY.npy", allmat)
    
#This section interprets the PP_request file.
#Runs the requested function from above and provides the necessary inputs.
fl = open(lPath_auto+"\\Temporary\\PP_request.txt", "rt")
flstr = fl.read() 
RTMfile = flstr.split("---")[0]
command = flstr.split("---")[1]
try:
    nS = flstr.split("---")[2]
except:
    print("no frames variable") 
getInit(RTMfile)
exec(command)
