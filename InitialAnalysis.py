# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 15:42:31 2023

@author: Admin
"""
import pandas as pd 
import seaborn as sns
import numpy as np
from loguru import logger
import time
sns.set_theme(style='ticks')
scoreColumnName = 'score'
fileName = 'PreProcessedData.csv'

def firstlook (fileName, scoreColumnName):
    df = pd.read_csv(fileName)
    logger.info('Preprocessed file contains the following columns: ' +str(df.columns))
    # firstLook = sns.boxplot(x = 'monthsPlayed', y = 'score', data = df)
    df['logScore'] = np.log10(df[scoreColumnName])
    logLook = sns.boxplot(x = 'monthsPlayed', y = 'logScore', data = df)
    
    return df 

# print(df.head(5))

def assignSkillLevel (Lower_Fence, Q1, Q3, Upper_Fence, score ):
    if score >= Upper_Fence:
        rating = 5 #'Exceptional'
    elif score >= Q3: 
        rating = 4 #'High'
    elif score >= Q1: 
        rating = 3 #'Ok'
    elif score >= 10000:  #lower fence is WAAAY deep in the negatives, using "having ANY form of functionality in your bot" as 
        rating = 2 #'Mediocre'
    else:
        rating = 1 #'Newby'
    return rating

def addSkillToDf (row, skillDatabase):
    try:
        rating = skillDatabase[row.user]
    except:
        rating = -1 # Not in dictionary because the user never played more than 1 month
    return rating

def identifySkillLevel (df, scoreColumnName):
    Q1 = df[scoreColumnName].quantile(0.25)
    Q3 = df[scoreColumnName].quantile(0.75)
    IQR = Q3 - Q1
    Lower_Fence = Q1 - (1.5 * IQR)
    Upper_Fence = Q3 + (1.5 * IQR)
    logger.info('The player score is quantifies as such, LF: ' +str(Lower_Fence) + ' Q1: ' +str(Q1) + ' Q3: ' + str(Q3) + ' UF: ' + str(Upper_Fence))
    skillDatabase = {'userName':0}
    for i in df.index.tolist():
        skill = assignSkillLevel(Lower_Fence, Q1, Q3, Upper_Fence, df[scoreColumnName][i])
        skillDatabase[df['user'][i]] = skill
    return skillDatabase

def graphData(graphType, x, y, data):
    if graphType == 'BP':
        plt = sns.boxplot(x = x, y = y, data = data)
        plt.yaxis.get_major_formatter().set_scientific(False)
        plt.set(ylim=(0,max(data[y])*0.05))
    elif graphType == 'HG':
        plt = sns.displot(y = y, data = data)
        # plt.yaxis.get_major_formatter().set_scientific(False)
        # plt.set(xlim=(0,100))
    else:
        logger.Warning('No graph selected')

def singleMonthSelector (df, specificMonth):
    query = f'monthsPlayed =={specificMonth}'
    interestingMonth = df.query(query)
    return interestingMonth

def singeMonthView (graphType, df):
    x = 'monthsPlayed'
    y = 'logScore'
    # y = 'score'
    data = df
    graphData(graphType, x, y, data)   
    
    

df = firstlook(fileName, scoreColumnName)

singleMonthDF = singleMonthSelector(df, specificMonth=2)
singeMonthView (graphType= 'HG', df= singleMonthDF)
skillDatabase = identifySkillLevel(singleMonthDF, scoreColumnName)     
df['skillLevel'] = df.apply(addSkillToDf,skillDatabase = skillDatabase, axis = 1)
sns.displot(x = 'skillLevel', data= df[['user','skillLevel']].drop_duplicates())





    



