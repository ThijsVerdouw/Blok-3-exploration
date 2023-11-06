Description:
This is the code for the module data mining and exploration.

Installation:
1. Clone repository.
2. The dependancy manager used is poetry. Type poetry activate in the project folderto configure your Virtual environment.
3. Done (or if errow, use pip to install: pyarrow, requests, pydantic, scikit-learn, seaborn and loguru on python 3.11.5

How to run:
Run the main.py while your base directory is the project folder. It takes no arguments.

What does it do
1. Data collection (takes 30 minutes or so):
It uses requests to download the data from the official screeps website. This data is stored as a raw data parquet file in data/raw. This takes about 30 or so minutes.

2. Data preprocessing (takes up to 5 minutes):
It calculates a lot of attributes (for more information about those attributes see the word file in the docs folder). 
It does this in preprocessing.py, which calls in a lot of function from other modules in the src folder.

3. Analysis (takes 10-20 seconds):
The analysis ran by the code generates (hopefully) meaningful pictures. These pictures are stored in the output folder.

4. Modelling (takes about 5 minutes):
The models are trained on the preprocessed data. The models are evaluated, and then saved in the output folder as .pickle files.
This also generates the Confusion matrix.

FAQ:
I want to reload the raw data/preproccessed data/retrain the models?
Either delete the files or go to main() and set the appropriate optional variable (forceDownload, forcePreProcessing, ForceTraining) == True.
