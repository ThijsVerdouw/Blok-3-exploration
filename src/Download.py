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
import Config

settings = Config.Settings()


def GetJason(url):
    # This function uses the API to get the data
    # It returns the data as a dataframe
    # This dataframe is then appended to a list outside of the function
    # To be merged together into one dataframe at the end, and stored for future use.

    collectedData = False
    tries = 0
    while collectedData == False and tries < 10:
        try:
            r = requests.get(url)
            j = r.json()
            collectedData = True
            df = pd.DataFrame.from_dict(j["list"])
            if tries > 0:
                logger.info("Fixed issue for this ULR by retrying: " + str(url))
        except Exception as e:
            logger.warning(
                "Failed to collect total number of records for this ULR: \n" + str(url)
            )
            logger.warning("Reason:" + str(e))
            tries = tries + 1
        ## Contains: (['ok', 'list', 'count', 'users'])
        # print(j.keys())
        # for i in j.keys():
        #     print(j[i])
    if tries > 9:
        # Download has failed:
        df = pd.DataFrame()  # ensures we return an empty dataframe to prevent crashes.
    # print (df)
    return df


def ListSeasons(startYear):
    # This creates a list (seasonNumbers) with all of the seasons (yyyy-mm strings) for the period in scope.
    today = datetime.date.today()
    currentYear = today.year
    currentMonth = today.month
    seasonNumbers = []

    # All seasons for all years but the current year:
    for year in range(currentYear - startYear):
        year = startYear + year
        for i in range(12):
            i = i + 1
            # Months have to be 01 instead of 1.
            if i < 10:
                monthstr = "0" + str(i)
            else:
                monthstr = str(i)
            seasonNumbers.append(str(year) + "-" + monthstr)
    # The seasons for current year:
    for i in range(currentMonth - 1):
        # -1 because current month is not completed, and should therefore not be in dataset.
        i = i + 1
        # Months have to be 01 instead of 1.
        if i < 10:
            monthstr = "0" + str(i)
        else:
            monthstr = str(i)
        seasonNumbers.append(str(currentYear) + "-" + monthstr)
    logger.info(str(len(seasonNumbers)) + " seasons have to be downloaded.")
    # print(seasonNumbers)
    return seasonNumbers


def downloadSeason(seasonNumber):
    # This function first identifies the total number of records for a given season,
    # and then it downloads all of those records in batches of 20.
    # I am intentionally not downloading the last couple of records, those are bad data.
    url = settings.countRecordsLink + seasonNumber

    # This has to succeed, it gets the total number of records for a month. if it fails the entire thing dies.
    collectedData = False
    tries = 0
    while collectedData == False and tries < 10:
        try:
            r = requests.get(url)
            j = r.json()
            collectedData = True
            if tries > 0:
                logger.info("Fixed issue for this ULR by retrying: " + str(url))
        except Exception as e:
            logger.warning(
                "Failed to collect total number of records for this ULR: \n" + str(url)
            )
            logger.warning("Reason:" + str(e))
            tries = tries + 1
    totalRecords = j[settings.totalRecordsCol]
    if totalRecords <= 0:
        logger.warning("No records for season: " + str(seasonNumber))
        return []
    else:
        totalLoops = int(totalRecords / 20)
        downloadedDatasets = []
        # totalLoops = 1

        baseUrl = settings.downloadLink
        seasonText = "&season="
        logger.info("Starting to collect season: " + str(seasonNumber))

        for i in range(totalLoops):
            offset = str(i * 20)
            url = baseUrl + offset + seasonText + seasonNumber
            # print(url)
            downloadedDatasets.append(GetJason(url))
        if len(downloadedDatasets) == 0:
            logger.warning("Failed to collect for season: " + seasonNumber)
        else:
            logger.info(
                "Collected "
                + str(len(downloadedDatasets) * 20)
                + " out of "
                + str(totalRecords)
                + " records."
            )
            downloadedDatasets = pd.concat(downloadedDatasets)
        return downloadedDatasets


def DownloadLeaderboard(startYear):
    # First this uses a different function to get all of the seasons in scope
    # then it figures out how many loops are needed for each season
    # then it downloads a season
    # repeat until all seasons are downloaded.

    seasons = ListSeasons(startYear)
    # seasons = ['2021-09'] # debug
    downloadedSeasons = []
    for season in seasons:
        downloadedData = downloadSeason(season)
        if len(downloadedData) == 0:
            pass  # warning has been triggered in download function
        else:
            downloadedSeasons.append(downloadedData)
    downloadedSeasons = pd.concat(downloadedSeasons)
    logger.info(
        "Completed download. Downloaded " + str(len(downloadedSeasons)) + " records."
    )
    downloadedSeasons = downloadedSeasons.astype(dtype=settings.dataTypesRawData)
    downloadedSeasons.to_parquet(
        (settings.datadir / settings.scrapedFileName).absolute(), index=False
    )


# DownloadLeaderboard(startYear)
# print()
# return j['count']
