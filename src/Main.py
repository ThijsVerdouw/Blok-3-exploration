# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 11:21:34 2023

@author: Admin
"""

import Config
import Download
import Preprocessing
import warnings
from loguru import logger
# import streamlit as st
import os
import InitialAnalysis
import Retention
import ScoreGrowth
import Models


def createPathIfNeeded (Path):
    # Check whether the specified path exists or not
    if not os.path.exists(Path):
        # Create path
        logger.info('Path to ' + str(Path) + ' did not exist. \n Created path.')
        os.makedirs(Path)
    else:
        # logger.info('Path to ' + str(Path) + ' existed already.')
        pass

def main(forceDownload = False, 
         forcePreProcessing = False, 
         InitialGraphing = True,
         RetentionGraphing= True,
         ScoreGraphing = True,
         ForceTrainingModels = False,
         Streaming = False):
    # initializing settings:
    settings = Config.Settings()
    createPathIfNeeded(settings.logdir)
    logger.add(settings.logdir / settings.logFile)
    
    # Getting raw data:
    RawFile = (settings.datadir / settings.scrapedFileName).absolute()
    createPathIfNeeded(settings.datadir)
        
    # If the raw data has not been downloaded, download it:
    if not RawFile.exists() or forceDownload == True:
        logger.warning(f"file {RawFile} does not exist")
        Download.DownloadLeaderboard(settings.startYear)
    
    # Preprocessing raw data:
    createPathIfNeeded(settings.outputdir)
    PreProccessedFile = (settings.outputdir / settings.preProccessedFilename).absolute()
    # If the data has not been preproccessed
    if not PreProccessedFile.exists() or forcePreProcessing == True:
        logger.warning(f"file {PreProccessedFile} does not exist")
        Preprocessing.basicFeatureCreation(RawFile, settings)
    
    # Visualising and saving results:
    createPathIfNeeded(settings.figdir)
    if InitialGraphing == True:
        InitialAnalysis.GraphAssesment(settings)
        
    if RetentionGraphing == True:
        Retention.PerformRetentionAnanlyis(PreProccessedFile)
    
    if ScoreGraphing == True:
        ScoreGrowth.identifyImpactOfLeaving (PreProccessedFile)
    
    # checking if the last model in the list has been trained:
    ModelPath = (settings.figdir / settings.includedModels[4]).absolute() 
    if not ModelPath.exists() or ForceTrainingModels == True:
        Models.TrainModels(PreProccessedFile)

    # if Streaming == True:
    #     df = InitialAnalysis.getFileForStreamlit(PreProccessedFile)
    #     st.session_state.allData = df.head(100)

    #     option1 = st.selectbox(
    #         "Select the x-axis",
    #         st.session_state.allData.columns,
    #         index=2,
    #     )
    #     option2 = st.selectbox(
    #         "Select the y-axis",
    #         st.session_state.allData.columns,
    #         index=3,
    #     )
    #     color = st.selectbox("Select the color", st.session_state.allData.columns, index=0)

    #     fig, ax = plt.subplots()

    #     option1 = settings
    #     sns.scatterplot(data=st.session_state.allData, x=option1, y=option2, hue=color)

    #     st.pyplot(fig)
    
if __name__ == "__main__":
    main()
# main(forcePreProcessing= False, ForceTrainingModels = True)
# main()