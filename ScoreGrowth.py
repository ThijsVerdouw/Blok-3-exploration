# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 13:30:10 2023

@author: Admin
"""

import pandas as pd 
import seaborn as sns
import numpy as np 
from scipy import stats
import InitialAnalysis


# sns.set_theme(style='ticks')
# scoreColumnName = 'score'
fileName = 'PreProcessedData.csv'
df = pd.read_csv(fileName)

# print(df[['scoreChange','score', 'previousScore','user']].head(20))

def fancyXAxisForComparingReturning(row, selectedMonth):
    if row.returning == 1:
        result = 'Returning player'
    elif row.monthsPlayed == selectedMonth:
        result = 'Normal player'
    else: 
        result = 'Rest of dataset'
    return result


def T_test (df1, df2, columnName):
    pass

def identifyImpactOfLeaving (df, referenceMonth):
    # The idea is that leaving causes player to lose a lot of score because all of their infrastructure is gone.
    # The aim is to measure this by checking if they lose a large percentage of the score 
    # they have the in month they return in comparison to the month they had before.
    # The expectation is that this would be significantly more negative than normal months for normal players.
    df['PlayerType'] = df.apply(fancyXAxisForComparingReturning, selectedMonth = referenceMonth, axis = 1)

    plt = InitialAnalysis.graphData(graphType = 'BP', x = 'PlayerType', y = 'scoreChange' , data = df)
    plt.set(ylim=(-1,5)) # Reality shows us that the returning month can instead be all over the place.
    # They can return up to 10 times more powerful than before after quitting, or they can lose everything.
    # month of big variation here. Good for including in final presentation.

    plt = InitialAnalysis.graphData(graphType = 'HG',  y = 'PlayerType' , data = df)
    

identifyImpactOfLeaving (df, referenceMonth= 3)
# sns.histplot(x = 'scoreChange', data= filteredData, bins = 3 )

# plt = sns.boxplot(y = 'scoreChange', data = filteredData)
# plt.yaxis.get_major_formatter().set_scientific(False)
# plt.set(ylim=(-2,10))

# print(stats.ttest_ind(normalThirdMonth['scoreChange'], returning['scoreChange']))