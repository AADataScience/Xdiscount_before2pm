# -*- coding: utf-8 -*-
import time
import math
import pyodbc
import pandas as pd
import numpy as np
from collections import OrderedDict
import matplotlib.pyplot as plt  
import os
from scipy import interpolate as interp
import sys
sys.path.append('C:\Users\lbongiovanni\Desktop\Python_my_libs')
import my_library as my
reload(my) ## reloads my_library to include eventual changes in the file



#########################  PLOT OF THE AVERAGED MONTH
def Plot_singlePlot(save_name,title,x,y,erry):
    NaN_toZero(y) ##converts NaNs to zeros for the plots
    y_max=np.amax(y)
    x_max=np.amax(x)
    x_min=np.amin(x)
    plt.clf()
    plt.plot(x,y,'ro',label=title)  ##MONTH
    plt.errorbar(x,y,xerr=0,yerr=erry,ecolor='r',fmt='o',label='error')
    handles, labels = plt.gca().get_legend_handles_labels() #------- prevents duplication of labels (comnig from the plot of 'Sunday')
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(),bbox_to_anchor=(0., .93, 1., .102), loc=3,ncol=2, mode="expand", borderaxespad=0.)
    axes = plt.gca()                  ##set axis range
    axes.set_xlim([x_min-1,x_max+1])
    axes.set_ylim([0,1.2*y_max])
    axes.grid(True)
    plt.locator_params(axis='x',nbins=10)
    plt.title(title)
    plt.xlabel('Hours of the day')
    tck = interp.splrep(x, y, s=0) #----- smooth lines (interpolation); s is the parameter that regulates the smoothness 
    xnew = np.linspace(0,24,2000)  ## range of the spline
    line_smooth = interp.splev(xnew, tck, der=0)
    plt.plot(xnew,line_smooth,'b') #----- end smooth lines
    plt.savefig(save_name)
    plt.show()



################ SUBPLOTS OF THE 4 WEEKS 
def Plot_subPlots(save_name,title,NSubs,x,y,erry):
    j=0
    fig, arr= plt.subplots(NSubs,NSubs)
    x_max=np.amax(x)
    x_min=np.amin(x)
    for i in range(2):  ##2x2 index for subplots
        for n in range(2):
            NaN_toZero(y[j,:]) ##converts NaNs to zeros for the plots
            y_max=np.amax(y[j,:])
            title_subpls=title+' %s'%j
            arr[i,n].plot(x,y[j,:],'ro-',label=title) ## WEEKS
            arr[i,n].errorbar(x,y[j,:],xerr=0,yerr=erry[j,:],ecolor='r',label='error')
            arr[i,n].set_title(title_subpls)
            arr[i,n].set_ylim([0,1.2*y_max])
            arr[i,n].set_xlim([x_min-1,x_max+1])
            arr[i,n].set_xlabel('Hours of the day')
            j+=1  ## flat index for array
    plt.setp([a.get_xticklabels() for a in arr[0, :]], visible=False)
    plt.setp([a.get_yticklabels() for a in arr[:, 1]], visible=False)
    fig.tight_layout()  ## automatically adjusts space between subplots
    #plt.show()
    plt.savefig(save_name)



def fill_24hours(x,Ncol):
    if (len(x)>0): ##means it's not a weekend
        x=np.array(x)
        x24=np.zeros((24,Ncol))
        for i in range(24):x24[i,0]=i ##inizialize an array with 24 hrs and zeros for each entry at each hour
        j=0
        for i in range(24):
            if(j<len(x) and i==int(x[j,0])): ## otherwise after the last element of x, j+1 will become too big and x[j,:] will trow an error
                    x24[i]=x[j,:]  ##when the hour in x matches the hour of the day the data get copied from x
                    j+=1
    else : ##weekends empty 
        x24=np.zeros((24,Ncol))
        for i in range(24):x24[i,0]=i ##inizialize an array with 24 hrs and zeros for each entry at each hour
        
    return x24

def join_data(data1,data2):
    if(len(data1)!=len(data2)): print 'Warning! data1 and data2 have different lenghts!'
    data=[]
    Ncol1=len(data1[0][0,:])
    Ncol2=len(data2[0][0,:])
    
    for i in range(len(data1)):
        x=fill_24hours(data1[i],Ncol1)
        y=fill_24hours(data2[i],Ncol2)
        data.append(np.delete(np.hstack((x,y)),Ncol1,axis=1)) #The first column of Sales (col position =Ncol1) has to be deleted
    return data
    

