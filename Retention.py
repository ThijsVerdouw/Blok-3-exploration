# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 16:47:30 2023

@author: Admin
"""
import pandas as pd 
import seaborn as sns
from loguru import logger
import matplotlib.ticker as mtick
import Config

settings = Config.Settings()
sns.set_theme(style="darkgrid")


# fileName = (settings.outputdir / settings.preProccessedFilename).absolute()
# df = pd.read_parquet(fileName)

# print(df['retentionRate'].unique())
# print(df[settings.retrurningPlayerCol].unique())

def setAFKFlag(row, threshold, rangeEnd):
    if row[settings.MonthsAFKCol]>=threshold and row[settings.MonthsAFKCol]<rangeEnd:
        return 1
    else:
        return 0

def setMassiveLossFlag(row, threshold):
    if row[settings.retrurningPlayerCol] == 1: # if they just came back, their bot died. This is pointless as the aim of this column is to predict if someone is going to leave.
        return 0
    elif row[settings.ScoreChangePercantageCol] < threshold:
        return 1 
    else:
        return 0
    
def addRetentionColumns (df):
    # This adds certain flags based on thresholds for the months afk field and the scorechange field.
    # This is triggered from post processing.
    logger.info('adding retention columns')
    df[settings.threeMonthsAFKCol] = df.apply(setAFKFlag,threshold = 3, rangeEnd = 6, axis = 1)
    df[settings.SixMonthsAFKCol] = df.apply(setAFKFlag,threshold = 6, rangeEnd = 12, axis = 1)
    df[settings.TwelveMonthsAFKCol] = df.apply(setAFKFlag,threshold = 12, rangeEnd = 999999, axis = 1)
    df[settings.MassiveLossCol] = df.apply(setMassiveLossFlag,threshold = -0.5, axis = 1)
    logger.info('Succesfully added retention columns')
    return df

def GroupActivePlayersBySkill (df):
    # The aim of this function is to get all of the players who have played for more than one month
    # and to visualise, for each month, the count of active players.
    graphTitle = 'Active players by skill level'
    logger.info('Graphing ' + graphTitle)
    
    # gets all players who have played for more than 1 month:    
    query = settings.skillLevelCol + '!=-1' 
    df = df.query(query)
    
    # This makes a nice looking graph:
    plt = sns.histplot(x = settings.monthsPlayedCountCol, data= df, hue= settings.skillLevelCol, palette="tab10", multiple = 'stack')
    graphTitle = 'Active players by skill level'
    plt.set(title= graphTitle, xlabel='Number of months played', ylabel = 'Number of players')
    plt.figure.savefig(str(settings.figdir) + '/' + graphTitle + ".jpg", format='jpg',dpi=600)
    
    # Clears figure so it does not fuck up the other graphs being generated.
    plt.figure.clear()
    logger.info('Saved ' + graphTitle)

def RetentionAnalysis (df):
    # The aim of this function is to graph the retention rate by month, by skill level.
    graphTitle = 'Retention rate by month'
    logger.info('Graphing ' + graphTitle)
    
    # The players who quit in the first month are out of scope:        
    query = settings.skillLevelCol + '!=-1' 
    df = df.query(query)
    
    # Averages the retention rate by the groups and months:
    sumDf = df[[settings.monthsPlayedCountCol, 
                settings.skillLevelCol,
                settings.FinalPlayedMonthCol]].copy()
    sumDf = sumDf.groupby([settings.monthsPlayedCountCol, settings.skillLevelCol]).mean()
    
    # Makes a nice lookin graph:
    plt=sns.lineplot(x=settings.monthsPlayedCountCol, y=settings.FinalPlayedMonthCol,
                  data=sumDf, 
                  hue = settings.skillLevelCol)
    plt.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    plt.set(title= graphTitle, xlabel='Number of months played', ylabel = 'Retention rate (%)')
    plt.figure.savefig(str(settings.figdir) + '/' + graphTitle + ".jpg", format='jpg',dpi=600)
    
    # Clears figure so it does not fuck up the other graphs being generated.
    plt.figure.clear()
    logger.info('Saved ' + graphTitle)

def LossByAFKMonth (df, comparisonColumn, quitColumn = settings.FinalPlayedMonthCol):
    df = df[[comparisonColumn,
                 quitColumn]]
    df = df.groupby(comparisonColumn).mean()
    print(df.head(20))

def QuitPercentageByColumn (df, comparisonColumn, graphTitle, yname, quitColumn = settings.FinalPlayedMonthCol):
    # This function groups the quit rate for the potential types of causes, and graphs them.
    
    logger.info('Graphing ' + graphTitle)
    # First we aggregate the average quit rate for the types of scenarios:
    df = df[[comparisonColumn,
                 quitColumn]]
    df = df.groupby(comparisonColumn).mean()
    
    # This makes a nice looking graph:
    GraphColumn = 'Bot Health'
    df[GraphColumn] = ['Doing fine','Dying bot']
    plt = sns.barplot(x = df[GraphColumn], y = quitColumn, data = df)
    plt.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    plt.set(title= graphTitle, xlabel='Bot health', ylabel = yname)
    plt.figure.savefig(str(settings.figdir) + '/' + graphTitle + ".jpg", format='jpg',dpi=600)
    
    # Clears figure so it does not fuck up the other graphs being generated.
    plt.clear()
    logger.info('Saved ' + graphTitle)

def corrMat(df):
      # The aim of this function is to get the correlation matrix for
      # "The features which have the highest likelyhood of predicting if a player will return"
      # as well as the other features
    graphTitle = 'Correlation matrix of engineered features'
    logger.info('Graphing ' + graphTitle)
    
    # gets all players who have played for more than 1 month:    
    df = df[[settings.SeasonNrCol ,
          settings.monthsPlayedCountCol ,
          settings.MonthsAFKCol,
          settings.skillLevelCol,
          
          settings.ScorePreviousMonthCol ,
          settings.scoreCol,
          settings.cumScoreCol ,
          settings.maxScoreCol ,
          settings.logScoreCol,
          
          settings.retrurningPlayerCol,
          settings.MassiveLossCol,
          settings.TMPandPermanentStopCol,
          settings.FinalPlayedMonthCol]]
    # query = quitColumn=settings.TMPandPermanentStopCol + '==1' # They quit 
    # df = df.query(query)
    corr_matrix = round(df.corr(),1)
    plt = sns.heatmap(corr_matrix, annot=True)
    plt.set(title= graphTitle)
    plt.figure.savefig(str(settings.figdir) + '/' + graphTitle + ".jpg", format='jpg',dpi=600, bbox_inches='tight')
    plt.figure.clear()
    
def PerformRetentionAnanlyis(FilePath):    
    # This function is triggered from main and performs the analysis in this module.
    df = pd.read_parquet(FilePath)
    GroupActivePlayersBySkill(df)
    RetentionAnalysis(df)
    # LossByAFKMonth(df, settings.MonthsAFKCol)
    # LossByAFKMonth(df, settings.monthsPlayedCountCol)
    QuitPercentageByColumn(df,settings.MassiveLossCol, 'Retention rate (%) by bot health', 'Retention rate (%)')
    QuitPercentageByColumn(df, settings.MassiveLossCol, 'Stop rate (%) by bot health', 'Stop rate (%)', quitColumn=settings.TMPandPermanentStopCol)
    corrMat(df)

    logger.info('We have had this many cases of a player quitting and coming back: ' + str(-1 * sum(df[settings.TMPandPermanentStopCol]-df[settings.FinalPlayedMonthCol])))    



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