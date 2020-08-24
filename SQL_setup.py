

#from mysql.connector import MySQLConnection, Error
#from python_mysql_dbconfig import read_db_config
#from IDP_cheats import togglePulse
from IDP_databases import cnt_X, dc_X

#connection to the database
cnnI, crrI = cnt_X('NCC')


#main results table
query = "CREATE TABLE arun (idArun int IDENTITY(1,1) PRIMARY KEY,project varchar(45),"\
        "part varchar(45),Iteration_count int,CADfile varchar(45),"\
        "braidFile varchar(45),meshFile varchar(45),FEfile varchar(45),"\
        "span_ele_size numeric(8,3),xs_seed int,root_perimeter decimal(8,3),"\
        "pher float,simulation_time float,date date"\
        ");"
crrI.execute(query)

#main FE table
query = "CREATE TABLE fe_inst (ID int IDENTITY(1,1) PRIMARY KEY,meshFile varchar(255),"\
        "braidFile varchar(255),material varchar(255),"\
        "feFile varchar(255),version int,"\
        "max_deflection decimal(8,3),mass float,"\
        "no_layers int,force_N float,"\
        "spanwise_sections int);"
crrI.execute(query)

#fibre material properties table
query = "CREATE TABLE fibre_properties (id int IDENTITY(1,1) PRIMARY KEY,"\
        "Material_name varchar(100),E1 decimal(10,3),"\
        "E2 decimal(10,3),G12 decimal(10,3),"\
        "v12 decimal(4,3),Info_source varchar(255),"\
        "fibre_dia decimal(10,8),density decimal(15,14),"\
        "perme_coeff float,"\
        ");"
crrI.execute(query)

#original optimisation record table
query = "CREATE TABLE ga1 (id int IDENTITY(1,1) PRIMARY KEY,"\
        "specie varchar(55),generation int,cs1 float,"\
        "cs2 float,cs3 float,no_layers int,"\
        "mandrel_speed float,fitness float,arunID int"\
        ");"
crrI.execute(query)

#matrix material properties table
query = "CREATE TABLE matrix_properties (id int IDENTITY(1,1) PRIMARY KEY,Material_name varchar(100),"\
        "E decimal(10,3),poisson decimal(5,3),Xmt decimal(10,3),"\
        "Xmc decimal(10,3),Sm decimal(10,3),G decimal(10,3),"\
        "density decimal(17,16),Info_source varchar(255)"\
        ");"
crrI.execute(query)

#meshing record table
query = "CREATE TABLE mesh_list (id int IDENTITY(1,1) PRIMARY KEY,CADfile varchar(255),"\
        "MeshFile varchar(255),xs_seed int, span_ele_size decimal(8,3),"\
        "version int,verified_mesh varchar(255)"\
        ");"
crrI.execute(query)


#main basic CAD shape record table
query = "CREATE TABLE sim_cad_iterations (id int IDENTITY(1,1) PRIMARY KEY,"\
        "product varchar(255),version varchar(255),"\
        "iteration varchar(255),RefInput varchar(255),"\
        "chord_max varchar(155),chord_min varchar(155),"\
        "created_on varchar(155)"\
        ");"
crrI.execute(query)

query = "CREATE TABLE rtm_main (id int IDENTITY(1,1) PRIMARY KEY,"\
        "MeshFile varchar(255),BraidFile varchar(255),"\
        "RTMFile varchar(255),resin varchar(255),"\
        "version int,Injection_T decimal(10,3),"\
        "Tool_T decimal(10,3),Injection_P decimal(10,3),"\
        "Vent_P decimal(15,3),Flow_rate float,"\
        ");"
crrI.execute(query)


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
query += """'"""+matrix_name+"""',"""+str(E)+""","""+str(poisson)+""","""+str(Xmt)+""","""+str(Xmc)+""","""+str(Sm)+""","""+str(G)+""","""+str(density)+""",'"""+str(Info_source)+"""')"""
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
query += """'"""+fibre_name+"""',"""+str(E1)+""","""+str(E2)+""","""+str(G12)+""","""+str(v12)+""",'"""+str(Info_source)+"""',"""+str(fibre_dia)+""","""+str(density)+""","""+str(pc)+""")"""
crrI.execute(query)

cnnI.commit()

dc_X('NCC',cnnI,crrI)