def load_SQLdata(conn_string,sql_select,Rule,start,end): 
    cnxn = pyodbc.connect(conn_string)
    x=[]
    i=0
    for day in range (start,end) :
        dayName=my.load_SQLdata('OGI',sql_dayName_OGI%day,Time=False) ## gets the name of the day corresponding to the dayoftheyear
        #print dayName.iloc[0,0]
        if(dayName.iloc[0,0]!='Saturday' and dayName.iloc[0,0]!='Sunday' ): ## only runs SQL for weekdays!
            x.append(pd.DataFrame())
            sql_query=sql_select % (day)
            start = time.clock()
            x[i]=pd.read_sql_query(sql_query,cnxn)  ##load the informations for the day in the pd.Dataframe data_day
            x[i]=x[i].values ## numpy representation of pandas DataFrame
            stop = time.clock()
            print 'time the for executing day %d : %.6f secs' % (day,stop-start)
            i+=1
    cnxn.close()     #<--- Close the connection
    return x

def load_OgiRefs(conn_string,sql_query):
    cnxn = pyodbc.connect(conn_string)
    x=pd.DataFrame()
    x=pd.read_sql_query(sql_query,cnxn)
    arr=x.as_matrix()
    Salses_Refs="'"
    for i in range(len(arr)-1) : Salses_Refs+=arr[i,0]+"','"
    Salses_Refs+=arr[len(arr)-1,0]+"'"
    cnxn.close()     #<--- Close the connection
    return Salses_Refs
        
        
### WRITE DATA TO EXCEL FILE     
def write_toExcel(dates,data,filename) : 
    cols_per_day=len(data[0][0,:])
    Ndays=len(dates) ## number of WEEKDAYS considered
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')  # Create a Pandas Excel writer using XlsxWriter as the engine.
    header=['hour','Quotes','Tops','Tops1','Tops2','Clicks','Sales']
    if(len(header)!=cols_per_day):print "ERROR in 'write_toExcel'! : the number of headers is not the same as the columns you are trying to write on the file!"
    for day in range (Ndays) :
        x=pd.DataFrame(columns=header)
        if(len(dates[day])>0) : x.loc[0]=dates[day][0,:]
        else : x.loc[0]=[0]*cols_per_day
        #print data[day]
        for i in range(len(data[day])):x.loc[i+1]=data[day][i,:]
        x.to_excel(writer, sheet_name='Sheet1',startcol=cols_per_day*day, header=True,index=False)    ##saves the DataFrames in an Excel file, each new query is written under the previous one (startrow=4*i)
    writer.save() # Close the Pandas Excel writer and output the Excel file.


### READ FROM EXCEL FILE  
def read_fromExcel(filename):
    start = time.clock()
    tab = pd.read_excel(filename,header = None,index_col = None,convert_float=True)
    stop = time.clock()
    print 'time the for importing data from Excell : %.2f secs' % (stop-start)
    #tab=tab.as_matrix()
    return tab



## removes NaNs from the array
def rmv_NaN(x):
    indx=[]
    for i in range(len(x)):
        if(str(x[i])=='nan'):indx.append(i) 
    x=np.delete(x,indx)
    return x

def rmv_inf(x):
    indx=[]
    for i in range(len(x)):
        if(str(x[i])=='inf'):indx.append(i) 
    x=np.delete(x,indx)
    return x


# find Mondays in the file :
def find_wkends(x,Nvar,Ndays):
    mon=[]
    sat=[]
    sun=[]
    for i in range(Ndays):
        if(str(x[1,Nvar*i])=='Monday'): mon.append(i)
        if(str(x[1,Nvar*i])=='Saturday'): sat.append(i)        
    sun=[i+1 for i in sat]
    return (sat,sun,mon)


##removes 0s from array (usefull when doing averages and wanting the weekends out)
def rmv_wkends(sat,sun,N,x):
    indx=[]
    sat1=[i*N for i in sat]
    sun1=[i*N for i in sun]
    for i in range(len(sat1)):
        for j in range(N): indx.append(sat1[i]+j) ## removes all the Nvar columns of Saturday
    for i in range(len(sun1)):
        for j in range(N): indx.append(sun1[i]+j) ## removes all the Nvar columns of Saturday
    return np.delete(x,indx,axis=1)
    
## replace NaNs in the array with 0
def NaN_toZero(x):
    for i in range(len(x)):
        if(str(x[i])=='nan'):x[i]=0 
    return x

