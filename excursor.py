#from SQLserverconfig import readconfig

#client, UID, heslo, driver, server, database = readconfig()
import pyodbc

def excursor():
    #driver= '{SQL Server Native Client 11.0}'
    cnxn = pyodbc.connect(
            Trusted_Connection='No',
            UID = '',
            PWD = '',
            Driver='{ODBC Driver 17 for SQL Server}',
            Server='',
            Database=''
            )
    cursor = cnxn.cursor()
    return(cursor, cnxn)
