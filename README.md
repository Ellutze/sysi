# sysi
System of simulation for holistic composite design
## User: Quick start guide 
This section of the documentation walks user through the minimal steps required to run one trial run of the System of Simulations. 
| | Pre-requisite | |
| --- | --- | --- |
| 1 | CATIA installation | 5.27.4 tested, but other versions should work
| 2 | Python libraries | lhsmdu, sklearn, PySimpleGUI, pyodbc, time,math, subprocess, bokeh, sys, pywin32,  os,numpy, (installing through requirements.txt should be possible “pip install -r requirements.txt”) |
| 3 | SQL Server Database | After SQL server is installed, database has to be configured. User needs to create “sql_config.txt” file in the main script directory. The information that should be stored in each line is as follows: user ID, password, SQL driver, server, database name. Example of how the file should look is shown on figure below. After the “sql_config.txt” file is ready, user can run “sql_setup.py” which creates all tables required. Default resin and fibre materials are also saved to relevant tables. |
| 4 | Abaqus installation | This includes built-in python libraries (2018 version tested) |

(picture to be inserted here)
### Figure X – configuration file for SQL server 

Running IDP_GUI.py displays various iteration options. It is recommended that for the first run user selects “mandrel_speed”, “no_layers”, and “spools” as the “altered variables”. In the “MAIN” tab user then needs to press run only. This combination of parameters has been well tested and should run smoothly. The progress can be checked by reviewing newly generated tables in the SQL database. 

 


## Developer Guide 

The scripts available here are part of an EngD project. The project aims to use scripts and good data management to allow for more complete design and optimization of braided composite components. Variables are shared between simulations, and an overall fitness function determines value of each optimization iteration. 

The difference between the proposed design strategy and standard design approach is outlined by figure 1. In short, more time is spent developing automatically generated models, which minimizes the amount of work required for design iterations. The scripts in the form presented here are demonstrator of this approach.  