## Jackknife (since we don't know the distribution of the datas, the only way to define an error is to use resampling. For the Central Limit Theorem the means of the resampled samples are distributed as a gaussian around the real mean of the distribution, therefore it is possible to define a variance )
def Jackknife(x):
    x=rmv_inf(x)  ##removes infinites
    x=rmv_NaN(x)
    if(len(x)>0):  ## case in which x is not all nan or infinities
        N=len(x)      ## resampling on the sample withouth infinites
        x_Jack=[]
        Sum=0
        for i in range(N):Sum+=x[i]
        for i in range(N): x_Jack.append((Sum-x[i])/float(N-1))
        x_avg=np.nanmean(x)
        var_Jack=0
        for i in range(N): var_Jack+=(x_avg-x_Jack[i])*(x_avg-x_Jack[i])
        err_Jack=math.sqrt(var_Jack*(N-1)/float(N))
    else : 
        x_avg=0
        err_Jack=0
    return (x_avg,err_Jack)
    
def avg_ratio(x,y):
    x2=[i*i for i in x]
    x2_avg=np.nanmean(x2)
    x_avg=np.nanmean(x)
    y_avg=np.nanmean(y)
    N=len(x)
    Ny=len(y)
    if(N!=Ny): print 'Warning! x and y have different lengths! length of x will be used'
    var_x=0
    var_y=0
    cov=0
    cov_xxy=0
    for i in range(N): 
        var_x+=(x_avg-x[i])*(x_avg-x[i]) ## variance of x
        var_y+=(y_avg-y[i])*(y_avg-y[i]) ## variance of y
        cov+=(x_avg-x[i])*(y_avg-y[i])   ## covariance of x and y
        cov_xxy+=(x2_avg-x[i]*x[i])*(y_avg-y[i]) ## covariance of x^2 and y
    var_x=var_x/float(N)
    var_y/var_y/float(N)
    cov=cov/float(N)
    cov_xxy=cov_xxy/float(N)
    r=x_avg/y_avg
    var_ratio=(x_avg/y_avg)*(x_avg/y_avg)*(var_x/(x_avg*x_avg)+var_y/(y_avg*y_avg)-cov/(x_avg*y_avg)) ## Estimation of variance of the Ratio (simply the propagation of the error)! for reference see http://stats.stackexchange.com/questions/19576/variance-of-the-reciprocal-ii/19580#19580 
    err_ratio=math.sqrt(var_ratio/(N-1))
    r_correct=r*(1+1/float(N)*(1/x_avg-cov/(x_avg*y_avg))+1/float(N*N)*(2/(x_avg*x_avg)-cov/(x_avg*y_avg)*(2+3/x_avg)+cov_xxy/(x_avg*x_avg*y_avg))) #secon order estimator for the correction to the biased E(x)/E(y) (see : https://en.wikipedia.org/wiki/Ratio_estimator)
    return (r_correct,err_ratio)
    
def Avgs_byHour(dat):
    ncols_perday=7
    #print dat
    #hours=dat.as_matrix()[2:,0].astype(int)
    quotes=dat.as_matrix()[2:,1::ncols_perday].astype(float)
    tops=dat.as_matrix()[2:,2::ncols_perday].astype(float)
    tops1=dat.as_matrix()[2:,3::ncols_perday].astype(float)
    tops2=dat.as_matrix()[2:,4::ncols_perday].astype(float)
    clicks=dat.as_matrix()[2:,5::ncols_perday].astype(float)
    sales=dat.as_matrix()[2:,6::ncols_perday].astype(float)    
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
    
    

##########################------------------------ MAIN ---------------------################################
#### Connection Strings
conn_string_QWD='DRIVER={SQL Server};SERVER=217.10.152.6;DATABASE=Riskdata;UID=iymqdw;PWD=cDfBn8DDaVW8hvst'
conn_string_OGI='DRIVER={SQL Server};SERVER=10.33.23.247;DATABASE=OpenGi;UID=ReportsUser;PWD=reportuser'



#### SQL select Queries
### sql_date just attach the date as the first row of data 
sql_dayName_OGI = "select top 1\
                    DATENAME(dw,Reqdate)\
                    from ic_BD_PRIC with (nolock)\
                    where datepart(dayofyear,Reqdate)=%d "
