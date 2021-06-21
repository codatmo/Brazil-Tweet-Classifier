import argparse
import pandas as pd

def concat_data(data_dir, extensions):
    """
    Loop for every data file in data_dir
    Robust for all OS because of pathlib module
    You should probably use like df = concat_data('data', {'.xlsx', '.xls'})
    """
    import pandas as pd
    from pathlib import Path
    return pd.concat([pd.read_excel(path)[['index', 'created_at', 'text', 'label']] for path in Path(data_dir).glob(r'**/*') if path.suffix in extensions])

def clean_labels(df, label_column):
    import pandas as pd
    """
    This function will for a given DataFrame df:
        1) remove NAs from the label_column
        2) normalize labels so that 1,2,3,4,6 is positive (1)
           and 99 is negative (0). 0 will be left unchanged.
           Also we filter out the label 5 because it is conspiracy theory label.
    """
    return df[df['label'] != 5].replace({label_column: {2: 1,
                                      3: 1,
                                      4: 1,
                                      6: 1,
                                      99: 0}}).dropna(subset=[label_column])


def save_csv(df, data_dir, filename):
    """
    Saves a pandas DataFrame df inside a data_dir folder with a filename.csv extension
    Robust for all OS because of pathlib module
    """
    import pandas as pd
    from pathlib import Path
    df.to_csv(Path(data_dir).joinpath(filename), index=False)

#df = concat_data('data', {'.xlsx'})
#df = clean_labels(df, 'label')
#save_csv(df, 'data', 'aggregated_data.csv')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script will clean your data and prepare for tweet_classifier.py', add_help=True)
    parser.add_argument('-i', '--input', help="string file path for the input CSV file")
    parser.add_argument('-l', '--label', help="string with the label column that should be prepped")
    parser.add_argument('-o', '--output', help="string file path for the output CSV file")
    args = parser.parse_args()
    df = pd.read_csv(args.input)
    df = clean_labels(df, args.label)
    df.to_csv(args.output)
