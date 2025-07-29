from functools import partial
from string_date_controller import get_date_n_days_ago
from fund_insight_engine.fund_data_retriever.timeseries.timeseries_utils import (
    get_df_menu8186_by_fund,
    set_index_of_timeseries,
    extend_price_timeseries_to_prev_date
)
from fund_insight_engine.market_retriever import (
    get_korea_indices,
    get_us_indices,
    get_currencies,
    get_korea_bonds,
    get_default_indices,
    get_compound_indices,
)
from fund_insight_engine.fund_data_retriever.fund_dates import (
    get_inception_date,
    get_latest_date_ref_in_configuration,
    get_default_date_ref,
)
from .fund_consts import KEYS_TO_PROJECT_FOR_FUND_PRICE, COL_FOR_FUND_PRICE

def get_corrected_prices(fund_code, start_date=None, end_date=None):
    if start_date is None:
        raw = get_df_menu8186_by_fund(fund_code=fund_code, end_date=end_date, keys_to_project=KEYS_TO_PROJECT_FOR_FUND_PRICE)
        df = (
            raw
            .pipe(set_index_of_timeseries)
            .pipe(extend_price_timeseries_to_prev_date)
        )
    else:
        prev_date = get_date_n_days_ago(start_date, 1)
        raw = get_df_menu8186_by_fund(fund_code=fund_code, start_date=prev_date, end_date=end_date, keys_to_project=KEYS_TO_PROJECT_FOR_FUND_PRICE)
        df = (
            raw
            .pipe(set_index_of_timeseries)
        )
    return df

def get_corrected_prices_with_indices(fund_code, start_date=None, end_date=None, option_indices='default'):
    prices_fund = get_corrected_prices(fund_code, start_date, end_date)

    get_kospi_indices = get_default_indices
    def get_kosdaq_indices(start_date=None, end_date=None):
        indices = get_default_indices(start_date=start_date, end_date=end_date)
        COLS_ORDERED = ['KOSDAQ Index', 'KOSPI Index', 'KOSPI2 Index', 'SPX Index']
        indices = indices[COLS_ORDERED]
        return indices
    
    mapping_indices = {
        'kr': get_korea_indices,
        'us': get_us_indices,
        'currency': get_currencies,
        'bond': get_korea_bonds,
        'default': get_default_indices,
        'compound': get_compound_indices,
        'KOSPI': get_kospi_indices,
        'KOSDAQ': get_kosdaq_indices,
    }
    kernel_indices = mapping_indices.get(option_indices, 'default')
    indices = kernel_indices(prices_fund.index[0], prices_fund.index[-1])
    prices = (
        prices_fund
        .join(indices)
        .pipe(lambda df: df.rename(columns={COL_FOR_FUND_PRICE: fund_code}))
    )
    return prices


def ensure_list(item):
    """Convert single item to list, keep lists as-is."""
    return [item] if isinstance(item, str) else list(item)


def get_timeseries_of_field_in_menu8186(fund_code, fields, start_date=None, end_date=None):
    fields = ensure_list(fields)
    raw = get_df_menu8186_by_fund(fund_code=fund_code, start_date=start_date, end_date=end_date, keys_to_project=['일자', *fields])
    df = (
        raw
        .pipe(set_index_of_timeseries)
    )
    return df

get_price = partial(get_timeseries_of_field_in_menu8186, fields='수정기준가')
get_nav = partial(get_timeseries_of_field_in_menu8186, fields='순자산')
get_aum = partial(get_timeseries_of_field_in_menu8186, fields='설정액')
get_units = partial(get_timeseries_of_field_in_menu8186, fields='설정좌수')
get_stock_proportion = partial(get_timeseries_of_field_in_menu8186, fields='주식순비율')
get_bond_proportion = partial(get_timeseries_of_field_in_menu8186, fields='채권순비율')

def get_proportions(fund_code, start_date=None, end_date=None):
    return get_timeseries_of_field_in_menu8186(fund_code, fields=['주식순비율', '채권순비율'], start_date=start_date, end_date=end_date).rename(columns={'주식순비율': 'Stock', '채권순비율': 'Bond'})


def correct_prices(prices):
    return(
        prices
        .copy()
        .pipe(set_index_of_timeseries)
        .pipe(extend_price_timeseries_to_prev_date)
    )