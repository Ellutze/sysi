from sklearn.svm import SVR
import numpy as np
n_samples, n_features = 10, 3
rng = np.random.RandomState(0)
#from IDP_databases import cnt_X,dc_X
#from python_mysql_dbconfig import read_db_config
#from data_proc_utils import shuffle
#from data_proc_utils import collector
#from data_proc_utils import fit2,fit3,collector,shuffle

#y = rng.randn(n_samples)
#X = rng.randn(n_samples, n_features)

'''
GENtable = "[DIGIProps].[dbo].[_iters_37]"
cnnT,crrT = cnt_X('NCC')
#print(GENtable)
query = """SELECT no_layers, mandrel_speed, fitness,arunID FROM """+GENtable+""" where fitness > 0;"""
#print(query)
crrT.execute(query)
rows = crrT.fetchall()

M =np.matrix([0.000,0.000,0.000,0.000,0.00,0.0,0.0])
Mtamp = np.matrix([0.000,0.000,0.000,0.000,0.00,0.0,0.0])
for i in rows:
    #Mtamp[0,4] = (i[4])
    Mtamp[0,1] = (i[1])
    Mtamp[0,2] = (i[2])
    Mtamp[0,0] = (i[0])
    #Mtamp[0,3] = (i[3])
    query = """SELECT FEfile FROM arun where idArun = """+str(i[3])+""";"""
    crrT.execute(query)
    FEfile = crrT.fetchall()
    for mu in FEfile:    
        mu1 = str(mu[0])
    query = """SELECT max_deflection, mass FROM fe_inst where FEfile = '"""+mu1+"""';"""
    print(query)
    crrT.execute(query)
    fitComp = crrT.fetchall()  
    print(fitComp)
    for nu in fitComp:
        #max_deflectoin
        Mtamp[0,3] = nu[0]
        #mass
        Mtamp[0,4] = nu[1]
    M = np.concatenate((M,Mtamp),axis=0)
M = np.delete(M,0,axis=0)
multi = 100
print(M)

dc_X('NCC',cnnT,crrT)
'''

nom, dt, colis = collector([36,37,38,39,40,41])
#print(dt)


#optional translation of fitness
dt = fit3(dt)


M = shuffle(dt)

pofi = np.size(dt,1)-3
print("number of vars is:",nom)
print("number of datapoints is:",np.size(M,0))

i = 0
while i < np.size(M,0):
    M[i,2] = M[i,2] 
    #*multi)
    i = i + 1
    
    
'''
#cleaning up outliers:
i = 0
while i < np.size(M,0):
    if M[i,2] > 0.6:
        M = np.delete(M,i,axis=0)
    #if M[i,2] < 0.45:
    #    M = np.delete(M,i,axis=0)
    i = i + 1
'''    
    

#M[:3]
MX = np.zeros([np.size(M,0),np.size(M,1)])
#makes the variables the same scale
i = 0
while i < np.size(M,1):
   rng = max(M[:,i])-min(M[:,i])
   print(i)
   print(max(M[:,i]))
   print(min(M[:,i]))
   
   ii = 0
   while ii < np.size(M,0):
       if i != pofi:
           MX[ii,i] = (M[ii,i]-min(M[:,i]))/rng
       else:
           MX[ii,i] = M[ii,i]
       ii = ii + 1
   i = i + 1
   
#MX = M
#i = 0
#while i < np.size(M,0):
#    
#    M[i,3] = M[i,3]**6
#    i = i + 1
mem = (np.size(MX,axis=0))
h = int((mem/2))

M1 = np.copy(MX[0:h,:])
X3 = np.copy(MX[h:mem,:])
#X3 = np.split(M,h,axis=0)
print("size of M1",np.size(M1,0))
print("size of x3",np.size(X3,0))

#print(M3)
#M[:,0:3] = 0
#M3[:,0:3]=0


#X = np.copy(M1[:,0:3])
X = np.copy(M1[:,0:pofi])


y = np.copy(M1[:,pofi])
#X3 = np.copy(M3[:,0:4])

#print("checkpoint2")
#gamma=0.001 ==> deleted
clf = SVR(kernel='poly',degree =7, C=20, gamma='auto', epsilon=0.0000001,coef0=1)
clf.fit(X, y) 
#x = clf.predict(X3[:,0:3])

#for prediction curve
#print("checkpoint3")

ver_pred = clf.predict(X3[:,0:pofi])



#use prediction for differential evolution
import scipy

from default_var_dict import getBase

varVal,varMin,varMax = getBase()

print(colis)

#bounds = np.zeros([len(colis),2])
#i = 0
#while i < len(colis):
#    bounds[i,0] = 0#varMin[colis[i]]
#    bounds[i,1] = 1#varMax[colis[i]]
#    i = i + 1
#print("bounds",bounds)
bounds = [(0,1),(0,1),(0,1)]

#x =np.zeros([3,1])
#print("x",x)
#i = 0
#while i < len(colis):
#    x[i,0] = 0.5#varVal[colis[i]]
#    i = i + 1
#print("x",x)
DE = np.zeros([1,4])
np.save("temporary\\DE.npy",DE)


#vp2 = clf.predict(x)
#print(vp2)
def ff(x):
    DE = np.load("temporary\\DE.npy")
    y = np.zeros([1,3])
    y[0,0] =x[0]
    y[0,1] =x[1]
    y[0,2] =x[2]
    fit = clf.predict(y)
    fitMin = 1 - fit
    DEt = np.matrix([x[0],x[1],x[2],fit[0]])
    DE = np.concatenate((DE,DEt),axis = 0)
    np.save("temporary\\DE.npy",DE)
    return(fitMin)


