

from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
#from IDP_cheats import togglePulse
import time

#connection to the database
db_config = read_db_config()
cnnI = MySQLConnection(**db_config)
crrI = cnnI.cursor()


DN = "irut" #random database name
query = "CREATE DATABASE "+DN
crrI.execute(query)
cnnI.commit()


crrI.close()
cnnI.close()
#togglePulse()

time.sleep(30)
#connection to the database
db_config = read_db_config(filename='config2.ini')
cnnI = MySQLConnection(**db_config)
crrI = cnnI.cursor()

#main results table
query = "CREATE TABLE `arun` (`idArun` int(11) NOT NULL AUTO_INCREMENT,`project` varchar(45) DEFAULT NULL,"\
        "`Part` varchar(45) DEFAULT NULL,`Iteration_count` int(11) DEFAULT NULL,`CADfile` varchar(45) DEFAULT NULL,"\
        "`BraidFile` varchar(45) DEFAULT NULL,`MeshFile` varchar(45) DEFAULT NULL,`FeFile` varchar(45) DEFAULT NULL,"\
        "`span_ele_size` decimal(8,3) DEFAULT NULL,`xs_seed` int(11) DEFAULT NULL,`root_perimeter` decimal(8,3) DEFAULT NULL,"\
        "`Pher` float DEFAULT NULL,`simulation_time` float DEFAULT NULL,`date` date DEFAULT NULL,PRIMARY KEY (`idArun`)"\
        ") ENGINE=InnoDB AUTO_INCREMENT=512 DEFAULT CHARSET=ascii;"
crrI.execute(query)

#main braiding table
query = "CREATE TABLE `braidmain` (`id` mediumint(9) NOT NULL AUTO_INCREMENT,`GENfile` varchar(255) DEFAULT NULL,"\
        "`version` int(2) DEFAULT NULL,`spoolsWa` decimal(4,0) DEFAULT NULL,`rota` decimal(3,1) DEFAULT NULL,"\
        "`travel` decimal(5,1) DEFAULT NULL,`GuideRadius` decimal(8,2) DEFAULT NULL,`InitialMandrelDistance` decimal(8,2) DEFAULT NULL,"\
        "`NoIterations` int(2) DEFAULT NULL,PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=319 DEFAULT CHARSET=ascii;"
crrI.execute(query)

#main FE table
query = "CREATE TABLE `fe_inst` (`ID` mediumint(9) NOT NULL AUTO_INCREMENT,`MeshFile` varchar(255) DEFAULT NULL,"\
        "`BraidFile` varchar(255) DEFAULT NULL,`material` varchar(255) DEFAULT NULL,"\
        "`FeFile` varchar(255) DEFAULT NULL,`version` int(2) DEFAULT NULL,"\
        "`max_deflection` decimal(8,3) DEFAULT NULL,`mass` float DEFAULT NULL,"\
        "`no_layers` int(11) DEFAULT NULL,`force_N` float DEFAULT NULL,"\
        "`spanwise_sections` int(11) DEFAULT NULL,PRIMARY KEY (`ID`)) ENGINE=InnoDB AUTO_INCREMENT=430 DEFAULT CHARSET=ascii;"
crrI.execute(query)

#fibre material properties table
query = "CREATE TABLE `fibre_properties` (`id` int(11) NOT NULL AUTO_INCREMENT,"\
        "`Material_name` varchar(100) DEFAULT NULL,`E1` decimal(10,3) DEFAULT NULL,"\
        "`E2` decimal(10,3) DEFAULT NULL,`G12` decimal(10,3) DEFAULT NULL,"\
        "`v12` decimal(4,3) DEFAULT NULL,`Info_source` varchar(255) DEFAULT NULL,"\
        "`fibre_dia` decimal(10,8) DEFAULT NULL,`density` decimal(15,14) DEFAULT NULL,"\
        "`perme_coeff` float DEFAULT NULL,"\
        "PRIMARY KEY (`id`),UNIQUE KEY `id_UNIQUE` (`id`)) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=ascii;"
crrI.execute(query)

