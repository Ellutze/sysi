# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 10:58:13 2020

@author: jakub.kucera
"""

import os
import numpy as np
lPath = os.path.dirname(os.path.abspath(__file__))
#np import spheres
II = np.load(lPath+'\\catiafiles\\meshfiles\\none_A000_JK_N032_nodes.npy')
print(II)

import win32com.client.dynamic


import os
from IDP_databases import cnt_X, dc_X
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
#from IDP_cheats import togglePulse
from default_var_dict import getBase


#CATIA FOR TESTING
CATIA = win32com.client.Dispatch("CATIA.Application")
str61 = "D:\\IDPcode\\CatiaFiles\\Part1.CatPart"
partDocument1 = CATIA.Documents.Open(str61)
part1 = partDocument1.Part
hybridShapeFactory1 = part1.HybridShapeFactory
hybridBodies1 = part1.HybridBodies
hybridBody1 = hybridBodies1.Item("xxx")
i = 0
while i < np.size(II,0):
    ii = 0
    while ii < np.size(II,2):
        #CATIA FOR TESTING
        hybridShapePointCoord1 = hybridShapeFactory1.AddNewPointCoord(II[i,1,ii],II[i,2,ii],II[i,3,ii])
        hybridBody1.AppendHybridShape(hybridShapePointCoord1)
        ii = ii + 1
    i = i + 1

              
silo = "D:\\IDPcode\\CatiaFiles\\YYYYTesting.CatPart"
partDocument1.SaveAs(silo)