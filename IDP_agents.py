from MASTER import SingleLoop
from mysql.connector import MySQLConnection
from IDP_databases import cnt_X, dc_X
from IDP_cheats import togglePulse
from python_mysql_dbconfig import read_db_config
import numpy as np
import random
import IDP_assistants
#import LHS
import lhsmdu
import itertools
import os

def is_empty(any_structure):
    #this functions checks if a list (or suchlike) is empty, used below in abaMain
    if any_structure:
        return False
    else:
        return True
    
#def AgentSmith():
    #define variable to iterate through - once error encountered go the otherr way, this should give me boundaries 
    #this creates a line through multi-dimensional design space, with enough lines, the surface can be estimated
    
def AgentKurnik(iters,specie,varVal):
    generation = 420 #for now
    GENtable = iters.split(",")[0]
    x = iters.count(',')
    i = 1
    varVar = []
    while i < x: 
        varVar.append(iters.split(",")[i])
        i = i + 1
    GENtable = GENtable.replace("""'""","")
    IDP_assistants.Linda(generation,specie,GENtable,varVal,varVar)
    print("All caught up, no more uncalculated members. Select follow up algorithm.")
    
def AgentSutler(varVar,varVal,fixedVars,varMin,varMax,specie):
    #this function is used by the GUI
    #Based on user input new iteration table in SQL is created
    
    lPath = os.path.dirname(os.path.abspath(__file__))
    #creates a string of iteratable variables list for SQL record
    i = 0
    varVarS = ""
    while i < len(varVar):
        varVarS = varVarS+varVar[i]+"_"
        i = i + 1
    
    
    cnnW,crrW = cnt_X('NCC')
    
    query  = """SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG='DIGIProps' and TABLE_NAME like '%_iters_%'"""
    crrW.execute(query)
    rows = crrW.fetchall()
    cc = 0
    for row in rows:
        x = int(row[0].split('_iters_')[1])
        
        if x > cc:
            cc = x
    cc = cc + 1

    GENtable = '_iters_'+str(cc)
    
    #Build User defined iteratable variable table
    query ="CREATE TABLE "
    query += GENtable
    query +="(id int IDENTITY(1,1) PRIMARY KEY,Specie varchar(100),Generation int,"
    i = 0
    while i < len(varVar):
        query+=str(varVar[i])+" "
        if type(varVal[varVar[i]]) is str:
            query +="varchar(100),"
        else:
            query +="float,"
        i = i + 1
    query += "fitness float,arunID int)"
    crrW.execute(query)
    cnnW.commit()
    
    
    #insert fixed variables into iteration table
    query = "INSERT INTO UserDefIterations(IterateVar,"
    i = 0
    while i < len(fixedVars):
        query +=fixedVars[i]+","
        i = i + 1
    query = query[:-1]
    query += ") VALUES("+"""'"""+varVarS+"""',"""

    i = 0 
    while i < len(fixedVars):
        if type(varVal[fixedVars[i]]) is str:
            query +="""'"""+str(varVal[fixedVars[i]])+"""',"""
        else:
            query +=str(varVal[fixedVars[i]])+","
        i = i + 1
    query = query[:-1]
    query +=")"
    crrW.execute(query)  
    cnnW.commit() 

    
    generation = 420 #untill combination of opt_algos is required
    #obtain data based on Latin Hypercube sampling method
    

    s = 100
    varN = len(varVar)
    sampleM = lhsmdu.sample(varN, s)
    sampleMAT = np.ndarray.transpose(sampleM)    

    print(varMin,varMax)
    BCs = np.matrix([[0.000,0.000]])
    temp = np.matrix([[0.000,0.000]])
    i = 0 
    #AFLe = 0
    while i < varN:
        if varMin[varVar[i]]!=False:
            temp[0,0] = varMin[varVar[i]]
            temp[0,1] = varMax[varVar[i]]
            BCs = np.concatenate((BCs,temp),axis = 0)
        elif "airfoil" in varVar[i]:
            img_folder_path = lPath+'\\aerofoilcollection\\'
            dirListing = os.listdir(img_folder_path)
            AFLS = len(dirListing)
            temp[0,0] = 0
            temp[0,1] = AFLS
            BCs = np.concatenate((BCs,temp),axis = 0)
            #AFLe = 1
        else:
            #0-10 now arbitrarily selected for string values (eg. material)
            #this needs to be replaced by a lookup function that checks the 
            #number of airfoils
            temp[0,0] = 0
            temp[0,1] = 10
            BCs = np.concatenate((BCs,temp),axis = 0)
            
        i = i + 1
    BCs =np.delete(BCs,0,axis=0)
    print(BCs)
    
    #Integer values turned into integers (LHS likely provided no integer values.)
    IntPos = 979
    IntPos2 = 979
    IntPos3 = 979
    IntPos4 = 979
    if 'no_layers' in varVar :
        IntPos = varVar.index('no_layers')
    if 'spools' in varVar:
        IntPos2 = varVar.index('spools')
    if 'c_max' in varVar:
        IntPos3 = varVar.index('c_max')
    if 'c_min' in varVar:
        IntPos4 = varVar.index('c_min')
    
    #transofrm the ratio values to actual variables and populate new entries to SQL
    i = 0
    while i < s:
        ii = 0
        while ii < varN:
            sampleMAT[i,ii]= (sampleMAT[i,ii])*(BCs[ii,1]-BCs[ii,0])+BCs[ii,0] 
            if IntPos == ii or IntPos2 == ii:
                sampleMAT[i,ii] = int(sampleMAT[i,ii])
            # if c_max and c_min are iterated
            if ii == max(IntPos3,IntPos4):
                #and if c_min is larger than c_max
                if sampleMAT[i,IntPos3] < sampleMAT[i,IntPos4]:
                    #switch values of c_max and c_min
                    c_max = np.copy(sampleMAT[i,IntPos4])
                    c_min = np.copy(sampleMAT[i,IntPos3])
                    sampleMAT[i,IntPos4] = c_min
                    sampleMAT[i,IntPos3] = c_max
            ii = ii + 1
        i = i + 1
        
        
    i = 0 
    while i < s:
        #sampleMAT[i,3] = int(sampleMAT[i,3])
        query = "INSERT INTO "+GENtable+"(specie,generation,"
        ii = 0
        while ii < varN:
            query += varVar[ii]+","
            ii = ii + 1
        query = query[:-1]
        query += ") VALUES("
                                          
        query += """'"""+specie+"""',"""+str(generation)+""","""
        ii = 0
        while ii < varN:
            if "airfoil" in varVar[ii]:
                # Will raise StopIteration if you don't have x files
                fileNO = int(sampleMAT[i,ii])
                file1000 = next(itertools.islice(os.scandir(lPath+'\\aerofoilcollection\\'), fileNO, None)).path
                file1000 = file1000.split(lPath+"\\aerofoilcollection\\")[1]
                query += """'"""+str(file1000)+"""',"""
            else:
                query += str(sampleMAT[i,ii])+","
            ii = ii + 1
        query = query[:-1]
        query += ");"
        crrW.execute(query)
        cnnW.commit()
        i = i + 1
    dc_X('NCC',cnnW,crrW)
    
    with open(lPath+"\\temporary\\underground.txt", "a") as text_file:
        text_file.write("LHS run, begin evaluation.\n")
    IDP_assistants.Linda(generation,specie,GENtable,varVal,varVar)
    print("Finished sampling the Hypercube")
    #check for uncalculated SQL entries and calculate them
    #(force integer somewhere)   

   
