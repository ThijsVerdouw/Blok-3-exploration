Description:
This is the code for the module data mining and exploration.

Installation:
1. Clone repository.
2. The dependancy manager used is poetry. Run the lock file with poetry to configure your Virtual environment.
3. Done

How to run:
Run the main.py while your base directory is the project folder. It takes no arguments.

What does it do
1. Data collection:
It uses requests to download the data from the official screeps website. This data is stored as a raw data parquet file in data/raw. This takes about 30 or so minutes.

2. Data preprocessing:
It calculates a lot of attributes (for more information about those attributes see the word file in the docs folder). 
It does this in preprocessing.py, which calls in a lot of function from other modules in the src folder.

3. Analysis:
The analysis ran by the code generates (hopefully) meaningful pictures. These pictures are stored in the output folder.

4. Modelling:
The models are trained on the preprocessed data. The models are evaluated, and then saved in the output folder as .pickle files.

FAQ:
I want to reload the raw data/preproccessed data/retrain the models?
Either delete the files or go to main() and set the appropriate optional variable (forceDownload, forcePreProcessing, ForceTraining) == True.