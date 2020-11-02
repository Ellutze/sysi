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
