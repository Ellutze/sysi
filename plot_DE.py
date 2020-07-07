# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 15:56:56 2020

@author: jakub.kucera
"""

import numpy as np
DE =np.load("temporary\\DE.npy", allow_pickle=True)
print(DE)

DE = np.delete(DE,0,axis=0)

from bokeh.io import output_file, show
from bokeh.layouts import row
from bokeh.plotting import figure
from bokeh.models import Range1d
import numpy as np

#Select output format.
output_file("layout.html")
#Create first plot
s1 = figure(title="1",plot_width=500, plot_height=500)
s1.circle( DE[:,0], DE[:,1], size=10, color="firebrick", alpha=0.5)
#s1.triangle(X3[:,1],X3[:,pofi], size=10, color="navy", alpha=0.5,legend="validation data")
#s1.circle(X[:,1],y, color="orange", alpha =0.5,legend="teaching data")
s1.xaxis.axis_label = "spools"
s1.yaxis.axis_label = 'mandrel speed'
#s1.triangle(X3[:,3], x, size=10, color="firebrick", alpha=0.5,legend="predictions")
#Create second plot
s2 = figure(title="2",plot_width=500, plot_height=500)
#s2.x_range=Range1d(250, 500)
#s2.y_range=Range1d(80, 105)
#Triangles stand for fully infused datapoints.
s2.circle(DE[:,0], DE[:,2], size=10, color="firebrick", alpha=0.5)
#Circles stand for failed infusions.
#s2.triangle(X3[:,0],X3[:,pofi],size=10, color="navy", alpha =0.5,legend="validation data")

#s2.circle(X[:,0],y, color="orange", alpha =0.5,legend="teaching data")
s2.xaxis.axis_label = "spools"
s2.yaxis.axis_label = 'no_layers'
s2.legend.location = "top_right"
#Create third plot
s3 = figure(plot_width=500, plot_height=500)
#s2.x_range=Range1d(250, 500)
#s2.y_range=Range1d(80, 105)
#Triangles stand for fully infused datapoints.
s3.triangle(DE[:,1], DE[:,2], size=10, color="firebrick", alpha=0.5)
#s3.circle(X3[:,1], X3[:,0], size=errn[:,0], color="navy", alpha=0.5,fill_color="white", line_width=3)

#Circles stand for failed infusions.
#s3.circle(X3[:,2],X3[:,4], color="green", alpha =0.5,legend="source data")
s3.xaxis.axis_label = "mandrel_speed"
s3.yaxis.axis_label = "no_layers"
#s3.legend.location = "top_right"


#Triangles stand for fully infused datapoints.
s4 = figure(title="1",plot_width=500, plot_height=500)
s4.circle( DE[:,0], DE[:,3], size=10, color="firebrick", alpha=0.5)
#s4.triangle(X3[:,2],X3[:,pofi], size=10, color="navy", alpha=0.5,legend="validation data")
#s4.circle(X[:,1],y, color="orange", alpha =0.5,legend="teaching data")
s4.xaxis.axis_label = "spools"
s4.yaxis.axis_label = 'fitness'
#show(row(s1, s2))


s5 = figure(plot_width=500, plot_height=500)
#s2.x_range=Range1d(250, 500)
#s2.y_range=Range1d(80, 105)
#Triangles stand for fully infused datapoints.
s5.triangle(DE[:,1], DE[:,3], size=10, color="firebrick", alpha=0.5)
#s5.circle(X3[:,1], X3[:,2], size=errn[:,0], color="navy", alpha=0.5,fill_color="white", line_width=3)

#Circles stand for failed infusions.
#s3.circle(X3[:,2],X3[:,4], color="green", alpha =0.5,legend="source data")
s5.xaxis.axis_label = "mandrel_speed"
s5.yaxis.axis_label = "fitness"
#s3.legend.location = "top_righ


s6 = figure(plot_width=500, plot_height=500)
#s2.x_range=Range1d(250, 500)
#s2.y_range=Range1d(80, 105)
#Triangles stand for fully infused datapoints.
s6.triangle(DE[:,2], DE[:,3], size=10, color="firebrick", alpha=0.5)
#s6.circle(X3[:,0], X3[:,2], size=errn[:,0], color="navy", alpha=0.5,fill_color="white", line_width=3)

#Circles stand for failed infusions.
#s3.circle(X3[:,2],X3[:,4], color="green", alpha =0.5,legend="source data")
s6.xaxis.axis_label = "no_layers"
s6.yaxis.axis_label = "fitness"
#s3.legend.location = "top_righ
show(row(s1,s2,s3,s4,s5,s6))