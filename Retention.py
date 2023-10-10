# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 16:47:30 2023

@author: Admin
"""
import pandas as pd 
import seaborn as sns
import numpy as np
from loguru import logger
import time
sns.set_theme(style='ticks')
scoreColumnName = 'score'
fileName = 'PreProcessedData.csv'
df = pd.read_csv(fileName)

sns.displot(x = 'monthsPlayed', data= df)

sumDf = df[['monthsPlayed', 'retentionRate']].copy()
sumDf = sumDf.groupby('monthsPlayed').mean()
sns.lineplot(x='monthsPlayed', y='retentionRate',
              data=sumDf)