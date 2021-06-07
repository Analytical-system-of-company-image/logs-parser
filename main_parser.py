#! /usr/bin/python3.8
from ParserLogs.logs_reader import FileReader
from ParserLogs.parser import CommonLogsParser, AbstractParser
from ParserLogs.filter import *

from ParserLogs.logs_writer import AbstractWriter, MongodbWriter, CSVWriter
from typing import List

if __name__ == '__main__':
    fr = FileReader()
    datalogs = fr.readlogs('./logs/2020-03-16 - Архив логов с разными IP-адресами')
    conditions: List[ConditionFilterAbstaract] = []
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
    filter = Filter(conditions)
    commonLogsParser: AbstractParser = CommonLogsParser(filter)
    result = commonLogsParser.parsefile(datalogs)
    wr: AbstractWriter = MongodbWriter('server_logs', 'root', 'root', 27017)
    wr.write(result)
