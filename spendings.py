

import csv
import os
import re
import pandas as pd

from os import path

'''


- may need to strip dollar signs from columns
- when joining, empty values end up as NaN. Might be fine.

- assert the totals row values correct.

- after joining all csvs, create a total spendings column.
- and nice to get more fine-grained, like percentages for sums of specific columns (aka categories).

'''

SOURCE_DIR = '/Users/michal/LeDocuments/finance/60percentbudget/2015_numbers'

ORIGINAL_COLUMN_NAME = 'Spending'

TOTALS_COLUMN = 'total'

def make_combined_csv():

    source_files = os.listdir(SOURCE_DIR)

    csv_files = [_file for _file in source_files if re.match(r'2015.*\.csv', _file)]

    print source_files
    print csv_files

    dfs = []

    for csv_file in csv_files:

        new_column_name = csv_file.split('.')[0]

        csv_file = path.join(SOURCE_DIR, csv_file)

        df = pd.read_csv(csv_file, index_col='Dates') #, parse_dates=True)

        df[new_column_name] = df[ORIGINAL_COLUMN_NAME]

        df = df.drop(ORIGINAL_COLUMN_NAME, axis=1)

        dfs.append(df)
    pass
    import ipdb; ipdb.set_trace()

    full_df = concat_data_frames(dfs)

    cleaned_df = clean_dollar_signs(full_df)

    new_df = sum_column(cleaned_df)

    import ipdb; ipdb.set_trace()
    
    pass

def sum_column(df):

    df[TOTALS_COLUMN] = df.sum(axis=1)

    return df

def clean_dollar_signs(df):

    #df.replace('$','',regex=True).astype('float')

    df = df.replace('\$','',regex=True).replace(',','',regex=True).astype('float')

    return df


def concat_data_frames(dfs):

    new_dataframe = pd.concat(dfs, axis=1)

    return new_dataframe
    


if __name__ == '__main__':
    make_combined_csv()

