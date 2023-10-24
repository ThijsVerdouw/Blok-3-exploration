# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 11:21:34 2023

@author: Admin
"""

import Config
import Download
import Preprocessing
from loguru import logger
import os


def createPathIfNeeded (Path):
    # Check whether the specified path exists or not
    if not os.path.exists(Path):
        # Create path
        logger.info('Path to ' + str(Path) + ' did not exist. \n Created path.')
        os.makedirs(Path)
    else:
        logger.info('Path to ' + str(Path) + ' existed already.')

def main(forceDownload = False, forcePreProcessing = False):
    # initializing settings.Settings()
    settings = Config.Settings()
    RawFile = (settings.datadir / settings.scrapedFileName).absolute()
    createPathIfNeeded(settings.datadir)
        
    # If the raw data has not been downloaded, download it:
    if not RawFile.exists() or forceDownload == True:
        logger.warning(f"file {RawFile} does not exist")
        Download.DownloadLeaderboard(settings.startYear)
    
    createPathIfNeeded(settings.outputdir)
    PreProccessedFile = (settings.outputdir / settings.preProccessedFilename).absolute()
    # If the data has not been preproccessed
    if not PreProccessedFile.exists() or forceDownload == True:
        Preprocessing.basicFeatureCreation(RawFile, settings)


main(forcePreProcessing = True)