def AgentPytlik(iters,varVal,varMin,varMax):
    

    GENtable = iters.split(",")[0]
    GENtable = GENtable.replace("""'""","")
    x = iters.count(',')
    i = 1
    varVar = []
    while i <= x: 
        varVar.append(iters.split(",")[i])
        i = i + 1
    
    
    
    lPath = os.path.dirname(os.path.abspath(__file__))
    #Ant colony optimisatoin, or gradient based adjustment optimisation
    #initial number of randoms
    #LHS or other initial sampling method should be run prior to this
    #population = 2  #start with 2 for testing, but likely 10+ is good initial number
    specie = "test"
    generation = 420 #untill combination of opt_algos is required
    
    # rows : variables : cs1,cs2,cs3,MS,NL
    # columns: min, max
    BCs = np.matrix([[0.000,0.000]])
    temp = np.matrix([[0.000,0.000]])
    i = 0 
    #AFLe = 0
    varN = len(varVar)
    print("varN",varN)
    while i < varN:
        if varMin[varVar[i]]!=False:
            temp[0,0] = varMin[varVar[i]]
            temp[0,1] = varMax[varVar[i]]
            BCs = np.concatenate((BCs,temp),axis = 0)
        elif "airfoil" in varVar[i]:
            img_folder_path = lPath+'\\aerofoilcollection\\'
            dirListing = os.listdir(img_folder_path)
            AFLS = len(dirListing)
            temp[0,0] = 0
            temp[0,1] = AFLS
            BCs = np.concatenate((BCs,temp),axis = 0)
            #AFLe = 1
        else:
            #0-10 now arbitrarily selected for string values (eg. material)
            #this needs to be replaced by a lookup function that checks the 
            #number of airfoils
            temp[0,0] = 0
            temp[0,1] = 10
            BCs = np.concatenate((BCs,temp),axis = 0)
            
        i = i + 1
    BCs =np.delete(BCs,0,axis=0)
    
    #check if specie exists
    cnnW,crrW = cnt_X('NCC')
    query = """SELECT * FROM """+str(GENtable)+""" where specie like '"""+specie+"""';"""
    print(query)
    crrW.execute(query)
    rows = crrW.fetchall()
    
    dc_X('NCC',cnnW,crrW)
    
    if is_empty(rows) ==True:
        print("Error: Sampling method should be created to generate initial population. No sample was detected")
        #IDP_assistants.Steph(population,specie,generation,BCs,optiTable,varVar,varVal)
    
    iiiii = 0
    while iiiii < 432.11:
        IDP_assistants.Linda(generation,specie,GENtable,varVal,varVar)
        
        #obtain all results
        pop = IDP_assistants.Toby(generation,specie,GENtable)
        
        #count the number of results        
        popSize = pop.shape[0]
        #find top 20% entries
        TOP = int(popSize*0.2)
        print("High end population size is:",TOP)
        #which column is pheromone level?
        pheroNo = np.size(pop,1)
        TOPmat = IDP_assistants.Fifi(TOP,pop,pheroNo)
        print(TOPmat)
        
        #random new values 
        specimen = np.zeros([1,varN])
        i = 0 
        while i < varN:
            specimen[0,i] = (random.uniform(0,1))*(BCs[i,1]-BCs[i,0])+(BCs[i,0])
            #negative iteration to go through most impactufull (highest pheromone) individual last
            ii = TOPmat.shape[0]-1
            print("random entry",specimen[0,i])
            while ii > -0.1:

                specimen[0,i] = specimen[0,i] + (TOPmat[ii,i]-specimen[0,i])*(TOPmat[ii,pheroNo-1]**2)*0.2
                print(TOPmat[ii,i])
                #this means that subsequent pushes have less effect than the initial one (best result influences more, the 0.1 is greater in magnitude)
                #but it also means that proper motion to minima is not going to be achieved --- 0.1 for the last push in negligible 0.9 is still the difference
                print("adjusted specimen",specimen[0,i])
                ii = ii -1
            i = i + 1
        #specimen[0,3] = int(specimen[0,3])
        
        #BELOW ORIGINAL : ERRASE AFTER NEW VERSION BELOW TESTED
        #cnnW,crrW = cnt_X('NCC')
        #query = "INSERT INTO "+GENtable+"(specie,generation,cs1,cs2,cs3, no_layers, mandrel_speed) VALUES("
        #query += """'"""+specie+"""','"""+str(generation)+"""','"""+str(specimen[0,0])+"""','"""+str(specimen[0,1])+"""','"""+str(specimen[0,2])+"""','"""+str(specimen[0,3])+"""','"""+str(specimen[0,4])+"""')"""
        #crrW.execute(query)
        #cnnW.commit()
        #close SQL handles 
        #dc_X('NCC',cnnW,crrW)
        cnnW,crrW = cnt_X('NCC')
        #filling SQL table with any number of columns used
        i = 0 
        while i < 1: #just one new specimen created at a time?
            #sampleMAT[i,3] = int(sampleMAT[i,3])
            query = "INSERT INTO "+GENtable+"(specie,generation,"
            ii = 0
            while ii < varN:
                query += varVar[ii]+","
                ii = ii + 1
            query = query[:-1]
            query += ") VALUES("
                                              
            query += """'"""+specie+"""',"""+str(generation)+""","""
            ii = 0
            while ii < varN:
                if "airfoil" in varVar[ii]:
                    # Will raise StopIteration if you don't have x files
                    fileNO = int(specimen[i,ii])
                    file1000 = next(itertools.islice(os.scandir(lPath+'\\aerofoilcollection\\'), fileNO, None)).path
                    file1000 = file1000.split(lPath+"\\aerofoilcollection\\")[1]
                    query += """'"""+str(file1000)+"""',"""
                else:
                    query += str(specimen[i,ii])+","
                ii = ii + 1
            query = query[:-1]
            query += ");"
            print("i",i)
            print(query)
            crrW.execute(query)
            cnnW.commit()
            i = i + 1
        dc_X('NCC',cnnW,crrW)
        
        iiiii = iiiii + 1
