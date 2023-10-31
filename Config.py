# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 10:07:51 2023

@author: Admin
"""

from pathlib import Path
from loguru import logger
from pydantic import BaseModel


class Settings(BaseModel):
    # Paths:
    basedir: Path = Path.cwd()
    datadir: Path = Path("data/raw")
    outputdir: Path = Path("data/processed")
    logdir: Path = basedir / "log"
    logFile: str = 'logfile.log'
    scrapedFileName: str = 'ScrapedData.parquet'
    preProccessedFilename: str = 'PreProccessedData.parquet'
    analysedFile : str = 'ProcessedData.parquet'
    
    # API & values used in the download:
    countRecordsLink: str = 'https://screeps.com/api/leaderboard/list?limit=10&mode=world&offset=NaN&season='
    downloadLink: str = 'https://screeps.com/api/leaderboard/list?limit=20&mode=world&offset='
    startYear: int = 2015
    
    # Column names in raw data download:
    originalIDCol: str = '_id' 
    seasonCol: str = 'season' 
    userIDCol: str = 'user'
    scoreCol: str = 'score'
    rankCol: str = 'rank'
    totalRecordsCol: str = 'count'
    
    # Raw data inputs:
    MonthNrForSkillLevel: int = 2
    MonthNrForPlayerType: int = 3

    # Engineered features column names:
    SeasonNrCol: str = 'SeasonNumber'
    retrurningPlayerCol: str ='returning'
    ScorePreviousMonthCol: str ='previousScore'
    cumScoreCol: str ='cumScore'
    maxScoreCol: str ='maxScore'
    ScoreChangePercantageCol: str ='scoreChange'
    monthsPlayedCountCol: str ='monthsPlayed'
    FinalPlayedMonthCol: str ='retentionRate'
    MonthsAFKCol: str ='monthsAFK'
    playerTypeCol: str = 'PlayerType'
    logScoreCol:  float = 'logScore'       
    skillLevelCol: int = 'skillLevel'
    threeMonthsAFKCol: str = 'threeMonthsAFK'
    SixMonthsAFKCol: str = 'SexMonthsAFK'
    TwelveMonthsAFKCol: str = 'TwelveMonthsAFK'
    MassiveLossCol: str = 'MassiveLoss'
    
    # Data types for the dataframes:
    dataTypesRawData: dict = { 
        # Column names in raw data download:
        originalIDCol: str,
        seasonCol: str,
        userIDCol: str,
        scoreCol: float,
        rankCol: int
        }
        
    dataTypesPreprocessedData: dict = {        
        # Column names in raw data download:
        originalIDCol: str,
        seasonCol: str,
        userIDCol: str,
        scoreCol: float,
        rankCol: int,

        # Engineered features column names:
        SeasonNrCol: int,
        retrurningPlayerCol: int,
        ScorePreviousMonthCol: float,
        cumScoreCol: float,
        maxScoreCol: float,
        ScoreChangePercantageCol: float,
        monthsPlayedCountCol: float,
        FinalPlayedMonthCol: int,
        MonthsAFKCol: int
                       }
    
        
settings = Settings()  # This object should be imported in other modules.

# print(settings.dataTypes[settings.originalIDCol])