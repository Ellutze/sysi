#from SQLserverconfig import readconfig

#client, UID, heslo, driver, server, database = readconfig()
import pyodbc

def excursor():
    #driver= '{SQL Server Native Client 11.0}'
    cnxn = pyodbc.connect(
            Trusted_Connection='No',
            UID = 'DIGIProps',
            PWD = 'QNv8@AYq',
            Driver='{ODBC Driver 17 for SQL Server}',
            Server='NCC-sql-02',
            Database='DIGIProps'
            )
    cursor = cnxn.cursor()
    return(cursor, cnxn)
