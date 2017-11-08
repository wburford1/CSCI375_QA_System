# CSCI375_QA_System
We will be using Python3 for this project.
## Package Syncing
Create a virtual environment called `venv` and connect to it:
```
$ python3 -m venv venv/
$ source venv/bin/activate
```
You should then see that you are connected to the `venv` vitual environment. You can now install the required packages using `pip`:
```
$ pip3 install -r requirements.txt
```
You can now run `pip3 freeze` to check that the packages have been installed.

## Running the Project
Once you are in the virtual environment with the all the dependencies installed (see above), you are ready to run the project. First edit `config.py` to set each variable to be the proper path on your system. It is already set up with the relative paths to answer questions that are provided in the repository.

You will then need to generate the answers file. To do this, run:
```
$ python3 main.py
```
The answer file that is created will be called `predictions.txt` and will be located in the same directory as `main.py`.

To evaluate the answers and calculate the MRR, run:
```
$ python evaluation.py answer-pattern-file prediction-file
```
Replace `answer-pattern-file` with the path to the answer patterns file to the question set on your system and `prediction-file` with the path to the prediction file. As an example, to evaluate on the training data set with the default prediction file name run the command:
```
$ python evaluation.py qadata/train/answer_patterns.txt predictions.txt
```

## Pre-predicted Answers
We have already run the QA system over both the training and the testing sets included in this repository. The prediction files for these can be found in `predictions-train.txt` and `predictions-test.txt` respectively.
