# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 14:18:23 2019

@author: j.kucera
"""
#This GUI is supposed to give user selection of variables for optimisation.

from default_var_dict import getBase
import PySimpleGUI as sg    
import numpy as np
from IDP_agents import AgentSutler, AgentKurnik, AgentPytlik
from MySQL_utils import dropDownInfo
from pathing import adj

#adjusts paths, only relevant when moving files to new folder
adj()

specie = "test"

#get default values for variables along with their limits
varVal, varMin,varMax = getBase()

#predifined looks of the GUI
sg.change_look_and_feel('SandyBeach')
  
#The tab definition for selection of optimisation goals.
tab3_layout = [[sg.Checkbox('Weight, importance:',size=(20, 1), default=False),sg.In(key='W_fit',size=(5, 1))],
               [sg.Checkbox('Load bearing, importance:',size=(20, 1), default=False),sg.In(key='L_fit',size=(5, 1))],
               [sg.Checkbox('Infusion time, importance:',size=(20, 1), default=False),sg.In(key='I_fit',size=(5, 1))],
                ]    
#All variables currently available.
fixedVars = ['span','twist_0','chord_0','no_layers','twist_1','chord_1','matrix','twist_2','chord_2','reinforcement','twist_3','chord_3',
             'mesh_size','airfoil_0','sweep_0','spools','airfoil_1','sweep_1','RAD', 'airfoil_2','sweep_2','mandrel_speed','airfoil_3','sweep_3',
             'dihedral_0','dihedral_1','dihedral_2','dihedral_3','c_min','c_max','guide_rad','IMD','inlet_temp','tool_temp',
             'inlet_pressure','vent_pressure','flow_rate']

#Automatically generate the tab-layout for iterated variables selection.        
tb1l = "tab1_layout =[["
ii = 0
for i in fixedVars:
    tb1l +="""sg.Checkbox('"""+str(i)+"""',size=(11, 1), default=False,key='vv_"""+str(ii)+"""')"""
    if (ii+1)%3==0:
        tb1l += "],["
    else:
        tb1l += ","
    ii = ii + 1
tb1l = tb1l[:-1]
if (ii+1)%3==0:
    tb1l += "]"
else:
    tb1l += "]]"      
exec(tb1l)              

#Automatically generate the tab-layout for fixed variables selection.
tb2l = "tab2_layout = [["
ii = 0
for i in fixedVars:
    tb2l +="""sg.T('"""+str(i)+"""',size=(10, 1)),sg.In(key='fv_"""+str(ii)+"""',size=(5, 1))"""
    if (ii+1)%3==0:
        tb2l += "],["
    else:
        tb2l += ","
    ii = ii + 1
tb2l = tb2l[:-1]
if (ii+1)%3==0:
    tb2l += "]"
else:
    tb2l += "]]"                               
exec(tb2l)


seznam = dropDownInfo()
algos = ["ACO","GA"]

#The tab layout for the execution of selected optimisation.
tab4_layout = [[sg.T('Specie: ',size=(8, 1)),sg.In(key='specie',size=(26, 1))],
                  [sg.Multiline( size=(35, 5),key='-INPUT0-')],
                  [sg.T('Continue run:',size=(12,1))],
                  [sg.Combo(seznam,size=(35,1),key='klic')],
                  [sg.Button('RUN'),sg.Button('continue RUN')],
                  [sg.T('Continuation algorithm:',size=(12,1))],
                  [sg.Combo(algos,size=(35,1),key='klic2')],
                  [sg.Button('Run continuous optimisation')]
                 ]

#The overall layout of the GUI
layout = [[sg.Text('Variable Selection')],[sg.TabGroup([[sg.Tab('Altered Variables', tab1_layout),
           sg.Tab('Fixed Variables', tab2_layout),sg.Tab('Fitness Function', tab3_layout),sg.Tab('MAIN', tab4_layout)]])]]    
window = sg.Window('My window with tabs', layout, default_element_size=(12,1))    

#GUI function loop
while True: 
    #read all potential user inputs
    event, values = window.read()    
    
    if event is None: # always, always give a way out!    
        break  
    if event in 'continue RUN':
        iters = str(values['klic'])
        rr = str(values['klic']).split(",")[0]
        if rr == "":
            print("Please select a run to continue")
        else:
            print("continuing run "+rr)
            AgentKurnik(iters,specie,varVal)
            #.............................
    #After selecting all the option user has one button to trigger the simulation.
    if event in 'RUN':
        #print(  str(values['fv_0']))
        
        #somehow in this window I would like to have printouts from how the sim is doing...
        window['-INPUT0-'].Update('This is where the info goes...')
        
        #initiate list of iterated variables
        varVar = []
        i = 0
        while i < len(fixedVars):
            if values['fv_'+str(i)] is not '':
                
                if varMin[fixedVars[i]] < float(values['fv_'+str(i)])  < varMax[fixedVars[i]]:
                
                    buildVar = """varVal['"""+fixedVars[i]+"""'] = str(values['fv_"""+str(i)+"""'])"""
                    #print(buildVar)
                    exec(buildVar)
                
                else:
                    "The selected value for "+fixedVars[i]+" is out of allowable limits, default value was used."
            
            if values['vv_'+str(i)] == True:
                varVar.append(fixedVars[i])
            
            #print(varVal)
            #print(varVar)
            i = i + 1
        if varVal['c_min'] > varVal['c_max'] or (varVal['c_min']=='' and varVal['c_max'] != '') or (varVal['c_min']!='' and varVal['c_max'] == ''):
            print('The spar limits are incorrectly defined. Either the upper limit is smaller than lower limit, or only one limit has been assigned')
        #elif ('c_min' in varVar and 'c_max' not in varVar) :
        else:
            AgentSutler(varVar,varVal,fixedVars,varMin,varMax,specie)
        #check specie 
        
        #if exists run ferda
        
        #if doesnt exist run Unity
        
        #Option for a solo run? if all in tab 1 are 0 
    
    if event in "Run continuous optimisation":
        alg = str(values['klic2'])
        tbl = str(values['klic'])
        if tbl == "":
            print("please select sample table to continue on")
        else:
                        #initiate list of iterated variables
            varVar = []
            i = 0
            while i < len(fixedVars):
                if values['fv_'+str(i)] is not '':
                    
                    if varMin[fixedVars[i]] < float(values['fv_'+str(i)])  < varMax[fixedVars[i]]:
                    
                        buildVar = """varVal['"""+fixedVars[i]+"""'] = str(values['fv_"""+str(i)+"""'])"""
                        #print(buildVar)
                        exec(buildVar)
                    
                    else:
                        "The selected value for "+fixedVars[i]+" is out of allowable limits, default value was used."
                
                if values['vv_'+str(i)] == True:
                    varVar.append(fixedVars[i])
                
                #print(varVal)
                #print(varVar)
                i = i + 1
            
            
            if alg == "ACO":
                
                AgentPytlik(tbl,varVal,varMin,varMax)
            