import sys, os

def align_price_by_date(df1, df2, how='inner'):
    """
    Your DataFrame must be combined with `date` and `price` field

    Args:
        df1 (DataFrame): First DataFrame going to be aligned
        df2 (DataFrame): Second DataFrame going to be aligned
        how (str)      : Method to join DataFrame. `inner` or `outer`.
    Returns:
        DataFrame: Pandas DataFrame after aligned by date
    """
    try:
        dfp1 = df1[['date', 'price']]
        dfp2 = df2[['date', 'price']]
    except Exception as e:
        raise e

    # Align by merge
    # inner - both has data
    # outer - will have NaN
    df_m = dfp1.merge(dfp2, how=how, left_on='date', right_on='date')
    return df_m

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

