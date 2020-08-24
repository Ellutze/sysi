# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 11:09:02 2019

@author: kuceraj
"""

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
#__________________ VhmCommand BEGIN __________________
var1=VCmd.Activate( 1, r"VHostManagerPlugin.VhmInterface", r"VhmCommand" )
import VHostManager
import VE

#automatically adjusted path
lPath_auto=r'D:\sysi'

with open(lPath_auto+"\\pamrtm\\mainsimfiles\\currentProgress.txt","a") as text_file:
    text_file.write("The initial simulation starts here:")

#input file - instead function arguments - which are not possible due to the command line passing
fl = open(lPath_auto+"\\temporary\\RTM_in.txt","rt")
flstr = fl.read() 
RTMfile = flstr.split("---")[1]

#__________________ SessionCommand BEGIN __________________
var2=VCmd.Activate( 1, r"VSessionManager.Command", r"SessionCommand" )
#__________________ VEAction BEGIN __________________
var3=VCmd.Activate( 1, r"VToolKit.VSectionCutInterface", r"VEAction" )
ret=VE.ChangeContext( r"Visual-RTM" )
VE.SetActiveWindow( r"p1w1" )
ret = VExpMngr.LoadFile(lPath_auto+"\\pamrtm\\mainsimfiles\\"+RTMfile+".vdb",0)
VE.SetCurrentPage( 1 )
ret=VE.ModelChange( "M  @0" )

var4=VCmd.Activate( 1, r"VRTMUtilities.VRTMInterface", r"SolverManager" )
ret=VCmd.ExecuteCommand( var4, r"RUN" )
ret=VCmd.ExecuteCommand( var4, r"OpenLogFile" )
VScn.ExecutePythonInterpeter( r"C:\Program Files\ESI Group\Visual-Environment\15.0\COMMON\Resources\VisualProcessExec\user_scripts\CompositeLoadResult.py" )
    
