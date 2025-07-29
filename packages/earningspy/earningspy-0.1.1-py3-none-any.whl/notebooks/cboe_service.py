import pandas as pd
import yfinance as yf
import requests
from io import StringIO

# ----------------------------
# Function to download CBOE CSV index data
# ----------------------------
def download_cboe_index(index_symbol: str) -> pd.DataFrame:
    """
    Downloads daily index data for a CBOE index from their public CSV files.
    E.g. index_symbol = 'BXM' or 'BXY' or 'PUT'
    """
    # CBOE hosts CSVs under a consistent URL pattern
    url_map = {
        "BXM": "https://cdn.cboe.com/api/global/us_indices/daily_prices/BXN_History.csv",
        "BXY": "https://cdn.cboe.com/api/global/us_indices/daily_prices/BXY_History.csv",
        "PUT": "https://cdn.cboe.com/api/global/us_indices/daily_prices/PUT_History.csv"
    }

    url = url_map.get(index_symbol)
    if not url:
        raise ValueError(f"No URL mapping found for index {index_symbol}")

    response = requests.get(url)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))
    df.columns = df.columns.str.strip() 
    df['DATE'] = pd.to_datetime(df['DATE'])
    return df

def get_cboe_data(days=90):

    bxm_df = download_cboe_index('BXM')
    bxy_df = download_cboe_index('BXY')
    put_df = download_cboe_index('PUT')

    cboe_df = bxm_df.merge(bxy_df, on='DATE', how='outer') \
                    .merge(put_df, on='DATE', how='outer')

    cboe_df = cboe_df.sort_values('DATE').tail(days)
    cboe_df.index = pd.to_datetime(cboe_df['DATE'])
    cboe_df = cboe_df.drop(columns=['DATE'])
    return cboe_df
