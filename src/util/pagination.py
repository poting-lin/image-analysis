import pandas as pd


def paginate(df, pagination_params: pd.DataFrame) -> pd.DataFrame:
    """Selecting data to apply top and skip"""
    items_to_skip = pagination_params["skip"]
    top_number = pagination_params["top"]

    if items_to_skip:
        df = df.iloc[items_to_skip:]
    if top_number or top_number == 0:
        df = df.iloc[0:top_number]
    return df
