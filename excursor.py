#from SQLserverconfig import readconfig

#client, UID, heslo, driver, server, database = readconfig()
import pyodbc

def excursor():
    #driver= '{SQL Server Native Client 11.0}'
    
    #input file - instead function arguments - which are not possible due to the command line passing
    fl = open("sql_config.txt","rt")
    flstr = fl.read() 
    uid = flstr.splitlines()[0]
    pwd = flstr.splitlines()[1]
    driver = flstr.splitlines()[2]
    server = flstr.splitlines()[3]
    database = flstr.splitlines()[4]
    
    cnxn = pyodbc.connect(
            Trusted_Connection='No',
            UID = uid,
            PWD = pwd,
            Driver=driver,
            Server=server,
            Database=database
            )
    cursor = cnxn.cursor()
    return(cursor, cnxn)

