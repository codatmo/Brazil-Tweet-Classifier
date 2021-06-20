import numpy as np
from pathlib import Path
import pandas as pd


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
    print(f"model score: {clf.score(test_corpus, test_label_names):.3f}")
    return clf

df = load_csv('data', 'aggregated_data.csv')

df['text'] = normalize_series(df['text'])

clf = classifier(df, 'text', 'label')


full_df = pd.read_csv(Path('data').joinpath('flu_pt_raw_tweets.csv'),
                      index_col=0,
                      names=['id', 'created_at', 'text', 'user_id', 'place', 'user_place', 'country', 'coordinates', 'undefined_col', 'undefined_col2', 'undefined_col3'])

# Clean NAs in text
print(f"We have{full_df.text.isna().sum()} 303 NAs")
full_df.dropna(subset=['text'], inplace=True)


full_df['cleaned_text'] = normalize_series(full_df['text'])

full_df['predicted'] = clf.predict(full_df['cleaned_text'])
full_df['date'] = pd.to_datetime(full_df['created_at'])

full_df.groupby(full_df['date'].dt.date).agg(
    {'predicted': 'sum'}).to_csv(Path('data').joinpath('tweet_count.csv'))
