#! /usr/bin/python3.8
from typing import List
from parser_logs.logs_reader import readlogs
from parser_logs.parser import CommonLogsParser, AbstractParser
from parser_logs.filter import ConditionGz, \
    ConditionJs, ConditionResponse, ConditionPhp, ConditionSvg, \
    ConditionRobot, ConditionHead, ConditionPost, ConditionWoff, \
    ConditionPng, ConditionCss, ConditionFilterAbstract, Filter

from parser_logs.logs_writer import AbstractWriter, MongodbWriter

if __name__ == '__main__':
    wr: AbstractWriter = MongodbWriter('server_logs', 'root', 'root', 27017)
    try:
        data_logs = readlogs('logs/logs-2020-03-16.log')
    except FileExistsError:
        print("File doesn't exist!")
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
        commonLogsParser: AbstractParser = CommonLogsParser(logs_filter)
        result = commonLogsParser.parsefile(data_logs)
        wr.write(result)
