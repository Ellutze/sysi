# -*- coding: utf-8 -*-
"""
Created on Tue May 12 11:16:17 2020

@author: jakub.kucera
"""
import numpy as np

def shuffle(matrix):
    sf =matrix[0,:]
    i = 1
    while i < np.size(matrix,0):
        ii = np.random.randint(i+1)
        sf = np.insert(sf, ii, matrix[i,:], 0)  
        i = i + 1
    return(sf)
    
#a = np.matrix([[1,2,3],[4,5,6],[7,8,9]])
#a= shuffle(a)
#print(a)
        