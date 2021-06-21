# Brazil-Tweet-Classifier

Brazil Twitter Classifier for COVID Symptoms

To run the classifier:
1. Insert all your data into the `data` folder
2. Create the conda environment with `conda env create -f environment.yml`
3. Run `python data_prep.py -h` for help
4. Run `python tweet_classifier.py -h` for help

## NLTK

You might have to run in python:

```python
import nltk
nltk.download('stopwords')
```
