# from fund_insight_engine import get_timeseries_price
from .performance import Performance

class Seasonality:
    def __init__(self, timeseries, benchmark_timeseries):
        self.timeseries = timeseries
        self.benchmark_timeseries = benchmark_timeseries
        self.perf = Performance(timeseries=timeseries, benchmark_timeseries=benchmark_timeseries)

    def get_seasonality(self, index_name):
        return self.perf.get_seasonality(index_name)
    
    def get_relative_seasonality(self, index_name):
        return self.perf.get_relative_seasonality(index_name)
    

# class Seasonality:
#     def __init__(self, ticker, benchmark_ticker):
#         self.ticker = ticker
#         self.benchmark_ticker = benchmark_ticker
#         self.timeseries = get_timeseries_price(ticker)
#         self.benchmark_timeseries = get_timeseries_price(benchmark_ticker)
#         self.loader = SeasonalityLoader(ticker, benchmark_ticker)

#     def get_seasonality(self, index_name):
#         return self.loader.perf.get_seasonality(index_name)
    
#     def get_relative_seasonality(self, index_name):
#         return self.loader.perf.get_relative_seasonality(index_name)