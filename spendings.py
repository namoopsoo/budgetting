

import csv
import os
import re
import pandas as pd
import operator

from os import path

import datetime

import settings
'''


- may need to strip dollar signs from columns
- when joining, empty values end up as NaN. Might be fine.

- assert the totals row values correct.

- after joining all csvs, create a total spendings column.
- and nice to get more fine-grained, like percentages for sums of specific columns (aka categories).

'''


ORIGINAL_COLUMN_NAME = 'Spending'

TOTALS_COLUMN = 'total'

EXPENSE_CATEGORIES = [
        'State Tax', 'Mobile Phone', 'Pantalones Fancy', 'Pharmacy', 'Student Loan', 'Music', 'Fast Food', 'Home Supplies', 'TheRent', 'Shopping', 'Dessert', 'Gym', 'Coffee Shops', 'Fees & Charges', 'Utilities', 'ATM Fee', 'Electronics & Software', 'BooksMagazines', 'Incidental ZipCar', 'Charity', 'Wash & Fold', 'Television', 'Furnishings', 'Gift', 'Business Services', 'club', 'Financial Advisor', 'Food & Dining', 'Federal & State Tax', 'Uncategorized', 'SportsForHealth', 'Sports', 'Restaurants', 'Movies & DVDs', 'Public transit', 'Haircut', 'BarsAndAlcohol', 'Books', 'Groceries', 'Hobbies', 'Sports Fun', 'Clothing', 'Amusement']


def make_combined_csv():

    source_files = os.listdir(settings.SOURCE_DIR)

    csv_files = [_file for _file in source_files if re.match(r'2015.*\.csv', _file)]

    print source_files
    print csv_files

    dfs = []

    for csv_file in csv_files:

        new_column_name = csv_file.split('.')[1]

        csv_file = path.join(settings.SOURCE_DIR, csv_file)

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

def make_query_from_categories(df, categories):
    query = reduce(operator.or_, [
        (df['Category'] == category) 
        for category in categories
        ])
    
    return query

def get_month(i):
    return i.month + i.year

def annotate_make_month_col(df):
    df['Month'] = df['Date'].apply(get_month)
    return df 


def annotate_negate_credits(df):
    '''
    Make credits negative, but only for expense categories
    '''
    negate = lambda x: x*-1

    query = make_query_from_categories(df, EXPENSE_CATEGORIES)
    
    amounts = df[df['Transaction Type'] == 'credit' ][query]['Amount']

    amounts_negateds = amounts.map(negate)

    df[df['Transaction Type'] == 'credit' ][query]['Amount'] = amounts_negateds


    return df

def derive_spendings_from_all_transactions(df):
    '''
Given df, from all transacrtions
from spendings import derive_spendings_from_all_transactions
df = pd.read_csv('2015_all_transactions/2015_all_transactions.csv')

derive_spendings_from_all_transactions(df)


- This is using a file all_transactions.csv  , with columns:

    Date: 12/31/15
    Description: string
    Amount: float
    Transaction Type: debit, credit
    Category: Restaurants, Interest Income, ...
    Account Name: Visa Platinum, contingency, ...


    '''
    exclude_categories = ['Investments', 
            'Buy', 'Transfer', 'Credit Card Payment', 'Transfer for Cash Spending',
            ]

    income_categories = ['Interest Income', 'Income',
            'Paycheck', 
            ]

    expense_categories = []


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

