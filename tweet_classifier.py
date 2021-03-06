import numpy as np
import pandas as pd
import argparse

def load_csv(data_dir, filename):
    """
    Loades a pandas DataFrame df inside a data_dir folder with a filename.csv extension
    Robust for all OS because of pathlib module
    """
    import pandas as pd
    from pathlib import Path
    return pd.read_csv(Path(data_dir).joinpath(filename))

def normalize_document(doc):
    from nltk import WordPunctTokenizer
    from nltk.corpus import stopwords
    import re
    wpt = WordPunctTokenizer()
    stop_words = set(stopwords.words('portuguese'))
    # lowercase and remove special characters\whitespace
    doc = re.sub(r'[^a-zA-Z\s]', '', doc, re.I | re.A)
    doc = doc.lower()
    doc = doc.strip()
    # tokenize document
    tokens = wpt.tokenize(doc)
    # filter stopwords out of document
    filtered_tokens = [token for token in tokens if token not in stop_words]
    # re-create document from filtered tokens
    doc = ' '.join(filtered_tokens)
    return doc

normalize_corpus = np.vectorize(normalize_document)

def normalize_series(series):
    return normalize_corpus(series.to_numpy())

def classifier(df, text, target_label):
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    from sklearn.pipeline import Pipeline
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    train_corpus, test_corpus, train_label_names, test_label_names = train_test_split(
        df[text], df[target_label],
        test_size=0.2, random_state=42
    )
    clf = Pipeline(
        steps=[
            ('TF-IDF Vectorizer', TfidfVectorizer(use_idf=True, min_df=0.0, max_df=1.0)),
            ('RF Classifier', RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42))
        ])
    clf.fit(train_corpus, train_label_names)
    print(f"model accuracy: {clf.score(test_corpus, test_label_names):.3f}")
    print(classification_report(test_label_names, clf.predict(test_corpus)))
    return clf

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This script will use your clean by data_prep.py and classify the tweets', add_help=True)
    parser.add_argument(
        '-i', '--input', help="string file path for the input labeled CSV file")
    parser.add_argument(
        '-l', '--label', help="string with the label column that should be used for training the classifier, i.e. the 0/1 column")
    parser.add_argument(
        '-d', '--data', help="string file path for the data CSV file that you want to generate predictions")
    parser.add_argument(
        '-o', '--output', help="string file path for the output CSV file with predictions")
    args = parser.parse_args()
    df = pd.read_csv(args.input)
    df['text'] = normalize_series(df['text'])

    clf = classifier(df, 'text', args.label)

    full_df = pd.read_csv(args.data,
                        index_col=0,
                        names=['id', 'created_at', 'text', 'user_id', 'place', 'user_place', 'country', 'coordinates', 'undefined_col', 'undefined_col2', 'undefined_col3'])
    # Clean NAs in text
    print(f"We have {full_df.text.isna().sum()} NAs")
    full_df.dropna(subset=['text'], inplace=True)

    full_df['cleaned_text'] = normalize_series(full_df['text'])
    full_df['predicted'] = clf.predict(full_df['cleaned_text'])
    full_df['date'] = pd.to_datetime(full_df['created_at'])

    full_df.groupby(full_df['date'].dt.date).agg(
        {'predicted': 'sum'}).to_csv(args.output)
