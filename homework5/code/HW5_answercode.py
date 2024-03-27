# Homework 5 code -- Dylan Brewer

# Clear all
from IPython import get_ipython
get_ipython().magic('reset -sf')

# Import packages
import os
import numpy as np
import pandas as pd
import random
import statsmodels.api as sm
from linearmodels.iv import IVGMM

# Set working directories and seed
datapath = r'C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework5'
outputpath = r'C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework5\output'

os.chdir(datapath)

random.seed(96333)
np.random.seed(5659)

# Import homework data
data = pd.read_csv('instrumentalvehicles.csv')

# Question 1 -----------------------------------------------------------------
yvar = data['price']
xvar = data[['mpg','car']]

ols1 = sm.OLS(yvar,sm.add_constant(xvar)).fit()
print(ols1.summary())

# Question 2 -----------------------------------------------------------------
yvar2_1 = yvar
yvar2_2 = xvar['mpg']
xvar2 = xvar['car']
zvara = data['weight']
zvarb = data['weight']**2
zvarc = data['height']

## Part a
### First stage
stage1a = sm.OLS(yvar2_2,sm.add_constant(pd.concat([xvar2,zvara],axis = 1),prepend = False)).fit()
fstata = stage1a.tvalues.loc['weight']**2
ytildea = stage1a.predict(sm.add_constant(pd.concat([xvar2,zvara],axis = 1),prepend = False))

### Second stage
stage2a = sm.OLS(yvar2_1,sm.add_constant(pd.concat([xvar2,ytildea],axis = 1),prepend = False)).fit()
betasa = np.round(stage2a.params,2)
cia = pd.DataFrame(np.round(stage2a.conf_int(),2))
nobsa = int(stage2a.nobs)

## Part b
### First stage
stage1b = sm.OLS(yvar2_2,sm.add_constant(pd.concat([xvar2,zvarb],axis = 1),prepend = False)).fit()
fstatb = stage1b.tvalues.loc['weight']**2
ytildeb = stage1b.predict(sm.add_constant(pd.concat([xvar2,zvarb],axis = 1),prepend = False))

### Second stage
stage2b = sm.OLS(yvar2_1,sm.add_constant(pd.concat([xvar2,ytildeb],axis = 1),prepend = False)).fit()
betasb = np.round(stage2b.params,2)
cib = pd.DataFrame(np.round(stage2b.conf_int(),2))
nobsb = int(stage2b.nobs)

## Part c
### First stage
stage1c = sm.OLS(yvar2_2,sm.add_constant(pd.concat([xvar2,zvarc],axis = 1),prepend = False)).fit()
fstatc = stage1c.tvalues.loc['height']**2
ytildec = stage1c.predict(sm.add_constant(pd.concat([xvar2,zvarc],axis = 1),prepend = False))

### Second stage
stage2c = sm.OLS(yvar2_1,sm.add_constant(pd.concat([xvar2,ytildec],axis = 1),prepend = False)).fit()
betasc = np.round(stage2c.params,2)
cic = pd.DataFrame(np.round(stage2c.conf_int(),2))
nobsc = int(stage2c.nobs)

## Export
### Format confidence intervals
cia_s = '(' + cia.loc[:,0].map(str) + ', ' + cia.loc[:,1].map(str) + ')'
cib_s = '(' + cib.loc[:,0].map(str) + ', ' + cib.loc[:,1].map(str) + ')' 
cic_s = '(' + cic.loc[:,0].map(str) + ', ' + cic.loc[:,1].map(str) + ')'

### Build table
outputa = pd.DataFrame(pd.concat([pd.Series(betasa),cia_s],axis = 1).stack())
outputb = pd.DataFrame(pd.concat([pd.Series(betasb),cib_s],axis = 1).stack())
outputc = pd.DataFrame(pd.concat([pd.Series(betasc),cic_s],axis = 1).stack())

hw5output3 = pd.concat([outputa,outputb,outputc],axis = 1)
hw5output3.columns = ['(a)','(b)','(c)']
hw5output3.index = ['Sedan',' ','MPG','','Constant','']
hw5output3 = pd.concat([hw5output3,pd.DataFrame([[str(nobsa),str(nobsb),str(nobsc)], [fstata,fstatb,fstatc]], index = ['Observations', 'First stage F'], columns = ['(a)', '(b)','(c)'])])


os.chdir(outputpath)
hw5output3.to_latex('hw5output3.tex',column_format = 'lccc', na_rep = ' ')

# Question 4 -----------------------------------------------------------------
#tsls4 = sm.sandbox.regression.gmm.IV2SLS(yvar2_1,xvar2,yvar2_2 = [xvar2, zvara]).fit()

results4 = IVGMM.from_formula('price ~ 1 + car + [mpg ~ weight]',data).fit() # This is a nice function and nice way to write the regression

print(results4)