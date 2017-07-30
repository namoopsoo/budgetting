A bit of code to extend some of the analytics that mint.com categorical data offers.



```python

In [1]: filename = 'blahdata/raw/2017-07-30-raw-all-transactions.csv'

In [3]: import spendings as spends


In [4]: df_original = spends.read_mint_csv(filename)

In [14]:     df_0 = spends.remove_some_cols(df_original)

In [15]:     df_1 = spends.annotate_negate_credits(df_0)

In [19]:     df_2 = spends.annotate_make_month_col(df_1) 

In [25]: dfgroceries = df_2[df_2.Category == 'Groceries']

In [31]: dfgroceries_12mo = dfgroceries[dfgroceries.Month >= '2016-08']


```

