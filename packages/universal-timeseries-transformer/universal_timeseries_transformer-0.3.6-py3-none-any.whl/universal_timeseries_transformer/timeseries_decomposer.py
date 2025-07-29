import pandas as pd

def decompose_timeserieses_to_list_of_timeserieses(timeseries: pd.DataFrame) -> list[pd.DataFrame]:
    return [timeseries.iloc[:, [i]] for i in range(timeseries.shape[1])]

def concatenate_timeserieses(list_of_timeseries: list[pd.DataFrame]) -> pd.DataFrame:
    return pd.concat(list_of_timeseries, axis=1)

map_timeserieses_to_list_of_timeserieses = decompose_timeserieses_to_list_of_timeserieses
map_list_of_timeserieses_to_timeserieses = concatenate_timeserieses
