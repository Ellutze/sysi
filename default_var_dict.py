#These are dictionaries of defualt variables, minimum values and maximum values respectivelly.

def getBase():

    varVal = {'span': 400,'twist_0': 0,'chord_0': 150,'no_layers': 8,'twist_1':0,'chord_1':150,'matrix':"Bakelite EPR-L20",'twist_2':0,'chord_2':150,'reinforcement':"AKSAca A-42",'twist_3':0,'chord_3':150,
          'mesh_size':1.75,'airfoil_0':"clarkYdata.dat",'sweep_0':0,'spools':168,'airfoil_1':"clarkYdata.dat",'sweep_1':0,'RAD':3, 'airfoil_2':"clarkYdata.dat",'sweep_2':0,'mandrel_speed':4,'airfoil_3':"clarkYdata.dat",'sweep_3':0,
          'dihedral_0':0,'dihedral_1':0,'dihedral_2':0,'dihedral_3':0,'c_min':0.30,'c_max':0.45,'guide_rad':700,'IMD':500,'inlet_temp':410,'tool_temp':300,
          'inlet_pressure':200000000,'vent_pressure':10,'flow_rate':(1.0*10**(-8))}
    
    #varMin should not be exactly 0, it counts as False which puts it in same category as strings
    varMin = {'span': 150,'twist_0': -20,'chord_0': 80,'no_layers': 1,'twist_1':-20,'chord_1':50,'matrix': False,'twist_2':-20,'chord_2':50,'reinforcement':False,'twist_3':-20,'chord_3':50,
          'mesh_size':0.1,'airfoil_0':False,'sweep_0':-20,'spools':16,'airfoil_1': False,'sweep_1':-20,'RAD':1, 'airfoil_2':False,'sweep_2':-20,'mandrel_speed':1,'airfoil_3':False,'sweep_3':-20,
          'dihedral_0':-10,'dihedral_1':-10,'dihedral_2':-10,'dihedral_3':-10,'c_min':0.1,'c_max':0.2,'guide_rad':100,'IMD':50,'inlet_temp':300,'tool_temp':273,
          'inlet_pressure':2000000,'vent_pressure':0.01,'flow_rate':(1.0*10**(-10))}
    
    varMax ={'span': 800,'twist_0': 20,'chord_0': 400,'no_layers': 20,'twist_1':20,'chord_1':350,'matrix': False,'twist_2':20,'chord_2':250,'reinforcement':False,'twist_3':20,'chord_3':200,
         'mesh_size':10,'airfoil_0':False,'sweep_0':20,'spools':300,'airfoil_1': False,'sweep_1':20,'RAD':8, 'airfoil_2':False,'sweep_2':20,'mandrel_speed':12,'airfoil_3':False,'sweep_3':20,
         'dihedral_0':10,'dihedral_1':10,'dihedral_2':10,'dihedral_3':10,'c_min':0.6,'c_max':0.7,'guide_rad':1000,'IMD':500,'inlet_temp':573,'tool_temp':473,
          'inlet_pressure':2000000000,'vent_pressure':10000,'flow_rate':(1.0*10**(-4))}
    return(varVal,varMin,varMax)

#varVal, varMin,varMax = getBase()
#varMax["span"] = 1111111111111111
#print(varVal, varMin,varMax)
#print(type(varVal['span']))
