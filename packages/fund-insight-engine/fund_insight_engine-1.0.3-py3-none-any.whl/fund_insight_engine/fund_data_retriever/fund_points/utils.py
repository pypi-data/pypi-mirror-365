from functools import partial
from mongodb_controller import COLLECTION_8186
from string_date_controller import get_first_date_of_year, get_date_n_days_ago
from fund_insight_engine.fund_data_retriever.fund_dates.initial_and_final import get_date_i_by_fund, get_date_f_by_fund
from .basis import get_point_menu8186

def set_dates_for_points_by_kernel(kernel, fund_code: str, date_ref=None):
    date_f = get_date_f_by_fund(fund_code)
    date_i = get_date_i_by_fund(fund_code)
    date_ref = date_ref if date_ref else date_f
    date_ytd = kernel(date_ref)
    if date_ytd < date_i:
        date_ytd = date_i
    return date_ytd, date_ref

set_dates_for_ytd_points = partial(set_dates_for_points_by_kernel, get_first_date_of_year)
set_dates_for_n_days_points = partial(set_dates_for_points_by_kernel, partial(get_date_n_days_ago, n_days=1))

def set_dates_for_ytd_points(fund_code: str, date_ref=None):
    date_f = get_date_f_by_fund(fund_code)
    date_i = get_date_i_by_fund(fund_code)
    date_ref = date_ref if date_ref else date_f
    date_ytd = get_first_date_of_year(date_ref)
    if date_ytd < date_i:
        date_ytd = date_i
    return date_ytd, date_ref

def set_dates_for_n_days_points(fund_code: str, date_ref=None, n_days=None):
    date_f = get_date_f_by_fund(fund_code)
    date_i = get_date_i_by_fund(fund_code)
    date_ref = date_ref if date_ref else date_f
    date_n_days_ago = get_date_n_days_ago(date_ref, n_days)
    if date_n_days_ago < date_i:
        date_n_days_ago = date_i
    return date_n_days_ago, date_ref

def get_fund_ytd(fund_code: str, date_ref=None):
    date_f = get_date_f_by_fund(fund_code)
    date_i = get_date_i_by_fund(fund_code)
    date_ref = date_ref if date_ref else date_f
    date_ytd = get_first_date_of_year(date_ref)
    if date_ytd < date_i:
        date_ytd = date_i
    price_ytd = get_point_menu8186(fund_code, date_ytd, '수정기준가')
    price_ref = get_point_menu8186(fund_code, date_ref, '수정기준가')
    return (price_ref / price_ytd - 1) * 100

def get_fund_n_days_return(fund_code: str, date_ref=None, n_days=None):
    date_f = get_date_f_by_fund(fund_code)
    date_i = get_date_i_by_fund(fund_code)
    date_ref = date_ref if date_ref else date_f
    date_n_days_ago = get_date_n_days_ago(date_ref, n_days)
    if date_n_days_ago < date_i:
        date_n_days_ago = date_i
    price_ref = get_point_menu8186(fund_code, date_ref, '수정기준가')
    price_n_days_ago = get_point_menu8186(fund_code, date_n_days_ago, '수정기준가')
    return (price_ref / price_n_days_ago - 1) * 100

