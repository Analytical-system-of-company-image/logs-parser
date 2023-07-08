from datetime import datetime
from typing import List

from logs_analyzer.analyzer import LogsAnalyzer
from logs_analyzer.plots import (AbstractPlot, CountryPlot, IpPlot,
                                 PopularRegionsPlot, RegionPlot, TimePlot)
import pandas as pd

if __name__ == '__main__':

    need_plots: List[AbstractPlot] = []
    need_plots.append(IpPlot())
    need_plots.append(TimePlot())   
    need_plots.append(CountryPlot())
    need_plots.append(RegionPlot())
    need_plots.append(PopularRegionsPlot(3))
    logs_analyzer: LogsAnalyzer = LogsAnalyzer(need_plots)
    logs_analyzer.connect_db('server_logs', 'root', 'root', 27017)

    start = datetime(2021, 10, 9)
    end = datetime(2021, 10, 23)
    # end = datetime(2021, 10, 10)
    logs = logs_analyzer.read_from_db(start, end)
    # logs.to_csv('gorod_09102021_231021.csv',date_format='%Y/%m/%d/%H:%M:%S')
    
    logs_analyzer.analyze(logs)
