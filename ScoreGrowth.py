# -*- coding: utf-8 -*-
"""
Worth persuing? https://seaborn.pydata.org/tutorial/axis_grids.html
"""

import pandas as pd 
import seaborn as sns
import numpy as np 
# from scipy import stats
import matplotlib.ticker as mtick
import Config
from loguru import logger

settings = Config.Settings()
sns.set_theme(style="darkgrid")



def fancyXAxisForComparingReturning(row, selectedMonth):
    if row.returning == 1:
        result = 'Returning player'
    elif row.monthsPlayed == selectedMonth:
        result = 'Player in 3rd month'
    else: 
        result = 'Rest of dataset'
    return result


def T_test (df1, df2, columnName):
    pass

def identifyImpactOfLeaving (FilePath, referenceMonth= 3 ):
    # The idea is that leaving causes player to lose a lot of score because all of their infrastructure is gone.
    # The aim is to measure this by checking if they lose a large percentage of the score 
    # they have the in month they return in comparison to the month they had before.
    # The expectation is that this would be significantly more negative than normal months for normal players.
    df = pd.read_parquet(FilePath)
    df[settings.playerTypeCol] = df.apply(fancyXAxisForComparingReturning, selectedMonth = referenceMonth, axis = 1)

    graphTitle = 'Returning players have unpredictable scores'
    logger.info('Graphing ' + graphTitle)    

    plt = sns.boxplot(x = settings.playerTypeCol, y = settings.ScoreChangePercantageCol, data = df)
    plt.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    
    plt.set(title= graphTitle, xlabel='Player type', ylabel = 'Score change in comparison to previous month(%)')
    plt.figure.savefig(str(settings.figdir) + '/' + graphTitle + ".jpg", format='jpg',dpi=600)
    
    plt.set(ylim=(-1,5)) 
    # Reality shows us that the returning month can instead be all over the place.
    # They can return up to 10 times more powerful than before after quitting, or they can lose everything.
    # month of big variation here. Good for including in final presentation.
    
    # Clears figure so it does not fuck up the other graphs being generated.
    plt.figure.clear()
    logger.info('Saved ' + graphTitle)
    

# identifyImpactOfLeaving(df)






