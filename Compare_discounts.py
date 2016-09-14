import time
import math
import pandas as pd
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt  
import os
from scipy import interpolate as interp
import my_library as my
reload(my) ## reloads my_library to include eventual changes in the file




#########################  PLOT OF THE AVERAGED MONTH
def Plot_confront(save_name,title,x,y1,y2,y0,erry1,erry2,erry0):
    my.NaN_toZero(y1) ##converts NaNs to zeros for the plots
    my.NaN_toZero(y2) ##converts NaNs to zeros for the plots    
    y_max=np.amax([np.amax(y1),np.amax(y2)])
    x_max=np.amax(x)
    x_min=np.amin(x)
    plt.clf()
    plt.plot(x,y1,'bo',label='%s_50pound'%title)  ##MONTH
    plt.errorbar(x,y1,xerr=0,yerr=erry1,ecolor='g',fmt='o',label='error 50pounds')
    plt.plot(x,y2,'ro',label='%s_70pounds'%title)  ##MONTH
    plt.errorbar(x,y2,xerr=0,yerr=erry2,ecolor='g',fmt='o',label='error 70pounds')
    axes = plt.gca()                  ##set axis range
    axes.set_xlim([x_min-1,x_max+1])
    axes.set_ylim([0,1.3*y_max])
    axes.grid(True)
    plt.locator_params(axis='x',nbins=10)
    plt.title(title)
    plt.xlabel('Hours of the day')
    tck1 = interp.splrep(x, y1, s=0) #----- smooth lines (interpolation); s is the parameter that regulates the smoothness 
    tck2 = interp.splrep(x, y2, s=0) #----- smooth lines (interpolation); s is the parameter that regulates the smoothness 
    xnew = np.linspace(0,24,2000)  ## range of the spline
    line_smooth1 = interp.splev(xnew, tck1, der=0)
    line_smooth2 = interp.splev(xnew, tck2, der=0)
    plt.plot(xnew,line_smooth1,'b',lw=2) #----- end smooth lines
    plt.plot(xnew,line_smooth2,'r',lw=2) #----- end smooth lines
    
    #plt.plot(x,y0,'ko',label='%s_0pound'%title)  ##Incluse also data with discount =0
    #plt.errorbar(x,y0,xerr=0,yerr=erry0,ecolor='k',fmt='o',label='error 0pounds')
    #tck0 = interp.splrep(x, y0, s=0) #----- smooth lines (interpolation); s is the parameter that regulates the smoothness 
    #line_smooth0 = interp.splev(xnew, tck0, der=0)
    #plt.plot(xnew,line_smooth0,'k',lw=2) #----- end smooth lines
  
    handles, labels = plt.gca().get_legend_handles_labels() #------- prevents duplication of labels (comnig from the plot of 'Sunday')
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=(0., .85, 1., .102), loc=3,ncol=2, mode="expand", borderaxespad=0.)  
    plt.show()
    plt.savefig(save_name)





def Avgs_byHour(dat):
    ncols_perday=7
    #print dat
    hours=dat.as_matrix()[1:,0].astype(int)
    quotes=dat.as_matrix()[1:,1::ncols_perday].astype(float)
    tops=dat.as_matrix()[1:,2::ncols_perday].astype(float)
    tops1=dat.as_matrix()[1:,3::ncols_perday].astype(float)
    tops2=dat.as_matrix()[1:,4::ncols_perday].astype(float)
    clicks=dat.as_matrix()[1:,5::ncols_perday].astype(float)
    sales=dat.as_matrix()[1:,6::ncols_perday].astype(float)    
    Xavg=[]  ## Saves averages and errors in an array
    Xavg.append(np.mean(quotes,axis=1))
    Xavg.append(np.mean(tops,axis=1))
    Xavg.append(np.mean(tops1,axis=1))
    Xavg.append(np.mean(tops2,axis=1))
    Xavg.append(np.mean(clicks,axis=1))
    Xavg.append(np.mean(sales,axis=1))
    Xerr=[]
    Xerr.append(np.std(quotes,axis=1)/math.sqrt(len(quotes[0,:]-1)))
    Xerr.append(np.std(tops,axis=1)/math.sqrt(len(quotes[0,:]-1)))
    Xerr.append(np.std(tops1,axis=1)/math.sqrt(len(quotes[0,:]-1)))
    Xerr.append(np.std(tops2,axis=1)/math.sqrt(len(quotes[0,:]-1)))
    Xerr.append(np.std(clicks,axis=1)/math.sqrt(len(quotes[0,:]-1)))
    Xerr.append(np.std(sales,axis=1)/math.sqrt(len(quotes[0,:]-1)))    
    return Xavg,Xerr   


Rulename='CWM' 
folderName='C:\Users\lbongiovanni\Desktop\Projects//Xdiscount_before2pm'
if not os.path.exists(folderName):
    os.makedirs(folderName)
    
filename1=folderName+'//50pounds//%s//%s_QTCavgbyHour_50pounds.xlsx'%(Rulename,Rulename)
filename2=folderName+'//70pounds//%s//%s_QTCavgbyHour_70pounds.xlsx'%(Rulename,Rulename)
filename0=folderName+'//0pounds//%s//%s_QTCavgbyHour_0pounds.xlsx'%(Rulename,Rulename)

data0=my.read_fromExcel(filename0)
X0_avg,X0_err=Avgs_byHour(dat=data0)



data1=my.read_fromExcel(filename0)   ##reads data from the excel fileprint data
data2=my.read_fromExcel(filename2)


X1_avg,X1_err=Avgs_byHour(dat=data1)
X2_avg,X2_err=Avgs_byHour(dat=data2)

dirPlot=folderName+"//Plots_confront"
if not os.path.exists(dirPlot): ### Create Plot directory if doesn't exists already
    os.makedirs(dirPlot)
title_set=['Quotes','Tops','Tops1','Tops2','Clicks','Sales']
Ncol=len(title_set)
x=range(0,24)
for i in range(Ncol):
    title=title_set[i]  ###Plot monthly avgs 
    save_string=dirPlot+'//%s_compare_%s_disc_0-70.png'%(Rulename,title)
    
    y1=X1_avg[i]
    erry1=X1_err[i]
    y2=X2_avg[i]
    erry2=X2_err[i]
    y0=X0_avg[i]
    erry0=X0_err[i]
    
    Plot_confront(save_string,title,x,y1,y2,y0,erry1,erry2,erry0) ##plot of the avg on the month