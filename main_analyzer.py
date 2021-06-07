#! /usr/bin/python3.8
from ParserLogs.logs_reader import FileReader
from ParserLogs.parser import CommonLogsParser, AbstractParser
from ParserLogs.filter import *
from LogsAnalyzer.analyzer import LogsAnalyzer
from ParserLogs.logs_writer import AbstractWriter, MongodbWriter, CSVWriter
from LogsAnalyzer.plots import *
from typing import List

if __name__ == '__main__':

    need_plots: List[AbstractPlot] = []
    need_plots.append(IpPlot())
    need_plots.append(TimePlot())
    need_plots.append(CountryPlot())
    need_plots.append(RegionPlot())
    need_plots.append(PopularRegionsPlot(3))
    logs_analyzer: LogsAnalyzer = LogsAnalyzer(need_plots)
    logs_analyzer.connect_db('server_logs', 'root', 'root', 27017)
    logs = logs_analyzer.read_from_db()
    logs_analyzer.analyze(logs)