#original optimisation record table
query = "CREATE TABLE `ga1` (`idnew_table` int(10) unsigned NOT NULL AUTO_INCREMENT,"\
        "`specie` varchar(55) DEFAULT NULL,`generation` int(11) DEFAULT NULL,`cs1` float DEFAULT NULL,"\
        "`cs2` float DEFAULT NULL,`cs3` float DEFAULT NULL,`no_layers` int(11) DEFAULT NULL,"\
        "`mandrel_speed` float DEFAULT NULL,`fitness` float DEFAULT NULL,`arunID` int(11) DEFAULT NULL,"\
        "PRIMARY KEY (`idnew_table`),UNIQUE KEY `idnew_table_UNIQUE` (`idnew_table`)"\
        ") ENGINE=InnoDB AUTO_INCREMENT=439 DEFAULT CHARSET=ascii;"
crrI.execute(query)

#matrix material properties table
query = "CREATE TABLE `matrix_properties` (`id` int(11) NOT NULL AUTO_INCREMENT,`Material_name` varchar(100) DEFAULT NULL,"\
        "`E` decimal(10,3) DEFAULT NULL,`poisson` decimal(5,3) DEFAULT NULL,`Xmt` decimal(10,3) DEFAULT NULL,"\
        "`Xmc` decimal(10,3) DEFAULT NULL,`Sm` decimal(10,3) DEFAULT NULL,`G` decimal(10,3) DEFAULT NULL,"\
        "`density` decimal(15,14) DEFAULT NULL,`Info_source` varchar(255) DEFAULT NULL,PRIMARY KEY (`id`),"\
        "UNIQUE KEY `id_UNIQUE` (`id`)) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=ascii;"
crrI.execute(query)

#meshing record table
query = "CREATE TABLE `mesh_list` (`id` mediumint(9) NOT NULL AUTO_INCREMENT,`CADfile` varchar(255) DEFAULT NULL,"\
        "`MeshFile` varchar(255) DEFAULT NULL,`xs_seed` int(11) DEFAULT NULL, `span_ele_size` decimal(8,3) DEFAULT NULL,"\
        "`version` int(11) DEFAULT NULL,`verified_mesh` varchar(255) DEFAULT NULL,PRIMARY KEY (`id`)"\
        ") ENGINE=InnoDB AUTO_INCREMENT=303 DEFAULT CHARSET=ascii;"
crrI.execute(query)


#main basic CAD shape record table
query = "CREATE TABLE `sim_cad_iterations` (`id` mediumint(9) NOT NULL AUTO_INCREMENT,"\
        "`product` varchar(255) DEFAULT NULL,`version` varchar(255) DEFAULT NULL,"\
        "`iteration` varchar(255) DEFAULT NULL,`RefInput` varchar(255) DEFAULT NULL,"\
        "`chord_max` varchar(155) DEFAULT NULL,`chord_min` varchar(155) DEFAULT NULL,"\
        "`created_on` varchar(155) DEFAULT NULL,PRIMARY KEY (`id`)"\
        ") ENGINE=InnoDB AUTO_INCREMENT=526 DEFAULT CHARSET=ascii;"
crrI.execute(query)


cnnI.commit()



#input base material information
matrix_name = "Bakelite EPR-L20"
E = 3300
poisson = 0.350
Xmt = 60.180
Xmc = 107.370
Sm = 41.030
G = 1250
density = 0.00000000209000
Info_source = "C.Wang"
query = "INSERT INTO matrix_properties(Material_name,E,poisson,Xmt,Xmc,Sm,G,density,Info_source) VALUES("
query += """'"""+matrix_name+"""','"""+str(E)+"""','"""+str(poisson)+"""','"""+str(Xmt)+"""','"""+str(Xmc)+"""','"""+str(Sm)+"""','"""+str(G)+"""','"""+str(density)+"""','"""+str(Info_source)+"""')"""
crrI.execute(query)
cnnI.commit()

fibre_name = "AKSAca A-42"
E1 = 239500
E2 = 13400
G12 =6810
v12 = 0.2
fibre_dia = 0.1
density = 0.00000000176000
pc = 0.00000000000082
query = "INSERT INTO fibre_properties(Material_name,E1,E2,G12,v12,Info_source,fibre_dia,density,perme_coeff) VALUES("
query += """'"""+fibre_name+"""','"""+str(E1)+"""','"""+str(E2)+"""','"""+str(G12)+"""','"""+str(v12)+"""','"""+str(Info_source)+"""','"""+str(fibre_dia)+"""','"""+str(density)+"""','"""+str(pc)+"""')"""
crrI.execute(query)
cnnI.commit()


crrI.close()
cnnI.close()
#togglePulse()