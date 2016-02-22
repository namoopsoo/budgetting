

import csv
import os
import re
import pandas as pd
import operator

from os import path

import datetime

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

    full_df = concat_data_frames(dfs)

    cleaned_df = clean_dollar_signs(full_df)

    new_df = sum_column(cleaned_df)

    save_to_file(new_df)
    
    pass

def save_to_file(df):

    now = datetime.datetime.now()

    new_name = now.strftime('summary_%H%m.csv')

    df.to_csv(new_name)


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
    

def derive_spendings_from_all_transactions(df):
    '''
Given df, from all transacrtions
from spendings import derive_spendings_from_all_transactions
df = pd.read_csv('2015_all_transactions/2015_all_transactions.csv')

derive_spendings_from_all_transactions(df)

    '''
    exclude_categories = ['Investments', 'Interest Income', 'Income',
            'Paycheck', 'Buy', 'Transfer', 
            ]

    query = reduce(operator.and_, [
        (df['Category'] != category) 
        for category in exclude_categories
        
        ])

    df_expense_transactions = df[query]


    # And for 'debit', negate that,
    negate = lambda x: x*-1

    '''
    how to fill out only the 'credit' items ? 
In [51]: df[df['Transaction Type'] == 'credit']['Amount'].map(negate).head()
Out[51]: 
1    -0.02
2    -0.54
3    -0.68
4    -5.08
5   -95.83
Name: Amount, dtype: float64
    '''
    

    #  401k contributions...
    #       'Deposit', 
    # 'Loans', 


if __name__ == '__main__':
    make_combined_csv()

