# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 19:48:55 2023

@author: Admin
"""

import pandas as pd
import numpy as np
from loguru import logger
import Download
import InitialAnalysis
import ScoreGrowth
import Retention


def defineStartYear(row, seasonList):
    # This turns the season string into a season number, which is done to make it an easy to use X axis.
    try:
        return seasonList.index(row.season)
    except Exception as e:
        logger.warning(
            "Season not found for season: " + str(row) + "\nError: " + str(e)
        )
        return -1


def perfomInitialAnalysis(df, settings):
    logger.info("Starting creating complex features")
    singleMonthDF = InitialAnalysis.singleMonthSelector(
        df, specificMonth=settings.MonthNrForSkillLevel
    )
    skillDatabase = InitialAnalysis.identifySkillLevel(singleMonthDF, settings.scoreCol)
    df[settings.skillLevelCol] = df.apply(
        InitialAnalysis.addSkillToDf, skillDatabase=skillDatabase, axis=1
    )
    df[settings.playerTypeCol] = df.apply(
        ScoreGrowth.fancyXAxisForComparingReturning,
        selectedMonth=settings.MonthNrForPlayerType,
        axis=1,
    )
    df[settings.logScoreCol] = np.log10(df[settings.scoreCol])
    return df


def basicFeatureCreation(rawDataPath, settings):
    # This function downloads the raw dataset and performs various actions with it.

    logger.info("Starting creating basic features")
    df = pd.read_parquet(rawDataPath)
    logger.info("Opened dataset, dataset looks like this:\n" + str(df.describe()))

    # print(df)
    # print (settings.originalIDCol)
    seasonList = Download.ListSeasons(settings.startYear)
    # print(seasonList)

    uniquePlayers = df[settings.userIDCol].unique().tolist()
    df[settings.SeasonNrCol] = df.apply(
        defineStartYear, seasonList=seasonList, axis=1
    )  # creates a reliable int X axis.
    logger.info(
        "total records in the dataset: "
        + str(len(df[settings.originalIDCol].unique()))
        + ", Unique players: "
        + str(len(df[settings.userIDCol].unique()))
    )

    playerDatabase = (
        []
    )  # empty list to contain the individual dataframes once they are collected.
    for player in uniquePlayers:
        ###############################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#######################################
        query = f'user =="{player}"'  # unpipelined.
        ###############################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#######################################
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
        monthsAFK = 0
        totalLoops = len(playerActivity)
        currentMonth = seasonList[len(seasonList) - 1]  # The currently live season
        IndexesForPlayer = playerActivity.index.tolist()

        # This gets changed when the season numbers are not adding up
        for i in IndexesForPlayer:
            # print(i, len(playerActivity))
            # print(playerActivity['SeasonNumber'][i])
            # print(playerActivity)
            if previousSeason == -1:
                returning = 0  # the first season is always not a returning player
            elif playerActivity[settings.SeasonNrCol][i] == previousSeason + 1:
                returning = 0  # if he kept playing after the previous month
            else:
                returning = 1  # He skipped a month
            previousSeason = playerActivity[settings.SeasonNrCol][i]

            # The first month the user does not have a previous score, filling it with something useless.
            if previousScore == -1:
                previousScore = playerActivity[settings.scoreCol][i]
            # Cumulative score increases each month by the score
            cumScore = cumScore + playerActivity[settings.scoreCol][i]

            # Max score = the highest score the user has ever achieved until this point
            maxScore = max(maxScore, playerActivity[settings.scoreCol][i])

            # This identifies if a player has stopped improving, which helps identify AFK players
            # Which should help with predicting score growth.
            if playerActivity[settings.scoreCol][i] < maxScore:
                monthsAFK = monthsAFK + 1
            else:
                monthsAFK = 0
            # Score increase percentage based:
            scoreChange = (playerActivity[settings.scoreCol][i] / previousScore) - 1

            # This identifies if a player has permently stopped playing:
            if currentMonth == settings.seasonCol:
                lastMonth = (
                    1  # 1= The player is still playing in the last recorded month
                )
            elif loopNr == totalLoops:
                lastMonth = 0  # 0= He has permently stopped playing.
            else:
                lastMonth = 1
            # print(lastMonth, playerActivity[settings.SeasonNrCol][i],
            #       IndexesForPlayer[loopNr],
            #       IndexesForPlayer[1],
            #       loopNr
            #       )
            # This is a more broad variant of the lastMonth column, in which temporary quits are
            # also counted as quitting playing the game.
            # A player can come back after quitting after all.
            if lastMonth == 0:
                TMPandPermanentStop = 0  # the guy stoppped playin permanently (see lastMonth calculation above)
            elif (
                playerActivity[settings.SeasonNrCol][IndexesForPlayer[loopNr]]
                != playerActivity[settings.SeasonNrCol][i] + 1
            ):
                TMPandPermanentStop = 0  # If the next season is not the current season + 1, aka: the player skipped one or more months.
            else:
                TMPandPermanentStop = 1
            # Storing information for the dataframe using NP array:
            playerData.append(
                np.array(
                    [
                        playerActivity[settings.originalIDCol][i],
                        playerActivity[settings.seasonCol][i],
                        playerActivity[settings.userIDCol][i],
                        playerActivity[settings.scoreCol][i],
                        playerActivity[settings.rankCol][i],
                        playerActivity[settings.SeasonNrCol][i],
                        returning,
                        previousScore,
                        cumScore,
                        maxScore,
                        scoreChange,
                        monthsPlayed,
                        lastMonth,
                        monthsAFK,
                        TMPandPermanentStop,
                    ]
                )
            )

            # Storing score for next loop
            previousScore = playerActivity[settings.scoreCol][i]
            monthsPlayed = monthsPlayed + 1
            loopNr = loopNr + 1
        playerDatabase.append(playerData)
        # break (testing purposeses if only want to run one loop.)
    playerDatabase = np.concatenate(playerDatabase)
    playerDatabase = pd.DataFrame(
        playerDatabase,
        columns=[
            settings.originalIDCol,
            settings.seasonCol,
            settings.userIDCol,
            settings.scoreCol,
            settings.rankCol,
            settings.SeasonNrCol,
            settings.retrurningPlayerCol,
            settings.ScorePreviousMonthCol,
            settings.cumScoreCol,
            settings.maxScoreCol,
            settings.ScoreChangePercantageCol,
            settings.monthsPlayedCountCol,
            settings.FinalPlayedMonthCol,
            settings.MonthsAFKCol,
            settings.TMPandPermanentStopCol,
        ],
    )
    # print(playerDatabase[settings.FinalPlayedMonthCol].unique())
    playerDatabase = playerDatabase.astype(dtype=settings.dataTypesPreprocessedData)
    logger.info("Completed creating basic features")

    # This triggers the initial analysis module:
    playerDatabase = perfomInitialAnalysis(playerDatabase, settings)
    playerDatabase = Retention.addRetentionColumns(playerDatabase)

    # Save:
    playerDatabase.to_parquet(
        (settings.outputdir / settings.preProccessedFilename).absolute(), index=False
    )
    logger.info("Completed basic feature engineering")

    logger.info("Table contains the following columns:\n" + str(playerDatabase.dtypes))
    # logger.info()
