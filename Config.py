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
    scrapedFileName: str = 'ScrapedData.csv'
    preProccessedFilename: str = 'PreProccessedData.csv'
    
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
    logScoreCol = str = 'logScore'       
    skillLevelCol = str = 'skillLevel'
    
        
settings = Settings()  # This object should be imported in other modules.
logger.add(settings.logdir / settings.logFile)
# print(settings.basedir)