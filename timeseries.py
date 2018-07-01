import pandas as pd
import numpy as np
from functools import partial

def sample_id_hists(df, id_col, additional_sort_col=None, sort=True, **kwargs):         
    ids = pd.Series(df[id_col].unique())
    sorts = [id_col]
    if additional_sort_col is not None:
        sorts.append(additional_sort_col)
    if sort:
        df = df[df[id_col].isin(ids.sample(**kwargs))].sort_values(by=sorts)
    else:
        df = df[df[id_col].isin(ids.sample(**kwargs))]
    return df


def offset_from_first_event(group, date_col, event_col, event, period, find):
    group = group.sort_values(date_col)
    if event in group[event_col].values:
        if find == 'first':
            event_date_to_offset = (group[group[event_col] == event][date_col]
                                    .iloc[0]
                                    .to_period(period))
        if find == 'last':
            event_date_to_offset = (group[group[event_col] == event][date_col]
                                    .iloc[-1]
                                    .to_period(period))
        group[event_col+'_delta'] = group[date_col].dt.to_period(period) - event_date_to_offset
    else:
        group[event_col+'_delta'] = np.NaN
    return group


def event_delta(df, groupby_col, date_col, event_col, event=True, period='D', find='first'):
    """
    Returns pandas dataframe with new column containing offset from first event for each group.
    
    Arguments:
        df = pandas dataframe
        groupby_col = name of column to use for groups e.g. 'id'
        date_col = name of column containing time for offset
        event_col = name of column containing events of interest
        event = type of cell contents to look for, default is True
        period = string for pd.Series.dt offset alias, e.g. 'M' for months, 'D' for calendar days
        find = 'first' or 'last' to return offset from first or last occurence of event respectively
        """
    
    if event not in df[event_col].values:
        raise ValueError('No records contain event, will return NaN for every row.')    
    if find not in ['first', 'last']:
        raise ValueError("find argument should be either 'first' or 'last'")       
    
    partial_offset_func = partial(offset_from_first_event,
                                  date_col=date_col, 
                                  event_col=event_col, 
                                  event=event, 
                                  period=period,
                                  find=find)
    return df.groupby(groupby_col).apply(partial_offset_func).copy()
