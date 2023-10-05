# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 18:58:13 2023

@author: Admin
"""
import requests
import pandas as pd
import json
import datetime
from loguru import logger

startYear = 2017
url = 'https://screeps.com/api/leaderboard/list?limit=20&mode=world&offset=0&season=2023-10'



def GetJason (url):
    # This function uses the API to get the data 
    # It returns the data as a dataframe
    # This dataframe is then appended to a list outside of the function
    # To be merged together into one dataframe at the end, and stored for future use.
    
    r = requests.get(url)
    j = r.json()

    ## Contains: (['ok', 'list', 'count', 'users'])
    # print(j.keys())
    # for i in j.keys():
    #     print(j[i])

    df = pd.DataFrame.from_dict(j['list'])
    # print (df)
    return df


    
def ListSeasons (startYear):
    # This creates a list (seasonNumbers) with all of the seasons (yyyy-mm strings) for the period in scope.
    today = datetime.date.today()
    currentYear = today.year
    currentMonth = today.month
    seasonNumbers = [] 
    
    # All seasons for all years but the current year:
    for year in range (currentYear - startYear):
        year = startYear + year
        for i in range (12):
            i = i+1
            # Months have to be 01 instead of 1.
            if i <10:
                monthstr = '0' + str(i)
            else: 
                monthstr = str(i)
            seasonNumbers.append(str(year) + '-' + monthstr)

    # The seasons for current year:        
    for i in range (currentMonth - 1) :
        # -1 because current month is not completed, and should therefore not be in dataset.
        i = i+1
        # Months have to be 01 instead of 1.
        if i <10:
            monthstr = '0' + str(i)
        else: 
            monthstr = str(i)
        seasonNumbers.append(str(currentYear) + '-' + monthstr)
    logger.info(str(len(seasonNumbers)) + ' seasons have to be downloaded.')
    # print(seasonNumbers)
    return seasonNumbers



def DownloadLeaderboard(startYear):
    # First this uses a different function to get all of the seasons in scope
    # then it figures out how many loops are needed for each season
    # then it downloads a season
    # repeat until all seasons are downloaded.
    
    seasons = ListSeasons(startYear)
    downloadedSeasons = []
    for season in seasons:
        downloadedSeasons.append(downloadSeason(season))
    downloadedSeasons = pd.concat(downloadedSeasons)
    downloadedSeasons.to_csv('ScrapedData.csv', index=False)
    
def downloadSeason (seasonNumber):
    url = 'https://screeps.com/api/leaderboard/list?limit=10&mode=world&offset=NaN&season=' + seasonNumber 
    r = requests.get(url)
    j = r.json()
    totalRecords = j['count']
    totalLoops = int(totalRecords / 20)
    downloadedDatasets = []
    # totalLoops = 1
    
    baseUrl = 'https://screeps.com/api/leaderboard/list?limit=20&mode=world&offset='
    seasonText = '&season='
    logger.info('Starting to collect season: ' + str(seasonNumber))
    
    for i in range (totalLoops):
        offset = str(i * 20)
        url = baseUrl + offset + seasonText + seasonNumber
        # print(url)
        downloadedDatasets.append(GetJason(url))
    if len(downloadedDatasets) == 0:
        logger.warning('Failed to collect for season: ' + seasonNumber)
    else: 
        logger.info('Collected ' + str(len(downloadedDatasets) * 20) + ' out of ' + str(totalRecords) + ' records.')
        downloadedDatasets = pd.concat(downloadedDatasets)
    return downloadedDatasets

DownloadLeaderboard(startYear)        
    # print()
    # return j['count']
    
