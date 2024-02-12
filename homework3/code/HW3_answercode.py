# Homework 3 code -- Dylan Brewer
# Homework 3 is continued below the code from homework 2

# Clear all
from IPython import get_ipython
get_ipython().magic('reset -sf')

# Import packages
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

# Set working directories and seed
datapath = r'C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework2'
outputpath2 = r'C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework3\output'

os.chdir(datapath)

random.seed(65377037781)
np.random.seed(480971)

# Import homework data
kwh = pd.read_csv('kwh.csv')

# Question 1 ------------------------------------------------------------------

## These will be referenced later
varlist = ['electricity', 'sqft', 'temp']

os.chdir(outputpath2)

# Question 1

## Set up a few things we will need
Yvar = kwh['electricity'].to_numpy()
nobsa, = Yvar.shape
constant = np.ones((nobsa,1)) # Vector of ones for the constant

Xvar = kwh.drop('electricity',axis = 1).to_numpy()
Xvar = np.concatenate([constant,Xvar],axis = 1) # Add the constant


## Define logged variables
Xvar4 = kwh.drop('electricity',axis = 1).to_numpy()
Xvar4 = np.concatenate([constant,Xvar4],axis = 1)
Xvar4[:,1] = np.log(Xvar4[:,1])
Xvar4[:,3] = np.log(Xvar4[:,3])

Yvar4 = np.log(Yvar)

## Perform OLS estimation to get parameters.
olsbeta4 = np.matmul(np.linalg.inv((np.matmul(Xvar4.T, Xvar4))), np.matmul(Xvar4.T, Yvar4))
nobs4, = np.shape(Yvar4)

## Calculate the mean marginal effects
mfxraw = np.zeros((nobs4,4))
mfxraw[:,1] = olsbeta4[1]*Yvar*(Xvar[:,1]**(-1)) # sq ft
mfxraw[:,3] = olsbeta4[3]*Yvar*(Xvar[:,3]**(-1)) # temp
delta = np.exp(olsbeta4[2]) # Note the estimate is ln(delta), so get delta here
mfxraw[:,2] = ((delta-1)*Yvar)*((delta**Xvar[:,2])**(-1))
mfx4 = np.mean(mfxraw,axis = 0)

## Bootstrap confidence intervals
### Set boostrap replications
breps = 1000

### Initialize outputs
olsbeta4blist = np.zeros((breps,4)) # Contains one row for each replication
mfx4blist = np.zeros((breps,4))

### Get an index of the data we will sample
bidx = np.random.choice(nobs4,(nobs4,breps))

### Sample with replacement to the size of the sample
for r in range(breps):
    ### Sample the data
    Yvar4b = np.zeros((nobs4,1)) # Clears out the data each run
    Xvar4b = np.zeros((nobs4,4))
    Yvarb = np.zeros((nobs4,1))
    Xvarb = np.zeros((nobs4,4))
    for n in range(nobs4):
        Yvar4b[n] = Yvar4[bidx[n,r]]
        Xvar4b[n,:] = Xvar4[bidx[n,r],:]
        Yvarb[n] = Yvar[bidx[n,r]]
        Xvarb[n,:] = Xvar[bidx[n,r],:]
        
    Yvar4b = np.reshape(Yvar4b,-1) # To 1d array for later conformability
    Yvarb = np.reshape(Yvarb,-1)
    
    ### Perform the estimation
    olsbeta4blist[r,:] = np.matmul(np.linalg.inv((np.matmul(Xvar4b.T, Xvar4b))), np.matmul(Xvar4b.T, Yvar4b)).T
    
    ### Get the average marginal effect
    mfxrawb = np.zeros((nobs4,4))
    mfxrawb[:,1] = olsbeta4blist[r,1]*Yvarb*(Xvarb[:,1]**(-1)) # sq ft
    mfxrawb[:,3] = olsbeta4blist[r,3]*Yvarb*(Xvarb[:,3]**(-1)) # temp
    deltab = np.exp(olsbeta4blist[r,2]) # Note the estimate is ln(delta), so get delta here
    mfxrawb[:,2] = ((deltab-1)*Yvarb)*((deltab**Xvarb[:,2])**(-1))
    mfx4blist[r,:] = np.mean(mfxrawb,axis = 0)
    
### Extract 2.5th and 97.5th percentile
lb4 = np.percentile(olsbeta4blist,2.5,axis = 0,interpolation = 'lower')
ub4 = np.percentile(olsbeta4blist,97.5,axis = 0,interpolation = 'higher')

lbmfx4 = np.percentile(mfx4blist,2.5,axis = 0,interpolation = 'lower')
ubmfx4 = np.percentile(mfx4blist,97.5,axis = 0,interpolation = 'higher')

## Build output table
### Reorder output (I probably should figure out a way to do this all at once)
order = np.array([2,1,3,0])
lb4 = lb4[order]
ub4 = ub4[order]
olsbeta4 = olsbeta4[order]
lbmfx4 = lbmfx4[order]
ubmfx4 = ubmfx4[order]
mfx4 = mfx4[order]

### Row and column names
rownames4 = pd.concat([pd.Series(['retrofit', 'ln(sqft)', 'ln(temp)', 'Constant', 'Observations']),pd.Series([' ',' ',' ',' ',])],axis = 1).stack()
colnames4 = pd.Series(['Coefficients','Marginal effects (dy/dx)'])

### Format confidence intervals
lb4 = pd.Series(np.round(lb4,2)) # Rounds to two decimal places and puts into a Series
ub4 = pd.Series(np.round(ub4,2))
lbmfx4 = pd.Series(np.round(lbmfx4,2))
ubmfx4 = pd.Series(np.round(ubmfx4,2))

ci4 = '(' + lb4.map(str) + ', ' + ub4.map(str) + ')'
cimfx4 = '(' + lbmfx4.map(str) + ', ' + ubmfx4.map(str) + ')'
cimfx4.iloc[3] = ' ' # There is probably a better way to do this

### Format estimates and append observations
olsbeta4 = pd.Series(np.append(np.round(olsbeta4,2),nobs4))
mfx4 = pd.Series(np.append(np.round(mfx4,2),nobs4))
mfx4.iloc[3] = ' ' # There is probably a better way to do this

### Stack estimates over confidence intervals
col40 = pd.concat([olsbeta4,ci4],axis = 1).stack()
col41 = pd.concat([mfx4,cimfx4],axis = 1).stack()

### Output
outputtable4 = pd.concat([col40,col41],axis = 1)
outputtable4.index = rownames4
outputtable4.columns = colnames4


print(outputtable4)

outputtable4.to_latex('outputtable4.tex',float_format="%.2f")

## Build plot
lowbar = np.array(mfx4[1:3] - lbmfx4[1:3])
highbar = np.array(ubmfx4[1:3] - mfx4[1:3])

plt.errorbar(y = mfx4[1:3], x = np.arange(2), yerr = [lowbar,highbar], fmt= 'o', capsize = 5)
plt.ylabel('KWh')
plt.xticks(np.arange(2),['Sq ft', 'Temperature'])
plt.xlim((-0.5,1.5)) # Scales the figure more nicely
plt.axhline(linewidth=2, color='r')
plt.savefig('mfx.pdf',format='pdf')
plt.show()