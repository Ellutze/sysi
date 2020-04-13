#visual-rtm related imports
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
#general imports
import numpy as np
import os
#required inputs

#automatically adjusted path
lPath_auto='D:\sysi'

lPath_auto='D:\sysi'
flstr = fl.read() 
MeshFile = flstr.split("---")[0]+"_JK"

#Meshsize is only for identificaion of average 3D position of the surface. 
#It doesn't affect the actual mesh used for simulation.
meshsize = 3
mesh_info = np.load(r"D:\\sysi\\temporary\\mesh_info.npy")

def initiate(MeshFile):

    #This function only opens the relevant .igs file
    #__________________ VhmCommand BEGIN __________________
    var1=VCmd.Activate( 1, r"VHostManagerPlugin.VhmInterface", r"VhmCommand" )
    #__________________ SessionCommand BEGIN __________________
    var2=VCmd.Activate( 1, r"VSessionManager.Command", r"SessionCommand" )
    #__________________ VEAction BEGIN __________________
    var3=VCmd.Activate( 1, r"VToolKit.VSectionCutInterface", r"VEAction" )
    ret=VE.ChangeContext( r"Visual-RTM" )
    VE.SetActiveWindow( r"p1w1" )
    ret=VE.ChangeContext( r"Visual-Mesh" )
    ret=VE.ChangeSkin( r"General" )
    #__________________ ModelingTolerance BEGIN __________________
    var4=VCmd.Activate( 0, r"VMeshModeler.VmmICommandGui", r"ModelingTolerance" )
    VCmd.SetIntValue( var4, r"ScaleModelToMMSystem", 0 )
    VCmd.SetIntValue( var4, r"KeepFailedCADEntities", 1 )
    VCmd.SetIntValue( var4, r"CheckUnitFlagAndNameToScaleModel", 0 )
    VCmd.SetIntValue( var4, r"KeepBlankCADEntities", 1 )
    VCmd.SetIntValue( var4, r"CleanSelfIntersectingSurfaces", 1 )
    VCmd.SetIntValue( var4, r"StitchSurfaces", 1 )
    VCmd.SetIntValue( var4, r"SurfaceStitchToleranceOption", 1 )
    VCmd.SetIntValue( var4, r"CreatePartsByColor", 0 )
    VCmd.SetIntValue( var4, r"ReadSubFigAsPartsOrAsm", 4 )
    VCmd.SetIntValue( var4, r"RemovePointsAndCurves", 0 )
    VCmd.SetIntValue( var4, r"CadAccuracyLevel", 0 )
    VCmd.SetIntValue( var4, r"MergeLoopCurves", 1 )
    VCmd.Accept( var4 )
    VCmd.Quit( var4 )
    #__________________ ModelingTolerance END __________________
    #__________________ ModelingTolerance BEGIN __________________
    var5=VCmd.Activate( 0, r"VMeshModeler.VmmICommandGui", r"ModelingTolerance" )
    VCmd.Quit( var5 )
    #__________________ ModelingTolerance END __________________
    ret=VExpMngr.LoadFile( "D:\\sysi\\catiafiles\\meshfiles\\"+MeshFile+".igs", 4 )
    VE.SetCurrentPage( 1 )
lPath_auto='D:\sysi'
lPath_auto='D:\sysi'
    return(var1)
    
def surfaceLocator(mesh_info):

    #This function generates matrix of surfaces with their approximate 3D position.
    #The 3D position is recorded in global coordinate systems, as per CATIA .iges.
    iy = 0
    surf_mat = np.zeros([1,4])
    temp_mat = np.zeros([1,4])
    #Allel is the number of expected surfaces based on CATIA mesh generation.
    allel = mesh_info[0]*mesh_info[1]
    while iy < (allel):
        #__________________ TopologyMesh BEGIN __________________
        var444=VCmd.Activate( 1, r"VMeshModeler.VmmICommandGui", r"TopologyMesh" )
        VCmd.SetObjectValue( var444, r"CurrentModel", "M  @0" )
        VCmd.SetDoubleValue( var444, r"ElementSize", 10  )
        ret=VCmd.ExecuteCommand( var444, r"SetElementSizeToAllEdges" )
        VCmd.SetObjectValue( var444, r"SplitEdge1", NULL )
        lst1_count,lst1 =  VScn.List( "  MFace  @0/@"+str(iy)+" "  )
        VCmd.SetObjectArrayValue( var444, r"CreateMesh", lst1_count, lst1 )
        VCmd.SetObjectValue( var444, r"SplitEdge1", NULL )
        VCmd.Cancel( var444 )
        #Generate .inp file for the single meshed surface.
        VistaDb.ModelSetExportKeyWordOrder( "M  @0", 0 )
        VistaDb.ModelSetExportStateAsNoInclude( "M  @0", 1 )
