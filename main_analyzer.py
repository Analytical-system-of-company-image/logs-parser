from datetime import datetime
from typing import List

from logs_analyzer.analyzer import LogsAnalyzer
from logs_analyzer.plots import (AbstractPlot, CountryPlot, IpPlot,
                                 PopularRegionsPlot, RegionPlot, TimePlot)

if __name__ == '__main__':

    need_plots: List[AbstractPlot] = []
    need_plots.append(IpPlot())
    need_plots.append(TimePlot())
    need_plots.append(CountryPlot())
    need_plots.append(RegionPlot())
    need_plots.append(PopularRegionsPlot(3))
    logs_analyzer: LogsAnalyzer = LogsAnalyzer(need_plots)
    logs_analyzer.connect_db('server_logs', 'root', 'root', 27017)

    start = datetime(2021, 3, 1)
    end = datetime(2021, 3, 2)
    logs = logs_analyzer.read_from_db(start, end)
    logs_analyzer.analyze(logs)
