
import sys
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

- wish item for wishlist: do some clever budget balancing maths with the 'Credit Card Payment' type.

'''


ORIGINAL_COLUMN_NAME = 'Spending'

TOTALS_COLUMN = 'total'

EXPENSE_CATEGORIES = [
        'State Tax', 'Mobile Phone', 'Pantalones Fancy', 'Pharmacy', 'Student Loan', 'Music', 'Fast Food', 'Home Supplies', 'TheRent', 'Shopping', 'Dessert', 'Gym', 'Coffee Shops', 'Fees & Charges', 'Utilities', 'ATM Fee', 'Electronics & Software', 'BooksMagazines', 'Incidental ZipCar', 'Charity', 'Wash & Fold', 'Television', 'Furnishings', 'Gift', 'Business Services', 'club', 'Financial Advisor', 'Food & Dining', 'Federal & State Tax', 'Uncategorized', 'SportsForHealth', 'Sports', 'Restaurants', 'Movies & DVDs', 'Public transit', 'Haircut', 'BarsAndAlcohol', 'Books', 'Groceries', 'Hobbies', 'Sports Fun', 'Clothing', 'Amusement',
        'Home Improvement', 'Late Night Taxi', 'GreyHound', 'FriendLoan', 'Doctor',
        'Home Services', 'Shipping', 'Workshops/Seminars', 'FianceLoan',
        'Vacation Gas Pers', 'Vacation Travel Pers', 'Vacation Hotel Pers']

OTHER_EXPENSE_CATEGORIES = [

]

INCOME_CATEGORIES = ['Interest Income', 'Paycheck']
TRANSFER_CATEGORIES = ['Credit Card Payment', 'Transfer', 'Transfer for Cash Spending']

OTHER_CATEGORIES = []


EXPENSE_CATEGORY_PARENTS = {
        #
        'Entertainment': [
            'Pantalones Fancy', 'Late Night Taxi',
            'BarsAndAlcohol', 'Amusement', 'BooksMagazines', 'Books',
            'Music', 'Fun Electronics',
            ],
        'Taxes': [
            'Federal & State Tax', 'State Tax',
            ],
        'Health': [
            'Doctor', 'Pharmacy', 'Dentist', 'Gym',
            'Races', 'SportsForHealth',
            ],
        'Personal Care': [
            'Vacation Gas Pers', ''
            ],
        'Utilities': [
            'TheRent', 'Mobile Phone',
            ],
        'Travel': [
            'GreyHound', 'Public transit', 'Bike Maintenance'
            ],
        'Food & Dining': [
            'Groceries', 'Restaurants', 'Coffee Shops'
            ],
        'Gifts & Donations': ['Gift'],
        'Shopping': ['Clothing', 'Electronics & Software',
            'Shopping',
            ],
        'Transfer': ['Investments', 
            'Buy', 'Transfer', 'Credit Card Payment',
            'Transfer for Cash Spending',
            ],
        'Income': ['Interest Income', 'Paycheck'],
        'Fees & Charges': ['ATM Fee', ],
        'Business Services': ['Legal', 'Document Shredding',
            'Office Supplies'],


        # 
    }
'''
oops... still need to account for parents for these...
In [73]: print list(df_2[df_2['Parent Category'] == ''][['Category', 'Parent Category']]['
    ...: Category'].value_counts().keys())
['Transfer', 'Credit Card Payment', 'Interest Income', 'Dessert', 'ATM Fee', 'Transfer for Cash Spending', 'Student Loan', 'Paycheck', 'Electronics & Software', 'Movies & DVDs', 'Investments', 'Dividend & Cap Gains', 'Incidental ZipCar', 'Buy', 'Charity', 'Vacation Travel Pers', 'Music', 'Public Radio', 'Health Insurance', 'Payroll Taxes', 'Shopping', 'Gas & Fuel', 'Utilities', 'Income', 'Wash & Fold', 'Sporting Goods', 'Vacation Hotel Pers', 'Home Improvement', 'Sell', 'Shipping', 'Local Tax', 'Disability Insurance', 'Home Services', 'Haircut', 'Fees & Charges', 'Loans', 'Incidental EZ_Pass', 'Video Games', 'Uncategorized', 'club', 'Sports Fun', 'Financial Advisor', 'Finance Charge', 'Service Fee', 'Home Supplies', 'Travel Parking', 'Healthcare FSA', 'Printing', 'Newspapers & Magazines', 'Business Services', 'Hobbies', 'Furnishings', 'Entertainment', 'Deposit', 'Reimbursement', 'Arts', 'FianceLoan', 'Workshops/Seminars', 'Donation', 'Check', 'Mortgage & Rent', 'Car Insurance', 'Travel', 'Office Supplies', 'EZ Pass', 'Personal Care', 'Fun Electronics', 'Vacation Finance Fee', 'Gifts & Donations', 'Bank Fee', 'Trade Commissions', 'Parking', 'Alcohol & Bars', 'Public Transportation', 'Car Maintenance', 'CorporateInvestment', 'Television', 'Service & Parts', 'Internet/Phone', 'Loan Repayment', 'Late Fee', 'FriendLoan', 'Loan Payment', 'Baby Supplies', 'Taxes', 'Financial', 'Health & Fitness', 'Bills & Utilities', 'Education', 'Fast Food', 'Tuition', 'Air Travel', 'Sports', 'Incident Taxi', 'Food & Dining', 'Misc Expenses', 'Lawn & Garden']

'''

def make_reverse_mapping(parent_categories):
    mappings = {}
    for parent, sub_categories in parent_categories.items():
        for sub_category in sub_categories:
            assert sub_category not in mappings,\
                    '{} should not be in {}'.format(sub_category,
                            mappings)
            mappings[sub_category] = parent

    return mappings

REVERSE_PARENT_MAPPINGS = make_reverse_mapping(EXPENSE_CATEGORY_PARENTS)

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

def get_month(d):
    return '{}-{}'.format(d.year, str(d.month).zfill(2))

def annotate_make_month_col(df):
    ''' Add an extra column for the YYYY-MM month.
    '''
    df['Month'] = df['Date'].apply(get_month)
    return df 

def get_parent_category(i):
    parent = REVERSE_PARENT_MAPPINGS.get(i, '')
    return parent

def annotate_parent_categories(df):
    ''' Given a df with 'Category' column, add the 'Parent Category'
    column as well
    '''
    df['Parent Category'] = df['Category'].apply(get_parent_category)
    return df 

def derive_df_with_aggregated_spendings_per_category_per_month(
        df, categories):
    ''' So for a given arbitrary number of row df, which has all
    transactions, return a df which has, <categories>-many rows 
    for each month in the df.

    That way, the resulting output df can be used to produce a plot,
    of the variation in spending per category, along a time x axis.

    '''


def remove_some_cols(df):
    df = df.drop(labels=['Original Description', 'Labels', 'Notes'], axis=1)
    return df


def make_df_with_month_category_aggregates(df_original):
    '''
    Expecting an input df which comes from a csv dump of all transactions from Mint.
    '''

    # TODO ... may actually want to exclude some categories...
    df_0 = remove_some_cols(df_original)


    path.join(settings.SOURCE_DIR, source_file)

    # Negate those credits...
    df_1 = annotate_negate_credits(df_0)
    df_1.to_csv('{}/df_1_2009-2016.{}.csv'.format(settings.SOURCE_DIR, make_timestamp()))

    df_2 = annotate_make_month_col(df_1) 
    grp = df_2.groupby(by=['Month', 'Category'])
    df_1_sums = grp.aggregate({'Amount': sum})
    df_1_sums.to_csv('{}/df_1_sums_2009-2016.{}.csv'.format(settings.SOURCE_DIR, make_timestamp()))

    df_3 = annotate_parent_categories(df_2)
    df_3.to_csv('{}/df_3_2009-2016.{}.csv'.format(settings.SOURCE_DIR, make_timestamp()))

    grp3 = df_3.groupby(by=['Month', 'Parent Category'])
    df_3_sums = grp3.aggregate({'Amount': sum})
    df_3_sums.to_csv('{}/df_3_sums_2009-2016.{}.csv'.format(settings.SOURCE_DIR, make_timestamp()))


def grocery_store_pivot_table(df):
    stores = ['Whole Foods', "Trader Joe's", 'Fairway', 'Costco',
            'Amazon', 'Amazon Fresh',
            'Costco Whole Foods', 'Fresh Market', 
            ]
    df = dfgroceries_12mo
    pivot = pd.DataFrame.pivot_table(df, 
            values='Amount', index='Month', 
            columns='Description', aggfunc=np.sum)
    return pivot


def main_driver_example(source_file):
    import ipdb; ipdb.set_trace()
    source_file = path.join(settings.SOURCE_DIR, source_file)

    # 'data/2009_01-2016_11_transactions.csv'
    df = read_mint_csv(source_file)
    make_df_with_month_category_aggregates(df)

    # Then on a jupyter notebook, I was able to use ...
    # ax = df.groupby(["Parent Category", "Month"]).mean().unstack("Parent Category").plot()
    # and this gave a nice time series plot. But only after using the required preamble...
    #
    # %matplotlib inline
    # df = pd.read_csv('data/df_3_sums_2009-2016.2016-11-11T1302.csv')
    # ...
    pass


def make_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%dT%H%M')


def annotate_negate_credits(df):
    '''
    Make credits negative, but only for expense categories
    '''
    negate = lambda x: x*-1

    query = make_query_from_categories(df, EXPENSE_CATEGORIES)
    amounts = df[df['Transaction Type'] == 'credit' ][query]['Amount']
    amounts_negateds = amounts.map(negate)

    # This below method didnt work.
    # df[df['Transaction Type'] == 'credit' ][query]['Amount'] = amounts_negateds

    # But this did.
    df.loc[((df['Transaction Type'] == 'credit') & query), 'Amount'] = amounts_negateds

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


def combine_queries(df, queries):
    query = reduce(operator.and_, queries)
    return query


def read_mint_csv(csv_file):
    ''' Read a mint csv file,
    with Date being the col that has the mm/dd/yyyy transaction date.
    '''
    df = pd.read_csv(csv_file, parse_dates=['Date'])
    return df

def cool_date_query_example(df):
    jun1 = datetime.date( 2016,6,1)
    df[df['Date'] < jun1][['Date', 'Amount', 'Category']].head()


def make_queries_for_date_range(df, date_begin, date_end):
    queries = [
            df['Date'] < date_end,
            df['Date'] >= date_begin,
            ]
    return queries

def get_data_for_categories(df):

    category_query = df['Category'] == 'Pantalones Fancy'


    may1 = datetime.date(2016,5,1)
    jun1 = datetime.date(2016,6,1)
    date_queries = make_queries_for_date_range(df, may1, jun1)



    query = combine_queries(df, queries)





if __name__ == '__main__':
    if len (sys.argv) != 2:
        sys.exit('format: foo.py transactions.csv')

    source_file = sys.argv[1]
    main_driver_example(source_file)

