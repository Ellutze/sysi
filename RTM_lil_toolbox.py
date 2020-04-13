#Visual-RTM related imports
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
#other imports
import numpy as np

#automatically adjusted path
lPath_auto='D:\sysi'

with open(lPath_auto+"\\pamrtm\\mainSimFiles\\currentProgress.txt", "a") as text_file:
    text_file.write("toolbox initiated\n")

#input file - instead function arguments - which are not possible due to the command line passing
fl = open(lPath_auto+"\\Temporary\\RTM_in.txt", "rt")
flstr = fl.read() 
RTMfile = flstr.split("---")[1]
MeshFile = flstr.split("---")[0]+"_JK"
resin = flstr.split("---")[2]
I_T = float(flstr.split("---")[3])
T_T = float(flstr.split("---")[4])
I_P = float(flstr.split("---")[5])
V_P = float(flstr.split("---")[6])
FR = float(flstr.split("---")[7])
INITIAL = int(flstr.split("---")[10])
RTMF = flstr.split("---")[11]
filename = MeshFile+".igs"

with open(lPath_auto+"\\pamrtm\\mainSimFiles\\currentProgress.txt", "a") as text_file:
    text_file.write("______ReRun-flow_adjustment_____"+RTMfile+"_________\n")

def initiate(RTMF,lPath_auto):
    #Open the initial file saved before flow rate assignment.
    var1=VCmd.Activate( 1, r"VHostManagerPlugin.VhmInterface", r"VhmCommand" )
    var2=VCmd.Activate( 1, r"VSessionManager.Command", r"SessionCommand" )
    var3=VCmd.Activate( 1, r"VToolKit.VSectionCutInterface", r"VEAction" )
    ret=VE.ChangeContext( r"Visual-RTM" )
    VE.SetActiveWindow( r"p1w1" )
    ret=VExpMngr.LoadFile( lPath_auto+"\\pamrtm\\mainSimFiles\\"+RTMF+"_flowUnassigned.vdb", 0 )
    VE.SetCurrentPage( 1 )
    ret=VE.ModelChange( "M  @0" )
    return(var1)
      
def flowRate(RTMfile,FR,I_T,I_P,lPath_auto):    
    #Assigns flow rate based on input parameters. The flow-rate for each section
    #at any point in time is defined by a matrix.
    i = 0
    flowM  = np.load(lPath_auto+"\\temporary\\flowMAT.npy")
    
    
    np.savetxt(lPath_auto+"\\pamrtm\\mainSimFiles\\FM_"+RTMfile+".csv", flowM, delimiter=",")
    while i < 12:
        #Define flow rate 
        strt = r"Flow Rate_"+str(i)
        valt = I_T
        valp = I_P
        hmpf = i + 1
        strt2 = " "+str(hmpf)+r"=>USER_ForFlow"+str(i)+"  "        
        var41=VCmd.Activate( 1, r"VRTMUtilities.VRTMInterface", r"BoundaryConditions" )
        VCmd.SetStringValue( var41, r"ActiveBcType", r"Volume Flow Rate" )
        VCmd.SetGuStringValue( var41, r"OpeningMode", r"CreateSpecificType" )
        ret=VCmd.ExecuteCommand( var41, r"CreateNew" )
        VCmd.SetStringValue( var41, r"BcName", strt )
        VCmd.SetStringValue( var41, r"ActiveBcParam", r"flowRate" )
        VCmd.SetStringValue( var41, r"ParamValue", r"F(t)" )
        ret=VCmd.ExecuteCommand( var41, r"UpdateCurve" )
        VCmd.SetStringValue( var41, r"ActiveProperty", r"flowRate" )
        VCmd.SetStringValue( var41, r"PropertyValueUnit", r"m^3/sec" )
        VCmd.SetStringValue( var41, r"PropertyFuncUnit", r"sec" )
        ret=VCmd.ExecuteCommand( var41, r"UpdateParamForUnit" )
        ii = 0
        nSTR = ""
        while ii < np.size(flowM,0):
            nSTR = nSTR+" "+str(ii)+"  "+str(flowM[ii,i])+" | "
            ii = ii + 1
        lst1_count,lst1 =  VScn.Point2List( nSTR  )
        #Other parameters
        VCmd.SetPoint2ArrayValue( var41, r"PropertyTValue", lst1_count, lst1 )
        VCmd.SetStringValue( var41, r"ActiveBcParam", r"temperatureValue" )
        VCmd.SetDoubleValue( var41, r"ParamDoubleValue", valt  )
        VCmd.SetStringValue( var41, r"ActiveBcParam", r"maxPressure" )
        VCmd.SetDoubleValue( var41, r"ParamDoubleValue", valp  )
        lst1_count,lst1 =  VScn.StringList( strt2  )
        VCmd.SetStringArrayValue( var1, r"ListSelection", lst1_count, lst1 )
        ret=VCmd.ExecuteCommand( var41, r"UpdateSelectionMaster" )
        VCmd.Accept( var41 )
        VCmd.Quit( var41 )           
        i = i + 1

    with open(lPath_auto+"\\pamrtm\\mainSimFiles\\currentProgress.txt", "a") as text_file:
        text_file.write("flow rate assigned\n")
    
