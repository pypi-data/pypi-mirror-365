from functools import cached_property
from fund_insight_engine.price_retriever import get_timeserieses_price
from timeseries_performance_calculator import Performance

class Cluster:
    def __init__(self, tickers, benchmark_name=None, benchmark_index=-1):
        self.tickers = tickers
        self.benchmark_name = benchmark_name
        self.benchmark_index = benchmark_index
        self.prices = get_timeserieses_price(tickers)
        self.performance = Performance(timeseries=self.prices, benchmark_index=self.benchmark_index, benchmark_name=self.benchmark_name)

    @cached_property
    def prices(self):
        return self.performance.prices

    @cached_property
    def returns(self):
        return self.performance.returns
    
    @cached_property
    def cumreturns(self):
        return self.performance.cumreturns
    
    @cached_property
    def total_performance(self):
        return self.performance.total_performance
    
    @cached_property
    def period_returns(self):
        return self.performance.period_returns
    
    @cached_property
    def monthly_returns(self):
        return self.performance.monthly_returns
    
    @cached_property
    def yearly_returns(self):
        return self.performance.yearly_returns
    
    @cached_property
    def yearly_relative(self):
        return self.performance.yearly_relative
    