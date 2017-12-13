import sys, os

def count_corr(info1, info2):
    df1 = info1[['date', 'price']]
    df2 = info2[['date', 'price']]

    # Align by merge
    # inner - both has data
    # outer - will have NaN
    df_m = df1.merge(df2, how='inner', left_on='date', right_on='date')

    # Count correlation
    corr = df_m['price_x'].corr(df_m['price_y'])
    return corr

