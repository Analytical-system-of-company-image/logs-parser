#! /usr/bin/python3.8
from typing import List
import logging
from parser_logs.logs_reader import readlogs
from parser_logs.parser import CommonLogsParser, AbstractParser
from parser_logs.filter import ConditionGz, \
    ConditionJs, ConditionResponse, ConditionPhp, ConditionSvg, \
    ConditionRobot, ConditionHead, ConditionPost, ConditionWoff, \
    ConditionPng, ConditionCss, ConditionFilterAbstract, Filter

from parser_logs.logs_writer import AbstractWriter, MongodbWriter
from logs_analyzer.analyzer import LogsAnalyzer
from logs_analyzer.plots import IpPlot, TimePlot, CountryPlot, \
    RegionPlot, PopularRegionsPlot, AbstractPlot

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.NOTSET,
        filename="logsparser_logs.log",
        format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
        datefmt='%H:%M:%S',
    )

    wr: AbstractWriter = MongodbWriter('server_logs', 'root', 'root', 27017)
    file_path = input("Path to file with logs:")
    try:
        data_logs = readlogs(file_path)
        logging.info("File open and read successfully")
    except FileExistsError:
        print("File doesn't exist!")
        logging.critical("File doesn't exist!")
    else:
        conditions: List[ConditionFilterAbstract] = []
        conditions.append(ConditionRobot())
        conditions.append(ConditionPhp())
        conditions.append(ConditionPng())
        conditions.append(ConditionSvg())
        conditions.append(ConditionJs())
        conditions.append(ConditionCss())
        conditions.append(ConditionPost())
        conditions.append(ConditionWoff())
        conditions.append(ConditionGz())
        conditions.append(ConditionResponse())
        conditions.append(ConditionHead())
        logs_filter = Filter(conditions)
        print("Filters are set")
        logging.info("Filters are set")
        commonLogsParser: AbstractParser = CommonLogsParser(logs_filter)
        result = commonLogsParser.parsefile(data_logs)
        wr.write(result)
        need_plots: List[AbstractPlot] = []
        need_plots.append(IpPlot())
        need_plots.append(TimePlot())
        need_plots.append(CountryPlot())
        need_plots.append(RegionPlot())
        need_plots.append(PopularRegionsPlot(3))
        print("Plots are set")
        logging.info("Plots are set")
        logs_analyzer: LogsAnalyzer = LogsAnalyzer(need_plots)
        logs = logs_analyzer.read_from_db()
        logs_analyzer.analyze(logs)
