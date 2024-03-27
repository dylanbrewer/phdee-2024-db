# Homework 8 code -- Dylan Brewer

# Clear all
from IPython import get_ipython
get_ipython().magic('reset -sf')

# Import packages
import os
import numpy as np
import pandas as pd
import random
import statsmodels.api as sm
import matplotlib.pyplot as plt
from linearmodels.iv import IV2SLS

# Set working directories and seed
datapath = r'C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework5'
outputpath = r'C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework7\output'

os.chdir(datapath)

random.seed(3791)
np.random.seed(885223)

# Import homework data
data = pd.read_csv('instrumentalvehicles.csv')

# Set up variables

mpg = data['mpg']
length = data['length']

# Transform data around the cutoff

lengthtilde = length - 225

# Treatment variable

treat = (length>225)*1

# Question 2 -----------------------------------------------------------------

plt.scatter(lengthtilde,mpg,facecolors='none', edgecolors='red')
plt.axvline(linewidth=2, color='black',linestyle='dashed')
plt.ylabel('MPG')
plt.xlabel('Distance from cutoff')
plt.title('Question 2')
os.chdir(outputpath)
plt.savefig('hw7q2.pdf',format='pdf')
plt.show()

# Question 3 -----------------------------------------------------------------

# Interactions

lengthtildeabove=lengthtilde*treat

# Regression

rd3 = sm.OLS(mpg,sm.add_constant(pd.concat([lengthtilde,treat,lengthtildeabove],axis=1),prepend = False)).fit()
rd3betas = rd3.params

# Plot

xrun_1 = np.linspace(lengthtilde.min(),0,100)
xrun_2 = np.linspace(0,lengthtilde.max(),100)

yrd3_1 = rd3betas[-1] + xrun_1*rd3betas[0]
yrd3_2 = rd3betas[-1] + rd3betas[1] + xrun_2*(rd3betas[0] + rd3betas[2])

plt.scatter(lengthtilde,mpg,facecolors='none', edgecolors='silver')
plt.plot(xrun_1,yrd3_1)
plt.plot(xrun_2,yrd3_2)
plt.axvline(linewidth=2, color='r',linestyle='dashed')
plt.ylabel('MPG')
plt.xlabel('Distance from cutoff')
plt.title('Question 3')
plt.savefig('hw7q3.pdf',format='pdf')
plt.show()

# Question 4 -----------------------------------------------------------------

# Second degree polynomial

lengthtilde2 = lengthtilde**2

# Interactions

lengthtilde2above = lengthtilde2*treat

# Regression

rd4 = sm.OLS(mpg,sm.add_constant(pd.concat([lengthtilde,lengthtilde2,treat,lengthtildeabove,lengthtilde2above],axis=1),prepend = False)).fit()
rd4betas = rd4.params

yrd4_1 = rd4betas[-1] + xrun_1*rd4betas[0] + (xrun_1**2)*rd4betas[1]
yrd4_2 = rd4betas[-1] + rd4betas[2] + xrun_2*(rd4betas[0] + rd4betas[3]) + (xrun_2**2)*(rd4betas[1] + rd4betas[4])

# Plot

plt.scatter(lengthtilde,mpg,facecolors='none', edgecolors='silver')
plt.plot(xrun_1,yrd4_1)
plt.plot(xrun_2,yrd4_2)
plt.axvline(linewidth=2, color='r',linestyle='dashed')
plt.ylabel('MPG')
plt.xlabel('Distance from cutoff')
plt.title('Question 4')
plt.savefig('hw7q4.pdf',format='pdf')
plt.show()

# Question 5 -----------------------------------------------------------------

# Higher-order polynomials

lengthtilde3 = lengthtilde**3
lengthtilde4 = lengthtilde**4
lengthtilde5 = lengthtilde**5

# Interactions

lengthtilde3above = lengthtilde3*treat
lengthtilde4above = lengthtilde4*treat
lengthtilde5above = lengthtilde5*treat

rd5 = sm.OLS(mpg,sm.add_constant(pd.concat([lengthtilde,lengthtilde2,lengthtilde3,lengthtilde4,lengthtilde5,treat,lengthtildeabove,lengthtilde2above,lengthtilde3above,lengthtilde4above,lengthtilde5above],axis=1),prepend = False)).fit()
rd5betas = rd5.params
print(rd5.summary())

yrd5_1 = rd5betas[-1] + xrun_1*rd5betas[0] + (xrun_1**2)*rd5betas[1] + (xrun_1**3)*rd5betas[2] + (xrun_1**4)*rd5betas[3] + (xrun_1**5)*rd5betas[4]
yrd5_2 = rd5betas[-1] + rd5betas[5] + xrun_2*(rd5betas[0] + rd5betas[6]) + (xrun_2**2)*(rd5betas[1] + rd5betas[7]) + (xrun_2**3)*(rd5betas[2] + rd5betas[8]) + (xrun_2**4)*(rd5betas[3] + rd5betas[9]) + (xrun_2**5)*(rd5betas[4] + rd5betas[10])

plt.scatter(lengthtilde,mpg,facecolors='none', edgecolors='silver')
plt.plot(xrun_1,yrd5_1)
plt.plot(xrun_2,yrd5_2)
plt.axvline(linewidth=2, color='r',linestyle='dashed')
plt.ylabel('MPG')
plt.xlabel('Distance from cutoff')
plt.title('Question 5')
plt.savefig('hw7q5.pdf',format='pdf')
plt.show()

# Question 6 -----------------------------------------------------------------

yvar = data['price']
car = data['car']

# Change column names for 2SLS command

treat = treat.rename('Treat')
lengthtildeabove = lengthtildeabove.rename('Length X Treat')

# 2SLS

ivest = IV2SLS(yvar,sm.add_constant(car,prepend = False),mpg,pd.concat([lengthtilde,treat,lengthtildeabove],axis=1)).fit(cov_type='robust')

# Output

beta = pd.DataFrame(np.round(ivest.params,2)).reindex(['car','mpg','const'])

ci = pd.DataFrame(np.round(ivest.conf_int(),2)).reindex(['car','mpg','const'])

cis = '(' + ci.loc[:,'lower'].map(str) + ', ' + ci.loc[:,'upper'].map(str) + ')'

hw7output6 = pd.DataFrame(pd.concat([beta,cis],axis = 1).stack())
hw7output6.columns = ['Question 6']
hw7output6.index = ['Sedan',' ','MPG','','Constant','']
hw7output6 = pd.concat([hw7output6,pd.DataFrame([str(ivest.nobs)],index = ['Observations'],columns = ['Question 6'])])

hw7output6.to_latex('hw7output6.tex',column_format = 'lc', na_rep = ' ')





