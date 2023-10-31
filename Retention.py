# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 16:47:30 2023

@author: Admin
"""
import pandas as pd 
import seaborn as sns
from loguru import logger
import time
import Config

settings = Config.Settings()
sns.set_theme(style='ticks')

scoreColumnName = 'score'
fileName = (settings.outputdir / settings.preProccessedFilename).absolute()
df = pd.read_parquet(fileName)

# print(df['retentionRate'].unique())
# print(df[settings.retrurningPlayerCol].unique())

def setAFKFlag(row, threshold, rangeEnd):
    if row[settings.MonthsAFKCol]>=threshold and row[settings.MonthsAFKCol]<rangeEnd:
        return 1
    else:
        return 0

def setMassiveLossFlag(row, threshold):
    if row[settings.ScoreChangePercantageCol] < threshold:
        return 1 
    else:
        return 0

def GroupActivePlayersBySkill (df):
    query = settings.skillLevelCol + '!=-1' 
    df = df.query(query)
    a = sns.displot(x = settings.monthsPlayedCountCol, data= df, hue= settings.skillLevelCol, palette="PuOr")
    return a

def RetentionAnalysis (df):
    sumDf = df[[settings.monthsPlayedCountCol, 
                settings.skillLevelCol,
                settings.FinalPlayedMonthCol]].copy()
    sumDf = sumDf.groupby([settings.monthsPlayedCountCol, settings.skillLevelCol]).mean()
    b=sns.lineplot(x=settings.monthsPlayedCountCol, y=settings.FinalPlayedMonthCol,
                  data=sumDf, hue = settings.skillLevelCol)
    return b 

def ImpactOfAFK (df, comparisonColumn):
    df = df[[comparisonColumn,
                 settings.FinalPlayedMonthCol]]
    df = df.groupby(comparisonColumn).mean()
    print(df.head(20))
    
# a= GroupActivePlayersBySkill(df)
# time.sleep(2)
# b = RetentionAnalysis(df)

df[settings.threeMonthsAFKCol] = df.apply(setAFKFlag,threshold = 3, rangeEnd = 6, axis = 1)
df[settings.SixMonthsAFKCol] = df.apply(setAFKFlag,threshold = 6, rangeEnd = 12, axis = 1)
df[settings.TwelveMonthsAFKCol] = df.apply(setAFKFlag,threshold = 12, rangeEnd = 999999, axis = 1)
df[settings.MassiveLossCol] = df.apply(setMassiveLossFlag,threshold = -0.5, axis = 1)

ImpactOfAFK(df, settings.MonthsAFKCol)
ImpactOfAFK(df, settings.monthsPlayedCountCol)
ImpactOfAFK(df, settings.MassiveLossCol)
    

#   SeasonNrCol: str = 'SeasonNumber'
#   retrurningPlayerCol: str ='returning'
#   ScorePreviousMonthCol: str ='previousScore'
#   cumScoreCol: str ='cumScore'
#   maxScoreCol: str ='maxScore'
#   ScoreChangePercantageCol: str ='scoreChange'
#   monthsPlayedCountCol: str ='monthsPlayed'
#   FinalPlayedMonthCol: str ='retentionRate'
#   MonthsAFKCol: str ='monthsAFK'
#   playerTypeCol: str = 'PlayerType'
#   logScoreCol:  float = 'logScore'       
#   skillLevelCol: int = 'skillLevel'