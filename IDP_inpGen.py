# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 10:06:39 2020
@author: jakub.kucera

Below is example input file, based on which the script is designed:
mainString = "*Part, name=x \n"
mainString += "*Node \n"
mainString +="      1,  -20.0850544,  -3.85008717,         395. \n"
mainString +="      2,  -20.0852795,   -3.8498385,         400. \n"
mainString +="      3,  -21.5107517,  0.623654664,         400. \n"
mainString +="      4,  -21.5106201,  0.623697937,         395. \n"
mainString +="*Element, type=S4R \n"
mainString +="1, 1, 2, 3, 4"
text_file = open("temporary\\sample.inp", "w")
n = text_file.write(mainString)
text_file.close()
"""

import win32com.client.dynamic
import sys, os 
import numpy as np
import win32gui
import numpy as np
from bokeh.io import output_file, show
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.models import Range1d


def inpGen(ML,MeshFile):
    #Takes in 3D matrix of nodes at various spans.
    #Rewrites the data into an input file, which contains nodes and 4-sided elements.
    
    #the size of the matrix
    rS = np.size(ML,0)
    dS = np.size(ML,2)

    #Initial lines of .inp file
    mainString = "*Part, name=x \n"
    mainString += "*Node \n"
    
    #Create list of nodes.
    n = int(0)
    i = 0
    while i < dS:
        ii =0
        while ii < rS:
            n = n + 1
            mainString+="     "+str(n)+",  "+str(ML[ii,1,i])+",   "+str(ML[ii,2,i])+",    "+str(ML[ii,3,i])+"  \n"
            ii = ii + 1
        i = i + 1
    #Create list of elements.
    mainString +="*Element, type=S4R \n"
    n = int(0)
    i = 0 
    while i < dS-1:
        ii = 0
        while ii < rS:
            n = n + 1
            jedna = i*rS + ii + 1
            #The last node of a cross section needs to be connected 
            #to first node of the cross section to close the loop.
            if ii != rS-1:
                dva = i*rS + ii + 2
            else:
                dva = jedna - rS + 1
            ctyri = jedna + rS
            tri = dva + rS
            mainString+= str(n)+", "+str(jedna)+", "+str(dva)+", "+str(tri)+",  "+str(ctyri)+" \n"
            ii = ii + 1
        i = i + 1
    
    #Input file in temporary folder is ammended based on the new input.
    #text_file = open("temporary\\sample.inp", "w")
    text_file = open("catiafiles\\meshfiles\\"+MeshFile+"_JK.inp", "w")
    n = text_file.write(mainString)
    text_file.close()
    
    
def catDispPts(MLm):
    #This function just displays all points from 3D matrix in CATIA
    #CATIA should already be running    
    CATIA = win32com.client.Dispatch("CATIA.Application")   
    documents1 = CATIA.Documents
    partDocument1 = documents1.Add("Part")
    part1 = partDocument1.Part    
    hybridBodies1 = part1.HybridBodies   
    hybridBody1 = hybridBodies1.Add()   
    hybridShapeFactory1 = part1.HybridShapeFactory  
    i = 0
    while i < np.size(MLm,2)-1:
        ii = 0
        while ii < np.size(MLm,0)-1:
            hybridShapePointCoord1 = hybridShapeFactory1.AddNewPointCoord(MLm[ii,1,i], MLm[ii,2,i], MLm[ii,3,i])
            hybridBody1.AppendHybridShape(hybridShapePointCoord1)
            ii = ii + 1
        i = i + 1
    part1.InWorkObject = hybridShapePointCoord1
    part1.Update 
    
def plotXSP(MLm,xAnchor,yAnchor,varVal):

    airf = varVal["airfoil_0"]
    airfoil=np.loadtxt("aerofoilcollection\\"+airf,skiprows=1)
    airfoil[:,0]=airfoil[:,0]-xAnchor
    airfoil = airfoil*varVal["chord_0"]
    #Select output format.
    output_file("layout.html")
    
    #Create first plot
    
    #s1.triangle(X3[:,3], x, size=10, color="firebrick", alpha=0.5,legend="predictions")
    
    #Create second plot
    s2 = figure(title="Spar section mesh",plot_width=1800, plot_height=400)
    i = 0
    while i < np.size(MLm,2):
        s2.circle(MLm[:,1,i], MLm[:,2,i], size=5, color="firebrick", alpha=0.5,legend="datum")
        i = i + 1
    
    #s2.circle(ML[:,1,1], ML[:,2,1], size=10, color="firebrick", alpha=0.5,legend="1")
    #s2.circle( ML[:,1,0], ML[:,2,0], size=10, color="navy", alpha=0.5,legend="0")
    #s2.circle(ML[:,1,2], ML[:,2,2], color="green", alpha =0.5,legend="2")
    #s2.circle(ML[:,1,3], ML[:,2,3], color="black", alpha =0.5,legend="3")
    
    s2.triangle(airfoil[:,0],airfoil[:,1],color="blue",alpha = 0.5,legend="airfoil")
    s2.triangle(xAnchor,yAnchor,color="green",alpha = 0.5,legend="spar")
    s2.xaxis.axis_label = 'x'
    s2.yaxis.axis_label = 'y'
    s2.legend.location = "top_right"
    
    # put the results in a row
    #show(row(s1, s2))
    show(row(s2))
    

