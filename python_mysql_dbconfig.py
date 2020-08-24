#do not rename!
from configparser import ConfigParser
#from IDP_cheats import togglePulse
# 'configUoB.ini' or 'config64.ini'
def read_db_config(filename='configUoB.ini', section = 'mysql'):
    #filename = 'configUoB.ini' #for UoB MySQL
    #filename = 'config64.ini' #for laptop based MySQl
    
    #if filename == 'configUoB.ini':
    #    togglePulse()
    
    parser = ConfigParser()
    parser.read(filename)
    db= {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section,filename))
    #print(db) 
    return db