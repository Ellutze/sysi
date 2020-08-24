from mysql.connector import MySQLConnection
from IDP_cheats import togglePulse #only required due to VPN connection 
from python_mysql_dbconfig import read_db_config

from excursor import excursor

def cnt_X(reference):
    #reference = NCC , when SQL_server is being accessed
    #reference = UoB , when MySQL at UoB is being accessed
    #reference = ....
    if reference == 'NCC':
        cursor, connection = excursor()
        
    elif reference == 'UoB':
        db_config = read_db_config()
        connection = MySQLConnection(**db_config)
        cursor = connection.cursor()
        
    return(connection,cursor)


def dc_X(reference,connection,cursor):
    if reference == 'NCC':
        cursor.close()
        connection.close()
    elif reference == 'UoB':
        cursor.close()
        connection.close()
        togglePulse()