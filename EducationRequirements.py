#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is Python codes for my paper "The effect of high school exit exams on 
educational attainment and employment: new evidence from a reform in the state 
of Georgia"
See my website for more details: https://sites.google.com/view/htnguyen2403/home
@author: hieunguyen
"""

import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import seaborn as snb
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import econtools

# 4-year Adjusted Cohort Graduation Rates Data Files for Georgia and Florida
GeorgiaFile = "/Users/hieunguyen/Desktop/Dissertation/High School Graduation Requirement/Georgia/Graduation Rate/Georgia_Grad_rate.dta"
FloridaFile = "/Users/hieunguyen/Desktop/Dissertation/High School Graduation Requirement/Florida/Graduation Rates/Florida_GradRate_Total.dta"


# Read in the data and rename some variables
data_org = pd.read_stata(GeorgiaFile)   
data_org['state'] = "Georgia"
data_org = data_org.rename(columns ={"school_dstrct_cd":"districtnumber","school_dstrct_nm":"districtname"\
                             ,"instn_number":"schoolnumber","instn_name":"schoolname", \
                               "total_count":"totalcohort","program_total":"totalgraduates", \
                                "program_percent":"totalgradrate"})

    
# Analysis for the group of "All students"
data = data_org.query('label_lvl_1_desc== "Grad Rate -ALL Students"')
data = data.append(pd.read_stata(FloridaFile), ignore_index=True)
                  
# Collapse the data by state and graduation cohort
df = data.groupby(['classyear','state'])['totalgradrate'].\
    agg(['mean',stats.sem]).reset_index().rename(columns = {"mean":"totalgradrate"})    

df1 = df.query('state == "Georgia"')
df2 = df.query('state == "Florida"')
# How do you do aweight in Python?        

# Plot the comparison graphs for Florida vs Georgia
plt.errorbar(df1.classyear, df1.totalgradrate, yerr = 1.96*df1['sem'], color='red', mfc ='red')
plt.axvline(2014.5,linestyle="-", color = 'black')
plt.errorbar(df2.classyear, df2.totalgradrate, yerr = 1.96*df2['sem'], color='blue', mfc ='blue')

plt.title("Weighted 4-year Adjusted Cohort Graduation Rates of Florida and Georgia")
plt.xlabel("Graduation Cohort")
plt.ylabel("Percentages")


# Regression Analysis:
data = data.eval('Georgia = state == "Georgia"')    
data = data.eval('Post = classyear >=2015')
data['Int'] = data['Post'].multiply(data['Georgia'])

result1 = smf.ols(formula = 'totalgradrate ~ C(Georgia)*C(classyear)', data=data).fit(cov_type='HC0')
print(result1.summary())

data = econtools.group_id(data, cols=['schoolnumber', 'districtnumber', 'state'], merge = True)
result2 = smf.ols(formula = 'totalgradrate ~ Int + C(classyear) + C(group_id)', data=data).fit(cov_type='HC0')
print(result2.summary())

result3 = smf.ols(formula = 'totalgradrate ~ C(Georgia)*C(classyear) + C(group_id)', data=data).fit(cov_type='HC0')
print(result3.summary())