#AgentFerda()   
    


    
    
def AgentDarwin(GENtable,varVar,varVal,varMin,varMax):
    #specie is the name of the optimisation -- therefore it can be continued if generation already exists
    population = 8
    lPath = os.path.dirname(os.path.abspath(__file__))
    
    
    #here obtain highest generation... instead of prescribing
    generation = 1
    
    
    specie = "test"
    #limits of variables - not physical, estimated at this point ~~~~~~
    # rows : variables : cs1,cs2,cs3,MS,NL
    # columns: min, max
    BCs = np.matrix([[0.000,0.000]])
    temp = np.matrix([[0.000,0.000]])
    i = 0 
    #AFLe = 0
    varN = len(varVar)
    while i < varN:
        if varMin[varVar[i]]!=False:
            temp[0,0] = varMin[varVar[i]]
            temp[0,1] = varMax[varVar[i]]
            BCs = np.concatenate((BCs,temp),axis = 0)
        elif "airfoil" in varVar[i]:
            img_folder_path = lPath+'\\aerofoilcollection\\'
            dirListing = os.listdir(img_folder_path)
            AFLS = len(dirListing)
            temp[0,0] = 0
            temp[0,1] = AFLS
            BCs = np.concatenate((BCs,temp),axis = 0)
            #AFLe = 1
        else:
            #0-10 now arbitrarily selected for string values (eg. material)
            #this needs to be replaced by a lookup function that checks the 
            #number of airfoils
            temp[0,0] = 0
            temp[0,1] = 10
            BCs = np.concatenate((BCs,temp),axis = 0)
    
    #check if specie exists (let Steph do this?)
    cnnW,crrW = cnt_X('NCC')
    query = """SELECT * FROM ga1 where specie like '"""+specie+"""';"""
    crrW.execute(query)
    sd = []
    rows = crrW.fetchall()
    maxG = 0
    #creates a list of version numbers
    for row in rows:
        try:
            #highest version number is stored
            if row[2]> maxG:
                maxG = row[2]
            sd.append(row[2])
            #break
        except TypeError:
            print("No previous population, or other unaccounted error")

    
    
    # if no population exists:
    if is_empty(sd) ==True:
        specimen = np.zeros([population,np.size(BCs,0)])
        i = 0
        while i < population:
            #create new population -- number  of individuals, fully random each variable in range
            ii = 0
            while ii < np.size(BCs,0):
                specimen[i,ii] = (random.uniform(0,1))*(BCs(ii,1)-BCs(ii,0))+(BCs(ii,0))
                ii = ii + 1
            cnnW,crrW = cnt_X('NCC')
            # export the new generation into SQL table
            #filling SQL table with any number of columns used
            I = 0 
            while I < 1: #just one new specimen created at a time?
                #sampleMAT[i,3] = int(sampleMAT[i,3])
                query = "INSERT INTO "+GENtable+"(specie,"+str(generation)+","
                II = 0
                while II < varN:
                    query += varVar[II]+","
                    II = II + 1
                query = query[:-1]
                query += ") VALUES("
                                              
                query += """'"""+specie+"""',"""+str(generation)+""","""
                II = 0
                while II < varN:
                    if "airfoil" in varVar[II]:
                        # Will raise StopIteration if you don't have x files
                        fileNO = int(specimen[I,II])
                        file1000 = next(itertools.islice(os.scandir(lPath+'\\aerofoilcollection\\'), fileNO, None)).path
                        file1000 = file1000.split(lPath+"\\aerofoilcollection\\")[1]
                        query += """'"""+str(file1000)+"""',"""
                    else:
                        query += str(specimen[I,II])+","
                    II = II + 1
                query = query[:-1]
                query += ");"
                crrW.execute(query)
                cnnW.commit()
                I = I + 1
            dc_X('NCC',cnnW,crrW)
            i= i +1
        maxG = 1
    #check which generation we are on, if this is 0 error has occured as at least 1 should exist now
    if maxG > 0:
        print("Current generation is ",maxG)
    else:
        print("something is clearly wrong")
        exit()
            
    # check for uncalculated individuals (value null), and calculate those     
    query = """SELECT * FROM ga1 where fitness is null and generation = '"""+str(maxG)+"""';"""
    #print(query)
    crrW.execute(query)
    sd = []
    rows = crrW.fetchall()
    #close SQL handles 
    dc_X('NCC',cnnW,crrW)
    
    #for row in rows:
        #error handling switched off for now
        #try:
        
        
        
        #STOPPED HERE IN TRANSLATION OF INFINITE VARIABLES
  
        #evaluate the simulations -- use fitness function to establish value of each individual
    IDP_assistants.Linda(generation,specie,GENtable,varVal,varVar)
            
        # if error during calculation assign value 0 
        #except TypeError:
            #print("Error has occured, this individual is assumed 0 fitness")
            #recordID = row[0]
            #query = """UPDATE irut.ga1 SET  fitness = """+str(0)+""", arunID = """+str(0)+""" Where (idnew_table = """+str(recordID)+""");"""
            #crrW.execute(query)
            #crrW.execute(query)
            #cnnW.commit()

    # obtain data from the last generation   
    cnnW,crrW = cnt_X('NCC')
    query = """SELECT * FROM """+GENtable+""" where generation = '"""+str(maxG)+"""' and specie = '"""+specie+"""';"""
    crrW.execute(query)
    pop = np.zeros([1,len(varVal)])
    popi = np.zeros([1,len(varVal)])
    rows = crrW.fetchall()
    for row in rows:
        i = 0 
        while i < len(varVal):
            popi[0,i] = row[3+i]
        pop = np.concatenate((pop, popi), axis=0)
    pop = np.delete(pop, (0), axis=0)

    #pick suitable individuals 
    #while the population is too large
    pop = np.size(popi,0)
    while pop.shape[0] > (population/2):
        i = 0
        current_min = 999
        #loop through current population available
        while i < pop.shape[0]:
            #indicate the lowest of the current population
            if pop[i,5] < current_min:
                current_min = pop[i,3+len(varVal)]
                ii = i
            i = i + 1
        #delete the lowest of the current population
        pop = np.delete(pop, (ii), axis=0)
    
    #shuffles randomly the rows in pop
    np.random.shuffle(pop)
    
    #crossover
    # currently 4 offspring of 2 pairs,faster convergence is expected, other alternatives can be tested
    newpop = np.zeros([1,len(varVal)])
    newpopS = np.zeros([1,len(varVal)])
    i = int(0)
    while i < pop.shape[0]/2:
        #second match from the other end of matrix
        y = pop.shape[0]-1 - i
        iii = 0
        while iii < 4:
            ii = 0
            #fist child of parents i
            while ii < len(varVal):
                #randomise which parent fits the bill
                Parent = (random.randint(0, 1))
                if Parent == 0:
                    s = int(y) 
                if Parent == 1:
                    s = int(i)
                newpopS[0,ii] = pop[s,ii]
                ii = ii + 1
            newpop = np.concatenate((newpop, newpopS), axis=0)
            iii = iii + 1
        i = i + 1
    newpop = np.delete(newpop, (0), axis=0)
    
    #randomely select a gene in population to mutate
    #this will need rework for more variables -- matrix of limits~~~~~~~~~~~~~~~~~~~~~
    
    #the mutation rate decreases with generations
    mutR = 5 - maxG
    i = 0
    while i < mutR:
        member = random.randint(0, (population-1))
        trait = random.randint(0,len(varVal))

        MutVar = (random.uniform(0,1))*(BCs[trait,1]-BCs[trait,0])+(BCs[trait,0])

        newpop[member,trait] = MutVar
        i = i + 1
    
    print(newpop)
    i = 0
    maxG = maxG + 1
    cnnW,crrW = cnt_X('NCC')
    while i < newpop.shape[0]:
        
        # export the new generation into SQL table
        #filling SQL table with any number of columns used
        I = 0 
        while I < 1: #just one new specimen created at a time?
            #sampleMAT[i,3] = int(sampleMAT[i,3])
            query = "INSERT INTO "+GENtable+"(specie,"+str(maxG)+","
            II = 0
            while II < varN:
                query += varVar[II]+","
                II = II + 1
            query = query[:-1]
            query += ") VALUES("
                                          
            query += """'"""+specie+"""',"""+str(generation)+""","""
            II = 0
            while II < varN:
                if "airfoil" in varVar[II]:
                    # Will raise StopIteration if you don't have x files
                    fileNO = int(specimen[I,II])
                    file1000 = next(itertools.islice(os.scandir(lPath+'\\aerofoilcollection\\'), fileNO, None)).path
                    file1000 = file1000.split(lPath+"\\aerofoilcollection\\")[1]
                    query += """'"""+str(file1000)+"""',"""
                else:
                    query += str(specimen[I,II])+","
                II = II + 1
            query = query[:-1]
            query += ");"
            crrW.execute(query)
            cnnW.commit()
            I = I + 1
        i = i + 1
    dc_X('NCC',cnnW,crrW)

def Nekonecnej():
    i = 0
    while i < 678:
        AgentDarwin("Vespa")
        i = i - i**2 +i/6000 - i/300
        
#Nekonecnej()
        
