# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 15:42:31 2023

@author: Admin
"""
import pandas as pd
import seaborn as sns
import numpy as np
from loguru import logger
import Config

settings = Config.Settings()
sns.set_theme(style="ticks")


def firstlook(fileName):
    # This function opens the preprocessed file and plots it in a series of boxplots.
    graphTitle = "Distribution of score by number of months played"
    logger.info("Graphing " + graphTitle)

    # The players who quit in the first month are out of scope:
    df = pd.read_parquet(fileName)
    # logger.info('Preprocessed file contains the following columns: ' +str(df.columns))

    # Originally did this without a log correction, behold: The most usless graph ever.
    # firstLook = sns.boxplot(x = 'monthsPlayed', y = 'score', data = df)

    df[settings.logScoreCol] = np.log10(df[settings.scoreCol])
    plt = sns.boxplot(x="monthsPlayed", y="logScore", data=df)
    plt.set(title=graphTitle, xlabel="Number of months played", ylabel="Score (log10)")
    plt.figure.savefig(
        str(settings.figdir) + "/" + graphTitle + ".jpg", format="jpg", dpi=600
    )

    # Clears figure so it does not fuck up the other graphs being generated.
    plt.figure.clear()
    logger.info("Saved " + graphTitle)
    return df


# print(df.head(5))


def assignSkillLevel(Lower_Fence, Q1, Q3, Upper_Fence, score):
    # This gives each player a "talent" rating, by assesing their performance on the second month.
    # The assesment is based on their position in the boxplot.
    if score >= Upper_Fence:
        rating = 5  #'Exceptional'
    elif score >= Q3:
        rating = 4  #'High'
    elif score >= Q1:
        rating = 3  #'Ok'
    elif (
        score >= 10000
    ):  # lower fence is WAAAY deep in the negatives, using "having ANY form of functionality in your bot" as
        rating = 2  #'Mediocre'
    else:
        rating = 1  #'Newby'
    return rating


def addSkillToDf(row, skillDatabase):
    # Adds the skill level of the player to all records associated to a player in the dataframe.
    try:
        rating = skillDatabase[row.user]
    except:
        rating = -1  # Not in dictionary because the user never played more than 1 month
    return rating


def identifySkillLevel(df, scoreColumnName):
    # This uses a single month to calculate a boxplot of the distribution of the score.
    # These are compiled into a dictionary, which is later used to assign the skill level to indiviudal players.
    # Not using settings.scoreCol because I want to be able to use this function flexibly for different types of scores.
    Q1 = df[scoreColumnName].quantile(0.25)
    Q3 = df[scoreColumnName].quantile(0.75)
    IQR = Q3 - Q1
    Lower_Fence = Q1 - (1.5 * IQR)
    Upper_Fence = Q3 + (1.5 * IQR)
    logger.info(
        "The player score thresholls for each skill level are quantified as such: \nLevel one is <10.000 as the lower fence is below zero: "
        + str(Lower_Fence)
        + "\n level 2 betwen 10.000 and the Q1:"
        + str(Q1)
        + "\n level 3 is between Q1 and Q3: "
        + str(Q3)
        + "\n level 4 is between Q3 and the UF: "
        + str(Upper_Fence)
        + "\n level 5 is greater than the upper fence."
    )
    skillDatabase = {"userName": 0}
    for i in df.index.tolist():
        skill = assignSkillLevel(
            Lower_Fence, Q1, Q3, Upper_Fence, df[scoreColumnName][i]
        )
        skillDatabase[df["user"][i]] = skill
    return skillDatabase


def graphData(graphType, y, data, x=None):
    # This allows me to flexibly graph the data whenever I want.
    if graphType == "BP":
        plt = sns.boxplot(x=x, y=y, data=data)
        plt.yaxis.get_major_formatter().set_scientific(False)
        plt.set(ylim=(0, max(data[y]) * 0.05))
    elif graphType == "HG":
        plt = sns.displot(y=y, data=data)
        # plt.yaxis.get_major_formatter().set_scientific(False)
        # plt.set(xlim=(0,100))
    elif graphType == "SP":
        plt = sns.scatterplot(x=x, y=y, data=data)
    else:
        logger.Warning("No graph selected")
    return plt


def singleMonthSelector(df, specificMonth):
    # Most things need only a single month of data, this function returns a single month of data.
    query = f"monthsPlayed =={specificMonth}"
    interestingMonth = df.query(query)
    return interestingMonth


def singeMonthView(df):
    # This plots the distribution of score for a single month and saves it.
    graphTitle = "Distribution of score for the second month played for all players"
    logger.info("Graphing " + graphTitle)

    # Make figure:
    plt = sns.displot(y=settings.logScoreCol, data=df)
    plt.set(title=graphTitle, xlabel="Number of players", ylabel="Score (log10)")
    plt.figure.savefig(
        str(settings.figdir) + "/" + graphTitle + ".jpg", format="jpg", dpi=600
    )

    # Clears figure so it does not fuck up the other graphs being generated.
    plt.figure.clear()
    logger.info("Saved " + graphTitle)


def GraphAssesment(settings, specificMonth=2):
    df = firstlook((settings.outputdir / settings.preProccessedFilename).absolute())
    singleMonthDF = singleMonthSelector(df, specificMonth=specificMonth)
    singeMonthView(df=singleMonthDF)

    # This graphs the skill level of the users in the selected month:
    graphTitle = "Distribution of skill level across unique players"
    logger.info("Graphing " + graphTitle)

    plt = sns.displot(x="skillLevel", data=df[["user", "skillLevel"]].drop_duplicates())
    plt.set(
        title=graphTitle, xlabel="Programming skill level", ylabel="Number of players"
    )
    plt.figure.savefig(
        str(settings.figdir) + "/" + graphTitle + ".jpg", format="jpg", dpi=600
    )

    # Clears figure so it does not fuck up the other graphs being generated.
    plt.figure.clear()
    logger.info("Saved " + graphTitle)


def getFileForStreamlit(fileName):
    # This function opens the preprocessed file and plots it in a series of boxplots.
    df = pd.read_parquet(fileName)
    return df