def vent(V_P,lPath_auto):
    #Defining the vent boundary condition.
    var4=VCmd.Activate( 1, r"VRTMUtilities.VRTMInterface", r"BoundaryConditions" )
    VCmd.SetStringValue( var4, r"ActiveBcType", r"Vent" )
    VCmd.SetGuStringValue( var4, r"OpeningMode", r"CreateSpecificType" )
    ret=VCmd.ExecuteCommand( var4, r"CreateNew" )
    VCmd.SetStringValue( var4, r"BcName", r"Vent_1" )
    VCmd.SetStringValue( var4, r"ActiveBcParam", r"ventPressure" )
    VCmd.SetDoubleValue( var4, r"ParamDoubleValue", V_P  )
    ret=VCmd.ExecuteCommand( var4, r"PickEntities" )
    lst1_count,lst1 =  VScn.StringList( r" 2=>USER_ForVent  "  )
    VCmd.SetStringArrayValue( var1, r"ListSelection", lst1_count, lst1 )
    ret=VCmd.ExecuteCommand( var4, r"UpdateSelectionMaster" )
    VCmd.Accept( var4 )
    VCmd.Quit( var4 )
    
    with open(lPath_auto+"\\pamrtm\\mainSimFiles\\currentProgress.txt", "a") as text_file:
        text_file.write("vent specified")
        
def tool(T_T):
    #Applying tool temperture on all nodes.
    var27=VCmd.Activate( 1, r"VRTMUtilities.VRTMInterface", r"BoundaryConditions" )
    VCmd.SetStringValue( var27, r"ActiveBcType", r"Temperature" )
    VCmd.SetGuStringValue( var27, r"OpeningMode", r"CreateSpecificType" )
    ret=VCmd.ExecuteCommand( var27, r"CreateNew" )
    VCmd.SetStringValue( var27, r"BcName", r"Temperature_1" )
    lst1_count,lst1 =  VScn.StringList( r" 3=>USER_AllNodes  "  )
    VCmd.SetStringArrayValue( var1, r"ListSelection", lst1_count, lst1 )
    ret=VCmd.ExecuteCommand( var27, r"UpdateSelectionMaster" )
    VCmd.SetStringValue( var27, r"ActiveBcParam", r"temperatureValue" )
    VCmd.SetDoubleValue( var27, r"ParamDoubleValue", T_T  )
    VCmd.Accept( var27 )
    VCmd.Quit( var27 )
    
def saving(RTMfile,INITIAL,lPath_auto): 
    if INITIAL == 0:
        VExpMngr.ExportFile( lPath_auto+"\\pamrtm\\mainSimFiles\\"+RTMfile+".vdb", 0 )
        with open(lPath_auto+"\\pamrtm\\mainSimFiles\\currentProgress.txt", "a") as text_file:
            text_file.write("model saved, simulation ready\n")
    #So that flow mesh version does not overwrite the original.
    else:
        VExpMngr.ExportFile( lPath_auto+"\\pamrtm\\mainSimFiles\\"+RTMfile+"_adjusted.vdb", 0 )
        with open(lPath_auto+"\\pamrtm\\mainSimFiles\\currentProgress.txt", "a") as text_file:
            text_file.write("adjusted model saved, simulation ready\n")        
    
def run():
    var4=VCmd.Activate( 1, r"VRTMUtilities.VRTMInterface", r"SolverManager" )
    ret=VCmd.ExecuteCommand( var4, r"RUN" )
    ret=VCmd.ExecuteCommand( var4, r"OpenLogFile" )
    VScn.ExecutePythonInterpeter( r"C:\Program Files\ESI Group\Visual-Environment\15.0\COMMON\Resources\VisualProcessExec\user_scripts\CompositeLoadResult.py" )
    
var1 = initiate(RTMF,lPath_auto)
flowRate(RTMfile,FR,I_T,I_P,lPath_auto)
vent(V_P,lPath_auto)
tool(T_T)
#simPar()
saving(RTMfile,INITIAL,lPath_auto)
run()


