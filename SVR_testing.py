from sklearn.svm import SVR
import numpy as np
n_samples, n_features = 10, 3
rng = np.random.RandomState(0)
from IDP_databases import cnt_X,dc_X
from python_mysql_dbconfig import read_db_config
from data_proc_utils import shuffle

#y = rng.randn(n_samples)
#X = rng.randn(n_samples, n_features)

GENtable = "[DIGIProps].[dbo].[_iters_36]"
cnnT,crrT = cnt_X('NCC')
#print(GENtable)
query = """SELECT spools, mandrel_speed, fitness,arunID FROM """+GENtable+""" where fitness > 0;"""
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

M = shuffle(M)

print("checkpoint")

i = 0
while i < np.size(M,0):
    M[i,2] = M[i,2]#*multi)
    i = i + 1
    
    
#M[:3]
MX = np.zeros([np.size(M,0),np.size(M,1)])
#makes the variables the same scale
i = 0
while i < np.size(M,1):
   rng = max(M[:,i])-min(M[:,i])
   ii = 0
   while ii < np.size(M,0):
       MX[ii,i] = M[ii,i]#-(min(M[:,i]))/rng
       ii = ii + 1
   i = i + 1
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

#print(M3)
#M[:,0:3] = 0
#M3[:,0:3]=0


#X = np.copy(M1[:,0:3])
X = np.copy(M1[:,0:2])


y = np.copy(M1[:,2])
#X3 = np.copy(M3[:,0:4])

print("checkpoint2")
#gamma=0.001 ==> deleted
clf = SVR(kernel='rbf', C=1, gamma='auto', epsilon=0.000001,coef0=1)
clf.fit(X, y) 
#x = clf.predict(X3[:,0:3])

#for prediction curve
print("checkpoint3")

ver_pred = clf.predict(X3[:,0:2])
print("predicted:")
print(ver_pred)
print("actual:")
print(X3[:,2])

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
s1.triangle(X3[:,1],X3[:,2], size=10, color="navy", alpha=0.5,legend="source data")
s1.circle(X[:,1],y, color="orange", alpha =0.5,legend="teaching data")
s1.xaxis.axis_label = 'mandrel_speed'
s1.yaxis.axis_label = 'fitness'
#s1.triangle(X3[:,3], x, size=10, color="firebrick", alpha=0.5,legend="predictions")
#Create second plot
s2 = figure(title="2",plot_width=500, plot_height=500)
#s2.x_range=Range1d(250, 500)
#s2.y_range=Range1d(80, 105)
#Triangles stand for fully infused datapoints.
s2.triangle(X3[:,0], ver_pred, size=10, color="firebrick", alpha=0.5,legend="predictions")
#Circles stand for failed infusions.
s2.circle(X3[:,0],X3[:,2], color="green", alpha =0.5,legend="source data")

s2.circle(X[:,0],y, color="orange", alpha =0.5,legend="teaching data")
s2.xaxis.axis_label = 'spools'
s2.yaxis.axis_label = 'fitness'
s2.legend.location = "top_right"
#Create third plot
s3 = figure(title="spools and agains mandrel_speed",plot_width=500, plot_height=500)
#s2.x_range=Range1d(250, 500)
#s2.y_range=Range1d(80, 105)
#Triangles stand for fully infused datapoints.
s3.triangle(X3[:,1], X3[:,0], size=10, color="firebrick", alpha=0.5)

#Circles stand for failed infusions.
#s3.circle(X3[:,2],X3[:,4], color="green", alpha =0.5,legend="source data")
s3.xaxis.axis_label = 'mandrel_speed'
s3.yaxis.axis_label = 'spools'
#s3.legend.location = "top_right"

#s4 = figure(title="mandrel_speed",plot_width=500, plot_height=500)
#s2.x_range=Range1d(250, 500)
#s2.y_range=Range1d(80, 105)
#Triangles stand for fully infused datapoints.
#s4.triangle(X3[:,3], ver_pred, size=10, color="firebrick", alpha=0.5,legend="predictions")
#Circles stand for failed infusions.
#s4.circle(X3[:,3],X3[:,6], color="green", alpha =0.5,legend="source data")
#s4.xaxis.axis_label = 'pos2'
#s4.yaxis.axis_label = 'inf perc'
#s4.legend.location = "top_right"
# put the results in a row
#show(row(s1, s2))
show(row(s1,s2,s3))
