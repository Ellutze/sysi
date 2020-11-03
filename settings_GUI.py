# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 14:18:23 2019

@author: j.kucera
"""
#This GUI is selection of module options that can be turned on/off

from default_var_dict import getBase
import PySimpleGUI as sg    
import numpy as np
from IDP_agents import AgentSutler, AgentKurnik
from MySQL_utils import dropDownInfo
import os

#predifined looks of the GUI
sg.change_look_and_feel('SandyBeach')
path = os.getcwd()

#check the current settings to display checkboxes pre-checked where applicable
with open ("MASTER.py", "r") as myfile:
    data=myfile.readlines()
f = str(data)
if f.find("#key12345") != -1:
    bol1 = True
else:
    bol1 = False

#the visual of the menu
layout = [[sg.Checkbox("CAD",size=(11, 1), default=bol1,key="11")],[sg.Button('save settings')]]
window = sg.Window('settings', layout, default_element_size=(12,1))


while True:  # Event Loop
    event, values = window.read()
    #closing option always available
    if event == 'Exit':
        break
    
    #apply new settings and close window
    if event in 'save settings':
        #refresh the current settings 
        with open ("MASTER.py", "r") as myfile:
            data=myfile.readlines()
        f = str(data)
        if f.find("#key12345") != -1:
            bol1 = True
        else:
            bol1 = False
        
        print("selected:",values["11"],"original:",bol1)
        #compare current settings to desired once
        
        if values["11"] == True and bol1 == False:
            #if CATIA selected on and key suggests CATIA off turn CATIA on
            fl = open(os.path.join(path,"MASTER.py"),"rt")
            flstr = fl.read()            
            flstr = flstr.replace("CATbin = False #key789","CATbin = True #key12345")
            with open(os.path.join(path,"MASTER.py"),"w") as text_file:
                text_file.write(flstr)   
        elif values["11"] == False and bol1 == True:
            #if CATIA is selected off and is currently on
            fl = open(os.path.join(path,"MASTER.py"),"rt")
            flstr = fl.read()
            flstr = flstr.replace("CATbin = True #key12345","CATbin = False #key789")
            with open(os.path.join(path,"MASTER.py"),"w") as text_file:
                text_file.write(flstr)
                  
        break
window.close()
  
