# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 19:48:55 2023

@author: Admin
"""

import pandas as pd
import numpy as np
from loguru import logger
import Download
startYear = 2015


df = pd.read_csv('ScrapedData.csv')
# print(df.head(21))
seasonList = Download.ListSeasons (startYear)
# print(seasonList)

def defineStartYear (row):
    try:
        return seasonList.index(row.season)
    except Exception as e:
        logger.warning('Season not found for season: ' + str(row) + '\nError: ' + str(e))
        return -1



uniquePlayers = df['user'].unique().tolist()
df['SeasonNumber'] = df.apply(defineStartYear, axis =1)
logger.info('total records in the dataset: '+ str(len(df._id.unique())) + ', Unique players: ' + str(len(df.user.unique())))

playerDatabase = []
for player in uniquePlayers:
    
    
    query = f'user =="{player}"'
    playerActivity = df.query(query)
    # print(playerActivity.columns)
    
    # Start of loop variable cleanup:
    previousSeason = -1 
    previousScore = -1
    cumScore = 0 
    maxScore = 0 
    playerData = []
    monthsPlayed = 1
    loopNr = 1 
    totalLoops = len(playerActivity)
    
    # This gets changed when the season numbers are not adding up
    for i in playerActivity.index.tolist() :
        # print(i, len(playerActivity))
        # print(playerActivity['SeasonNumber'][i])
        if previousSeason == -1:
            returning = False # the first season is always not a returning player
        elif playerActivity['SeasonNumber'][i] == previousSeason + 1:
            returning = False # if he kept playing after the previous month
        else:
            returning = True # He skipped a month
        previousSeason = playerActivity['SeasonNumber'][i]
        
        
        # The first month the user does not have a previous score, filling it with something useless.
        if previousScore == -1:
            previousScore = playerActivity['score'][i]
       
        # Cumulative score increases each month by the score
        cumScore = cumScore + playerActivity['score'][i]
        
        # Max score = the highest score the user has ever achieved until this point
        maxScore = max(maxScore, playerActivity['score'][i])
        
        # Score increase percentage based:
        scoreChange = (playerActivity['score'][i] / previousScore) -1 
        
        # Last month of play?
        if loopNr == totalLoops:
            lastMonth = False
        else:
            lastMonth = True
            loopNr = loopNr + 1 
        
        # Storing information for the dataframe using NP array:
        playerData.append( np.array([playerActivity['_id'][i],
                            playerActivity['season'][i], 
                            playerActivity['user'][i],
                            playerActivity['score'][i],
                            playerActivity['rank'][i],
                            playerActivity['SeasonNumber'][i],
                            returning,
                            previousScore,
                            cumScore,
                            maxScore,
                            scoreChange,
                            monthsPlayed,
                            lastMonth
            ]))
        
        # DF version attempt:
        # data = {
        #     'season':playerActivity['season'][i], 
        #     'user':playerActivity['user'][i],
        #     'score':playerActivity['score'][i],
        #     'rank':playerActivity['rank'][i],
        #     'seasonNumber':playerActivity['SeasonNumber'][i],
        #     'returning':returning,
        #     'previousScore':previousScore,
        #     'cumScore':cumScore,
        #     'maxScore':maxScore,
        #     'scoreChange':scoreChange,
        #     'monthsPlayed':monthsPlayed,
            
        #     }
        # df = pd.DataFrame(data)
        # print(df)
        
        
        
        # Storing score for next loop
        previousScore = playerActivity['score'][i]
        monthsPlayed = monthsPlayed + 1
    playerDatabase.append(playerData)
    # break

playerDatabase = np.concatenate(playerDatabase)
playerDatabase = pd.DataFrame(playerDatabase, columns = ['_id','season','user', 'score', 'rank', 'seasonNumber', 'returning', 'previousScore', 'cumScore', 'maxScore', 'scoreChange', 'monthsPlayed', 'retentionRate'])
playerDatabase.to_csv('PreProcessedData.csv', index = False)

print('done')
# def ducktapeStuffTogether (row, columnName):
#     print(playerDatabase[0][0])
#     return playerDatabase[playerDatabase.index(row['_id'])]

# df.apply(ducktapeStuffTogether,columnName = 'a', axis = 1)

# df = pd.DataFrame(data = playerDatabase, columns = ['season','user', 'score', 'rank', 'seasonNumber', 'returning', 'previousScore', 'cumScore', 'maxScore', 'scoreChange', 'monthsPlayed'])
# print(df.columns)
# df[['season','user', 'score', 'rank', 'seasonNumber', 'returning', 'previousScore', 'cumScore', 'maxScore', 'scoreChange', 'monthsPlayed']]
# print(df)


# print(playerDatabase)