# Homework 2 code -- Dylan Brewer

# Clear all
from IPython import get_ipython
get_ipython().magic('reset -sf')

# Import packages
import os
import numpy as np
import pandas as pd
import scipy.stats as sc
import scipy.optimize as opt
import matplotlib.pyplot as plt
import seaborn as sns
import random
import statsmodels.api as sm

# Set working directories and seed
datapath = r'C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework2'
outputpath = r'C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework2\output'

os.chdir(datapath)

random.seed(65377037781)
np.random.seed(480971)

# Import homework data
kwh = pd.read_csv('kwh.csv')

# Question 1 ------------------------------------------------------------------

## These will be referenced later
varlist = ['electricity', 'sqft', 'temp']

## Get means
mean0 = kwh[ kwh[ 'retrofit' ] == 0 ].mean().drop('retrofit')
mean1 = kwh[ kwh[ 'retrofit' ] == 1 ].mean().drop('retrofit')

## Get difference in means
diff = mean0-mean1

## Get standard deviations
sd0 = kwh[ kwh[ 'retrofit' ] == 0 ].std().drop('retrofit')
sd1 = kwh[ kwh[ 'retrofit' ] == 1 ].std().drop('retrofit')

## Perform difference in means test
tval, pval = sc.ttest_ind(kwh[ kwh[ 'retrofit' ] == 0 ].drop('retrofit',axis=1) , kwh[ kwh[ 'retrofit' ] == 1 ].drop('retrofit',axis=1) , equal_var = False) # Get p value
pval = pd.Series(pval,varlist)

## Observations
ncontrol = pd.Series(kwh[ kwh[ 'retrofit' ] == 0 ].count().min())
ntreat = pd.Series(kwh[ kwh[ 'retrofit' ] == 1 ].count().min())
nobs = pd.Series(kwh.count().min())

## Construct table
### Construct row names and column names
rowlist = varlist + ['Observations']
rownames = pd.concat([pd.Series(x.capitalize() for x in rowlist),pd.Series([' ',' ',' '])],axis = 1).stack() # Note this stacks an empty list and capitalizes the variable list
columnnames = [('Control','(s.d.)'),('Treatment','(s.d.)'),('Difference','(p val)')] # Two levels of column names

### Display means and differences to two decimal places
mean0 = mean0.map('{:.2f}'.format)
mean1 = mean1.map('{:.2f}'.format)
diff = diff.map('{:.2f}'.format)

### Display obs without decimal places
ncontrol = ncontrol.map('{:.0f}'.format)
ntreat = ntreat.map('{:.0f}'.format)
nobs = nobs.map('{:.0f}'.format)

### Display standard deviations to two decimal places and add parentheses
sd0 = sd0.map('({:.2f})'.format)
sd1 = sd1.map('({:.2f})'.format)
pval = pval.map('({:.2f})'.format)

### Align std deviations under means and pvalues under differences
col0 = pd.concat([mean0,sd0,ncontrol],axis = 1,keys = ['mean','std dev','obs']).stack() # Align std deviations under means
col1 = pd.concat([mean1,sd1,ntreat],axis = 1,keys = ['mean','std dev','obs']).stack()
col2 = pd.concat([diff,pval,nobs],axis = 1,keys = ['difference','p value','obs']).stack()

### Get rid of Pandas indices
col0 = col0.reset_index(drop = True)
col1 = col1.reset_index(drop = True)
col2 = col2.reset_index(drop = True)

### Finally put the pieces together and export to LaTeX
btable = pd.concat([col0,col1,col2], axis = 1)
btable.columns = pd.MultiIndex.from_tuples(columnnames)
btable.index = rownames

print(btable.to_latex())

os.chdir(outputpath) # Output directly to LaTeX folder

btable.to_latex('btable.tex')

# Question 2 -----------------------------------------------------------------

## I used Seaborn because it seemed hip

sns.distplot(kwh[ kwh[ 'retrofit' ] == 0 ]['electricity'], hist=False, label='Did not receive retrofit')
sns.distplot(kwh[ kwh[ 'retrofit' ] == 1 ]['electricity'], hist=False, label='Received retrofit')
plt.xlabel('Electricity use (KwH)')
plt.savefig('treatmenthist.pdf',format='pdf') # I suggest saving to .pdf for highest quality
plt.show()

# Question 3------------------------------------------------------------------

## Part (a)
### Set up Numpy matrices for OLS:
Yvar = kwh['electricity'].to_numpy()
nobsa, = Yvar.shape
constant = np.ones((nobsa,1)) # Vector of ones for the constant
Xvar = kwh.drop('electricity',axis = 1).to_numpy()
Xvar = np.concatenate([constant,Xvar],axis = 1) # Add the constant

### Run the regression
betaolsa = np.matmul(np.linalg.inv((np.matmul(Xvar.T, Xvar))), np.matmul(Xvar.T, Yvar))

## Part (b)
### Set up objective function

def my_leastsq(beta,Y,X):
    return np.sum((Y-np.matmul(X,beta))**2)

### Set up the solver
betaolsb = opt.minimize(my_leastsq,np.array([0,1,1,1]).T, args = (Yvar, Xvar)).x # I had to play with the initial conditions to get it to converge
nobsb, = Yvar.shape

## Part (c)
### Simply call the statsmodels function.  Now there is an (arguably) easier way to do this using R-style syntax with an equation.
olsc = sm.OLS(kwh['electricity'],Xvar).fit()
betaolsc = olsc.params.to_numpy()
nobsc = olsc.nobs

## Output table

### Row and column names
xvarlist = ['Constant', 'Sqft', 'Retrofit', 'Temperature','Observations']

rownames3 = pd.Series(xvarlist)
colnames3 = pd.Series(['(a)','(b)','(c)'])

### Put outputs and observations together
outputtable3 = pd.DataFrame((np.append(betaolsa,nobsa),np.append(betaolsb,nobsb),np.append(betaolsc,nobsc))).T
outputtable3.index = rownames3
outputtable3.columns = colnames3

outputtable3 = outputtable3.reindex(index = ['Retrofit', 'Sqft', 'Temperature', 'Constant','Observations'])

### Format to three decimal places and change order
for z in colnames3 :
    outputtable3[z] = outputtable3[z].map('{:.3f}'.format)
    outputtable3.loc['Observations',z] = "{0:.0f}".format(float(outputtable3.loc['Observations',z])) # This cannot be the most efficient or elegant way to do this.

outputtable3.to_latex('outputtable3.tex')