sql_dateOGI= " select top 1\
                DATENAME(dw,Reqdate) as 'hour',\
                datepart(day,Reqdate) as 'Quotes',\
                DATENAME(month,Reqdate) as 'Tops',\
                datepart(dayofyear,Reqdate) as 'Tops1',\
                'Tops2',\
                'Clicks',\
                'end day'\
		from ic_BD_PRIC with (nolock)\
		where datepart(dayofyear,Reqdate)=%d\
		"
					
sql_QWD=" select \
                cast(datepart(hour,QuoteRequestTime) as varchar) as 'hour',                                                         \
                count(*) as 'Quotes',                         \
                cast(sum(case when TopPosition is not null then 1 else 0 end) as varchar) as 'Tops' , \
                cast(sum(case when TopPosition=1 then 1 else 0 end) as varchar) as 'Top1' , \
                cast(sum(case when TopPosition=2 then 1 else 0 end) as varchar) as 'Top2',\
                count(ClickedThrough) as 'Clicks'                                                     \
                from RiskData with (nolock)                                                                        \
                where Source in ('CTM','MSM','CONF','GOCO')\
                      and FinalPremium>0\
                      and Brand in ('IYM','4YD')\
                      and datepart(dayofyear,QuoteRequestTime)=%d \
                      and DATENAME(dw,QuoteRequestTime) not in ('Saturday','Sunday') \
                group by datepart(hour,QuoteRequestTime) "
#and Insurer='%s'\

sql_OGI=" select \
               datepart(hour,Reqtime),\
               count(*)\
               from icp_BD_PRIC with (nolock) \
	       where Finprem>0\
		     and datepart(dayofyear,Reqdate)=%d \
		     and Source in ('CTM','GOCO','CONF','MSM')\
		     and Brand in ('IYM','4YD')\
		     and DATENAME(dw,Reqdate) not in ('Saturday','Sunday') \
                group by datepart(hour,Reqtime) " 
                
                
                
Rulename='CWM'     
discount='70pounds'
folderName='C:\Users\lbongiovanni\Desktop\Projects//Xdiscount_before2pm//%s//%s'%(discount,Rulename)
if not os.path.exists(folderName):
    os.makedirs(folderName)
filename=folderName+'//%s_QTCavgbyHour_%s.xlsx'%(Rulename,discount)


## 0£ :  6Jun-1Jul (day 156-184);    50£ : 18Jul-12Aug (day 200-225);  70£ : 19Aug-8Sept (day 232-252)

FirstDay=232  
LastDay=252    
LastDay=LastDay+1 #This is to include the last day in the analysis, otherwise it will stop at LastDay-1
day_period=LastDay-FirstDay




## run sql queries
data_dates=load_SQLdata(conn_string_OGI,sql_dateOGI,Rulename,FirstDay,LastDay) ##loads the date of the day from the sql database
data_salesOGI=load_SQLdata(conn_string_OGI,sql_OGI,Rulename,FirstDay,LastDay) ##loads sales from OGI divided by hour per day
data_QWD=load_SQLdata(conn_string_QWD,sql_QWD,Rulename,FirstDay,LastDay) ## loads 
##write joined data (quotes+sales each day by hour) on file
data_matrix=join_data(data_QWD,data_salesOGI) ## creates a table with columns : Hour,Quotes,Tops,Clicks,Sales for each day
write_toExcel(data_dates,data_matrix,filename) ## writes table on excell file


data=read_fromExcel(filename)   ##reads data from the excel fileprint data



X_avg,X_err=Avgs_byHour(dat=data)

#print quotes
#print X_avg[2],X_err[2]


dirPlot=folderName+'//Plots'
if not os.path.exists(dirPlot): ### Create Plot directory if doesn't exists already
    os.makedirs(dirPlot)
title_set=['Quotes','Tops','Top1','Top2','Clicks','Sales']
for i in range(6):
    #print 'printed : %s'%title_set[i]
    #title='Week_avg'+title_set[i] ###Plot 4 weekly avgs 
    #save_string=dirPlot+'//%s.png'%title
    #N_subplots=2
    x=range(0,24)
    #y=X_wk[i]
    #erry=Xerr_wk[i]
    #Plot_subPlots(save_string,title,N_subplots,x,y,erry) ##subplot 2X2 of the weeks
    #print len(X_avg[i])
    title='%s (19Aug-8Sept) '%discount+title_set[i]  ###Plot monthly avgs 
    save_string=dirPlot+'//%s_%s.png'%(discount,title_set[i])
    y=X_avg[i]
    erry=X_err[i]
    Plot_singlePlot(save_string,title,x,y,erry) ##plot of the avg on the month





















