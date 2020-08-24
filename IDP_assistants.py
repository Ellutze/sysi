#from mysql.connector import MySQLConnection, Error
from IDP_databases import cnt_X,dc_X
#from python_mysql_dbconfig import read_db_config
import numpy as np
import random
from MASTER import SingleLoop
#from IDP_cheats import togglePulse
import os


def is_empty(any_structure):
    #this functions checks if a list (or suchlike) is empty, used below in abaMain
    if any_structure:
        return False
    else:
        return True
    
def Steph(population,specie,generation,BCs,optiTable,varVar,varVal):
    #creates a random first generation     
    cnnT,crrT = cnt_X('NCC')
    specimen = np.zeros([population,5])
    i = 0
    while i < population:
        #create new population -- number  of individuals, fully random each variable in range
        specimen[i,0] = (random.uniform(0,1))*(BCs[0,1]-BCs[0,0])+(BCs[0,0])
        specimen[i,1] = (random.uniform(0,1))*(BCs[1,1]-BCs[1,0])+(BCs[1,0])
        specimen[i,2] = (random.uniform(0,1))*(BCs[2,1]-BCs[2,0])+(BCs[2,0])
        specimen[i,3] = (random.uniform(0,1))*(BCs[3,1]-BCs[3,0])+(BCs[3,0])
        specimen[i,4] = (random.uniform(0,1))*(BCs[4,1]-BCs[4,0])+(BCs[4,0])
        specimen[i,3] = int(specimen[i,3])
        # export the new generation into SQL table
        query = "INSERT INTO "+optiTable+"(specie,generation,cs1,cs2,cs3, no_layers, mandrel_speed) VALUES("
        query += """'"""+specie+"""','"""+str(generation)+"""','"""+str(specimen[i,0])+"""','"""+str(specimen[i,1])+"""','"""+str(specimen[i,2])+"""','"""+str(specimen[i,3])+"""','"""+str(specimen[i,4])+"""')"""
        crrT.execute(query)
        cnnT.commit()
        i= i + 1  
    #close SQL handles 
    dc_X('NCC',cnnT,crrT)
    return(BCs)
          
def Linda(generation,specie,GENtable,varVal,varVar):
    lPath = os.path.dirname(os.path.abspath(__file__))
    #Linda2 is for GUI
    cnnT,crrT = cnt_X('NCC')
    #print(GENtable)
    query = """SELECT * FROM """+GENtable+""" where fitness is null and specie = '"""+str(specie)+"""' and generation = '"""+str(generation)+"""';"""
    #print(query)
    crrT.execute(query)
    rows = crrT.fetchall()
    #close SQL handles 
    dc_X('NCC',cnnT,crrT)
    for row in rows:
        recordID = row[0]
        #Sets fitness to 0, so that the same failed simulation isnt attempted twice
        cnnT,crrT = cnt_X('NCC')
        #mandrel speed might be adjusted during simulation - hence the re-import
        query = """UPDATE """+GENtable+""" SET  fitness = """+str(0)+""" Where (id = """+str(recordID)+""");"""
        crrT.execute(query)
        cnnT.commit()
        #adjust variables dictionary by iterated variables
        i = 0
        while i < len(varVar):
            varVal[varVar[i]] = row[i+3]
            i = i + 1
        #close SQL handles 
        dc_X('NCC',cnnT,crrT)
    
        #evaluate the simulations -- use fitness function to establish value of each individual
        with open(lPath+"\\temporary\\underground.txt", "a") as text_file:
            text_file.write("Initiating complete analysis.\n")
        fitness,arunID = SingleLoop(varVal)
        print("Hurrah! New individual was born into the populaiton!")
        #stores the result, reference simulaiton number, and mandrel_speed in case change was required due to minimal angle limit        
        cnnT,crrT = cnt_X('NCC')
        #mandrel speed might be adjusted during simulation - hence the re-import
        query = """UPDATE """+GENtable+""" SET  fitness = """+str(fitness)+""", arunID = """+str(arunID)+""" Where (id = """+str(recordID)+""");"""
        crrT.execute(query)
        cnnT.commit()
        #close SQL handles 
        dc_X('NCC',cnnT,crrT)
    
def Toby(generation,specie,GENtable):
    cnnT,crrT = cnt_X('NCC')
    # obtain data from the last generation   
    query = """SELECT * FROM """+GENtable+""" where specie = '"""+specie+"""';"""
    crrT.execute(query)
    
    rows = crrT.fetchall()
    varN = np.size(rows,1)-4
    pop = np.zeros([1,varN])
    popi = np.zeros([1,varN])
    dc_X('NCC',cnnT,crrT)
    for row in rows:
        i = 0
        while i < varN:
            popi[0,i] = (row[int(i+3)])
            i = i + 1
        pop = np.concatenate((pop, popi), axis=0)
    pop = np.delete(pop, (0), axis=0)
    return(pop)

    
def Fifi(TOP,mat1,pheroNo):
    #fishes top results from the matrix and outputs corresponding new matrix 
    switch = np.zeros([1,np.size(mat1,1)])
    TOPmat = np.zeros([TOP,np.size(mat1,1)])
    i = 0
    while i < mat1.shape[0]:
        tempVALs = mat1[i,:]
        ii = 0
        while ii < TOP:

            if TOPmat[ii,pheroNo-1] < tempVALs[pheroNo-1]:
                #swich the temporary for the one replaced in top values
                switch = np.copy(TOPmat[ii,:])               
                TOPmat[ii,:] = tempVALs
                tempVALs = switch
            ii = ii + 1
        i = i + 1
    #the exported matrix is also ordered from best to worst
    return(TOPmat)
                
        
        
        
        
        
        
        
        
        
        
        
        