lPath_auto='D:\sysi'
        #Delete the mesh, preparing it for the next element export.
        #__________________ TopologyMesh BEGIN __________________
        var444=VCmd.Activate( 1, r"VMeshModeler.VmmICommandGui", r"TopologyMesh" )
        VCmd.SetObjectValue( var444, r"CurrentModel", "M  @0" )
        VCmd.SetObjectValue( var444, r"SplitEdge1", NULL )
        lst1_count,lst1 =  VScn.List( "  MFace  @0/@"+str(iy)+" "  )
        VCmd.SetObjectArrayValue( var444, r"DeleteMesh", lst1_count, lst1 )
        VCmd.SetObjectValue( var444, r"SplitEdge1", NULL )
        VCmd.Cancel( var444 )
  
        #Next section processes the exported input file.
        #The nodes exported are collected, and their coordinates averaged.
        filer = str(iy)+".inp"
lPath_auto='D:\sysi'
        ff = eex.read() 
        ff = ff.split("*NODE")[1]
        ff = ff.split("*")[0]
        coord_mat = np.zeros([1,4])
        temp_mat = np.zeros([1,4])
        iiy = 0
        #Turnign the input file into matrix.
        coms = ff.count(',')
        while iiy < coms:
            if iiy != 0:
                ex = ff.split(',')[iiy]
                ex = float(ex.split()[1])
            else:
                ex = ff.split(',')[iiy]
            #node number
            temp_mat[0,0] = float(ex)
            ex = ff.split(',')[iiy+1]
            #x value
            temp_mat[0,1] = float(ex)
            ex = ff.split(',')[iiy+2]
            #y value
            temp_mat[0,2] = float(ex)       
            if iiy != coms-3:
                ex = ff.split(',')[iiy+3]
                ex = float(ex.split()[0])
            else:
                ex = ff.split(',')[iiy+3]
                ex = float(ex)
            #z value
            temp_mat[0,3] = float(ex)
            coord_mat = np.concatenate((coord_mat, temp_mat), axis=0)

            #add to coord mat matrix
            iiy = iiy + 3
        #delete the first row of coord mat
        coord_mat = np.delete(coord_mat, (0), axis=0)
        #average the matrix, input to surf_mat
        #surface number:
        temp_mat[0,0] = iy
        #x value
        temp_mat[0,1] = np.average(coord_mat[:,1])
        #y value
        temp_mat[0,2] = np.average(coord_mat[:,2])
        #z value
        temp_mat[0,3] = np.average(coord_mat[:,3])
        surf_mat = np.concatenate((surf_mat, temp_mat), axis=0)
        iy = iy + 1
        eex.close()
    surf_mat = np.delete(surf_mat, (0), axis=0)
    #eex.close()
    
    #Just a marker of progress for log file.
lPath_auto='D:\sysi'
        text_file.write("chopchop\n")
    
    #Delete current model to prevent any remaining mesh settings to affect
    #mesh in subsequent simulation.
    VE.SetCurrentPage( 1 )
    ret=VE.ModelChange( "M  @0" )
    ret=VE.ModelDestroy( "M  @0" )
    VE.SetCurrentPage( 1 )
    VE.SetCurrentPage( 1 )
    VE.SetActiveWindow( r"p1w1" )
    VE.NewSession(  )

    #Safe the surface matrix.
lPath_auto='D:\sysi'
    
    #Delete the input files.
lPath_auto='D:\sysi'
    for f in filelist:
lPath_auto='D:\sysi'

var1 = initiate(MeshFile)   
surfaceLocator(mesh_info)