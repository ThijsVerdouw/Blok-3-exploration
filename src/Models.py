# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 11:35:41 2023

@author: Admin
"""

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
import pickle
from loguru import logger
import time
from sklearn.metrics import RocCurveDisplay, roc_curve

import Config

settings = Config.Settings()


def CollectDataForModelling(FileName, debug=False):
    # Collect dataframe

    if debug == True:
        df = pd.read_parquet(FileName).head(500)
    else:
        df = pd.read_parquet(FileName)
    # Remove all completely irrelevant columns:
    df = df[
        [
            settings.monthsPlayedCountCol,
            settings.skillLevelCol,
            settings.logScoreCol,
            settings.MassiveLossCol,
            settings.TMPandPermanentStopCol,
        ]
    ]
    logger.info(
        "The Dataset for the model contains the following columns: \n" + str(df.info())
    )

    # Assign X and Y
    y = df[settings.TMPandPermanentStopCol]
    X = df.drop(settings.TMPandPermanentStopCol, axis=1)

    return X, y


def PerformPreProcessing(X, y):
    # This function prepares the pipele: it defines the variables and
    # fills the preproceser

    # Create test split:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0
    )

    # This catagorises the columns into the correct types for preprocessing:
    numeric_features = [settings.monthsPlayedCountCol, settings.logScoreCol]
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy=settings.numericTransformerType)),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_features = [settings.skillLevelCol, settings.MassiveLossCol]
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown=settings.categoricalHandle_unknown)),
        ]
    )  # Dataset should not have unknowns, but kept it in just to be sure.

    # Preprocess catagorised data:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    clf = Pipeline(
        steps=[("preprocessor", preprocessor), ("classifier", LogisticRegression())]
    )
    clf.fit(X_train, y_train)
    logger.info(
        "Pre gridsearch model performance on a simple logistic regression classifier: %.3f"
        % clf.score(X_test, y_test)
    )
    time.sleep(1)  # the previous print gets fucked if this is to fast.
    return preprocessor, X_train, X_test, y_train, y_test


def trainModel(preprocessor, X_train, X_test, y_train, y_test):
    # Training the different models to compare them:
    classifiers = [
        #    ('svc-linear', SVC(kernel='linear')), # Too slow
        ("svc-kernel", SVC(C=1.0)),
        ("random-forest", RandomForestClassifier(n_estimators=100, max_depth=7)),
        ("naive bayes", GaussianNB()),
        # ('gaussian', GaussianProcessClassifier(copy_X_train = False, n_jobs=-1)),
        # Copy X train = True made my PC unable to handle it and it crashed: 64 GB ram btw.
        # https://stackoverflow.com/questions/49524761/scikit-learn-gaussianprocessclassifier-memory-error-when-using-fit-function
        # Even now it cannot handle it
        # Unable to allocate 66.7 GiB for an array with shape (8954230753,) and data type float64
        ("kNN", KNeighborsClassifier(n_neighbors=5)),
        ("decision tree", DecisionTreeClassifier(criterion="gini")),
    ]
    logger.info("Starting the training of the following models: " + str(classifiers))

    """
    I am running out of time, and I think preprocessing is not applied by
    the code commented out below. So I'm implementing the most ugly fix I know.
    UPDATE: I was correct. Applying preprocessing increased model performance 
    around the board py 0.03-0.04
    
    for i, (name, clf) in enumerate(classifiers):
        logger.info('Started traning ' + str(name))
        clf.fit(X_train, y_train)
        
        # Evaluate classifier:
        result = cross_val_score(clf, X_test, y_test, cv = cv, scoring='f1_macro')
        
        # Save classifier:
        pickle.dump(clf, open(str(settings.figdir) + "/" + str(name) + '.pickle', 'wb'))
        
        # Sterror
        mu = np.mean(result)
        stderr = np.std(result)/np.sqrt(cv)
    
        # add to Graph:
        plt.scatter(i, mu, label=name)
        plt.errorbar(i, mu, yerr=stderr)
        plt.legend(loc=3)
        logger.info('Completed training ' + str(name))
    
    # Visualise the quality of the different classifiers
    plt.xticks(np.arange(len(classifiers)), [name[0] for name in classifiers], rotation=45);
    plt.ylim(top=1)
    plt.ylim(bottom=0)
    plt.show()
    """

    name = "svc-kernel"
    clf = Pipeline(steps=[("preprocessor", preprocessor), ("svc-kernel", SVC(C=1.0))])
    clf.fit(X_train, y_train)
    logger.info("Score on svc-kernel : %.3f" % clf.score(X_test, y_test))
    pickle.dump(clf, open(str(settings.figdir) + "/" + str(name) + ".pickle", "wb"))
    time.sleep(1)  # the previous print gets fucked if this is to fast.

    name = "random-forest"
    clf = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("random-forest", RandomForestClassifier(n_estimators=100, max_depth=7)),
        ]
    )
    clf.fit(X_train, y_train)
    logger.info("Score on random-forest : %.3f" % clf.score(X_test, y_test))
    pickle.dump(clf, open(str(settings.figdir) + "/" + str(name) + ".pickle", "wb"))
    time.sleep(1)  # the previous print gets fucked if this is to fast.

    name = "naive bayes"
    clf = Pipeline(
        steps=[("preprocessor", preprocessor), ("naive bayes", GaussianNB())]
    )
    clf.fit(X_train, y_train)
    logger.info("Score on model : %.3f" % clf.score(X_test, y_test))
    pickle.dump(clf, open(str(settings.figdir) + "/" + str(name) + ".pickle", "wb"))
    time.sleep(1)  # the previous print gets fucked if this is to fast.

    name = "kNN"
    clf = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("kNN", KNeighborsClassifier(n_neighbors=5)),
        ]
    )
    clf.fit(X_train, y_train)
    logger.info("Score on kNN : %.3f" % clf.score(X_test, y_test))
    pickle.dump(clf, open(str(settings.figdir) + "/" + str(name) + ".pickle", "wb"))
    time.sleep(1)  # the previous print gets fucked if this is to fast.

    name = "decision tree"
    clf = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("decision tree", DecisionTreeClassifier(criterion="gini")),
        ]
    )
    clf.fit(X_train, y_train)
    pickle.dump(clf, open(str(settings.figdir) + "/" + str(name) + ".pickle", "wb"))
    logger.info("Score on decision tree : %.3f" % clf.score(X_test, y_test))
    time.sleep(1)  # the previous print gets fucked if this is to fast.


def ConfusionMatrix (X, y, ModelName):
    """
    

    Parameters
    ----------
    X : array
        Actual X in preprocessed file.
    y : array
        Actual Y in preprocced file.
    ModelName : str
        Name of model to be loaded in.

    Returns
    -------
    None.

    """
    logger.info('Calculating confusion matrix for: ' + ModelName)
    clf = pickle.load(open(str(settings.figdir) + "/"+ ModelName + ".pickle", 'rb'))
    # X_ = preprocessor.fit_transform(X) (IS DIT NODIG??!??) hET LIJKT AUTOMATICH
    y_pred = clf.predict(X)
    cm = confusion_matrix(y, y_pred)
    cm_display = ConfusionMatrixDisplay(cm).plot()
    cm_display.ax_.set_title('Confusion matrix for ' + ModelName)
    cm_display.ax_.figure.savefig(str(settings.figdir) + "/" + ModelName + ".jpg", format="jpg", dpi=600)
    cm_display.ax_.figure.clear()
    # Random forest heeft geen .desicion function dus broken dus screw de ROC, tijd is op:
    # y_score = clf.decision_function(y)
    # fpr, tpr, _ = roc_curve(y_test, y_score, pos_label=clf.classes_[1])
    # roc_display = RocCurveDisplay(fpr=fpr, tpr=tpr).plot()

def TrainModels(FileName):
    X, y = CollectDataForModelling(FileName)
    preprocessor, X_train, X_test, y_train, y_test = PerformPreProcessing(X, y)
    trainModel(preprocessor, X_train, X_test, y_train, y_test)
    for model in settings.includedModels:
        ConfusionMatrix(X, y, model)

# FileName = (settings.outputdir / settings.preProccessedFilename).absolute()
# TrainModels(FileName)



"""
def gridsearchtooslow():
    pass 
    # Do a Grid Search and automatically fit using best parameters:
    # Instantiate GridSearchCV
    # [10**x for x in range(-3,3)]
    
    # Set parameter grid
    
    
    # Set parameter grid
    # zoom in on what looks like a usefull are for C and gamma
    # param_grid = {
    #     'C': np.linspace(10, 500, 20),
    #     'gamma': np.linspace(1e-7, 1e-3, 20),
    #     }
    
    
    # # often it is usefull to fiddle with the vmin to increase the contrast of colors
    # grid_search = train_model.search_and_fit(model=SVC(),
    #                                          X=X_train, 
    #                                          y=y_train, 
    #                                          param_grid=param_grid, 
    #                                          vmin=0.7,
    #                                          figsize=(15,15),
    #                                          cv = 3)
    
    # # Print best parameters and corresponding score
    # best_parameters = grid_search.best_parameters
    # best_score = grid_search.best_score
    
    # logger.info("Best parameters:  {}".format(best_parameters))
    # logger.info("Best score:       {:.2f}".format(best_score))
    
    # logger.info(grid_search)
    
    # plt = sns.heatmap(gridsearch_heatmap(grid_search, param_grid, figsize=(8,8))
"""
