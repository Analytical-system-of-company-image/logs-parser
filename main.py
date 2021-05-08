#! /usr/bin/python3.8
from ParserLogs.filereader import FileReader
from ParserLogs.parser import CommonLogsParser, AbstractParser
from ParserLogs.filewriter import FileWriter
from ParserLogs.filter import *
from typing import List

if __name__ == '__main__':
    fr = FileReader()
    datalogs = fr.readlogs('./logs/monthlogs.log')
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
    wr = FileWriter()
    wr.writetocsv(result[0], "goodlogs")
    wr.writetotxt(result[1], "badlogs")