result = scipy.optimize.differential_evolution( ff, bounds)

#, strategy='best1bin', maxiter=1000,\
                                               #popsize=15, tol=0.01, mutation=(0.5, 1), recombination=0.7, \
                                               #seed=None, callback=None, disp=False, polish=True, init='latinhypercube', \
                                               #atol=0, updating='immediate', workers=1)
print(result.x, result.fun)







#breakhere

#print("predicted:")
#print(ver_pred)
#print("actual:")
#print(X3[:,2])

i = 0
errm = np.zeros([np.size(X3,0),1])
T = 0
while i < np.size(X3,0):
    errm[i,0] = abs(ver_pred[i]-X3[i,pofi])
    T = T + errm[i,0]
    i = i + 1
    
print("total error is:",T,"for",np.size(errm,0),"results")
print("average error is:",T/np.size(errm,0))
    
#normalize errors:
i=0

rng = max(errm[:,0])-min(errm[:,0])
errn = np.zeros([np.size(errm,0),1])
while i < np.size(errn,0):
    errn[i,0] = ((((errm[i,0]-min(errm[:,0]))/rng)**1/2)*100)+15
    i=i+1
#print(terr)




from bokeh.io import output_file, show
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.models import Range1d
import numpy as np

#Select output format.
output_file("layout.html")
#Create first plot
s1 = figure(title="1",plot_width=500, plot_height=500)
s1.circle( X3[:,1], ver_pred, size=10, color="firebrick", alpha=0.5,legend="predictions")
s1.triangle(X3[:,1],X3[:,pofi], size=10, color="navy", alpha=0.5,legend="validation data")
s1.circle(X[:,1],y, color="orange", alpha =0.5,legend="teaching data")
s1.xaxis.axis_label = colis[1]
s1.yaxis.axis_label = 'fitness'
#s1.triangle(X3[:,3], x, size=10, color="firebrick", alpha=0.5,legend="predictions")
#Create second plot
s2 = figure(title="2",plot_width=500, plot_height=500)
#s2.x_range=Range1d(250, 500)
#s2.y_range=Range1d(80, 105)
#Triangles stand for fully infused datapoints.
s2.circle(X3[:,0], ver_pred, size=10, color="firebrick", alpha=0.5,legend="predictions")
#Circles stand for failed infusions.
s2.triangle(X3[:,0],X3[:,pofi],size=10, color="navy", alpha =0.5,legend="validation data")

s2.circle(X[:,0],y, color="orange", alpha =0.5,legend="teaching data")
s2.xaxis.axis_label = colis[0]
s2.yaxis.axis_label = 'fitness'
s2.legend.location = "top_right"
#Create third plot
s3 = figure(plot_width=500, plot_height=500)
#s2.x_range=Range1d(250, 500)
#s2.y_range=Range1d(80, 105)
#Triangles stand for fully infused datapoints.
s3.triangle(X3[:,1], X3[:,0], size=10, color="firebrick", alpha=0.5)
s3.circle(X3[:,1], X3[:,0], size=errn[:,0], color="navy", alpha=0.5,fill_color="white", line_width=3)

#Circles stand for failed infusions.
#s3.circle(X3[:,2],X3[:,4], color="green", alpha =0.5,legend="source data")
s3.xaxis.axis_label = colis[1]
s3.yaxis.axis_label = colis[0]
#s3.legend.location = "top_right"


#Triangles stand for fully infused datapoints.
s4 = figure(title="1",plot_width=500, plot_height=500)
s4.circle( X3[:,2], ver_pred, size=10, color="firebrick", alpha=0.5,legend="predictions")
s4.triangle(X3[:,2],X3[:,pofi], size=10, color="navy", alpha=0.5,legend="validation data")
s4.circle(X[:,1],y, color="orange", alpha =0.5,legend="teaching data")
s4.xaxis.axis_label = colis[2]
s4.yaxis.axis_label = 'fitness'
#show(row(s1, s2))


s5 = figure(plot_width=500, plot_height=500)
#s2.x_range=Range1d(250, 500)
#s2.y_range=Range1d(80, 105)
#Triangles stand for fully infused datapoints.
s5.triangle(X3[:,1], X3[:,2], size=10, color="firebrick", alpha=0.5)
s5.circle(X3[:,1], X3[:,2], size=errn[:,0], color="navy", alpha=0.5,fill_color="white", line_width=3)

#Circles stand for failed infusions.
#s3.circle(X3[:,2],X3[:,4], color="green", alpha =0.5,legend="source data")
s5.xaxis.axis_label = colis[1]
s5.yaxis.axis_label = colis[2]
#s3.legend.location = "top_righ


s6 = figure(plot_width=500, plot_height=500)
#s2.x_range=Range1d(250, 500)
#s2.y_range=Range1d(80, 105)
#Triangles stand for fully infused datapoints.
s6.triangle(X3[:,0], X3[:,2], size=10, color="firebrick", alpha=0.5)
s6.circle(X3[:,0], X3[:,2], size=errn[:,0], color="navy", alpha=0.5,fill_color="white", line_width=3)

#Circles stand for failed infusions.
#s3.circle(X3[:,2],X3[:,4], color="green", alpha =0.5,legend="source data")
s6.xaxis.axis_label = colis[0]
s6.yaxis.axis_label = colis[2]
#s3.legend.location = "top_righ
show(row(s1,s2,s4,s3,s5,s6))
