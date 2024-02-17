# Homework 4 code -- Dylan Brewer

# Clear all
from IPython import get_ipython
get_ipython().magic('reset -sf')

# Import packages
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import statsmodels.api as sm
from stargazer.stargazer import Stargazer as stargazer
from stargazer.stargazer import LineLocation

# Set working directories and seed
datapath = r'C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework4'
outputpath = r'C:\Users\brewe\Dropbox\teaching\Courses\BrewerPhDEnv\Homeworks\phdee-2024-db\homework4\output'

os.chdir(datapath)

random.seed(20121159)
np.random.seed(411128)

# Import homework data
datawide = pd.read_csv('fishbycatch.csv')

# Prepare data and pivot to long
datalong = pd.wide_to_long(datawide,stubnames = ['salmon','shrimp','bycatch'], i = 'firm', j = 'month')
datalong = datalong.reset_index(level=['firm', 'month'])

## Treatment group and treated variables
datalong['treatgroup'] = datalong['treated'] # Static variable for which firms are in the treatment group
datalong['treated2'] = np.where((datalong['treated'] == 1) & (datalong['month']>12) & (datalong['month']<25), 1, 0)
datalong['treated3'] = np.where((datalong['month']>24), 1, 0)
datalong['treated'] = datalong['treated2'] + datalong['treated3'] # Dynamic variable for when firms receive treatment

datalong = datalong.drop(columns = ['treated2', 'treated3']) # drop extra variables

# Problem 1 ------------------------------------------------------------------
trends = datalong.groupby(['treatgroup','month']).mean()
controltrends = trends.loc[0, :]
controltrends = controltrends.reset_index()
treattrends = trends.loc[1, :]
treattrends = treattrends.reset_index()

## Build the plot
plt.plot(controltrends['month'], controltrends['bycatch'], marker = 'o')
plt.plot(treattrends['month'], treattrends['bycatch'], marker = 'o')
plt.axvline(x=12.5, color = 'red', linestyle = 'dashed') # Vertical line to indicate treatment year
plt.xlabel('Month')
plt.ylabel('Mean bycatch per firm (lbs)')
plt.legend(['Control', 'Treatment','Treatment date'])
os.chdir(outputpath) # Change directory
plt.savefig('hw4_q1.pdf',format='pdf')
plt.show()

# Problem 2 ------------------------------------------------------------------

DID = (trends.loc[(1,13),'bycatch'] - trends.loc[(1,12),'bycatch']) - (trends.loc[(0,13),'bycatch'] - trends.loc[(0,12),'bycatch'])

# Problem 3a ------------------------------------------------------------------
twoperiod = datalong[(datalong['month'] == 12) | (datalong['month'] == 13)]
pre = pd.get_dummies(twoperiod['month'],prefix = 'pre', drop_first = True)
twoperiod = pd.concat([twoperiod,pre],axis = 1)

yvar3a = twoperiod['bycatch']
xvar3a = twoperiod[['treatgroup','treated','pre_13']]

DID3a = sm.OLS(yvar3a,sm.add_constant(xvar3a, prepend = False).astype(float)).fit()
DID3arobust = DID3a.get_robustcov_results(cov_type = 'cluster', groups = twoperiod['firm']) # Cluster-robust confidence intervals

# Problem 3b ------------------------------------------------------------------
yvar3b = datalong['bycatch']
tvars3b = pd.get_dummies(datalong['month'],prefix = 'time',drop_first = True) # creates dummies from time variables
xvar3b = pd.concat([datalong[['treatgroup','treated']],tvars3b],axis = 1)

DID3b = sm.OLS(yvar3b,sm.add_constant(xvar3b,prepend = False).astype(float)).fit()
DID3brobust = DID3b.get_robustcov_results(cov_type = 'cluster', groups = datalong['firm'])

# Problem 3c ------------------------------------------------------------------
yvar3c = datalong['bycatch']
tvars3c = pd.get_dummies(datalong['month'],prefix = 'time',drop_first = True) # creates dummies from time variables
xvar3c = pd.concat([datalong[['treatgroup','treated','shrimp','salmon','firmsize']],tvars3c],axis = 1)

DID3c = sm.OLS(yvar3c,sm.add_constant(xvar3c,prepend = False).astype(float)).fit()
DID3crobust = DID3c.get_robustcov_results(cov_type = 'cluster', groups = datalong['firm'])







# Output table with Stargazer package  ----------------------------------------
output = stargazer([DID3a,DID3b,DID3c])

output.covariate_order(['treated','treatgroup','pre_13','shrimp', 'salmon'])
output.rename_covariates({'treated':'Treated','treatgroup':'Treatment group','pre_13':'Pre-period','shrimp':'Shrimp','salmon':'Salmon'})
output.add_line('Month indicators',['Y','Y','Y'], LineLocation.FOOTER_TOP)
output.significant_digits(2)
output.show_degrees_of_freedom(False)

file_name = "test.tex" #Include directory path if needed
tex_file = open('outputhw4.tex', "w" ) #This will overwrite an existing file
tex_file.write( output.render_latex() )
tex_file.close()

# Export long data for use in Stata

datalong.to_csv('longdata_stata.csv', index = None, header=True)

