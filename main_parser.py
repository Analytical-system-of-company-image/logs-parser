import logging
from typing import List

from tqdm import tqdm

from parser_logs.filter import (ConditionCss, ConditionFilterAbstract,
                                ConditionGz, ConditionHead, ConditionJs,
                                ConditionPhp, ConditionPng, ConditionPost,
                                ConditionResponse, ConditionSvg, ConditionWoff,
                                Filter)
from parser_logs.logs_reader import read_logs
from parser_logs.logs_writer import AbstractWriter, MongodbWriter
from parser_logs.parser import AbstractParser, CommonLogsParser

SIZE_CHUNK = 500000

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        filename='parsing_logs.log', filemode='w')
    wr: AbstractWriter = MongodbWriter('server_logs', 'root', 'root', 27017)
    conditions: List[ConditionFilterAbstract] = []
    conditions.append(ConditionPhp())
    conditions.append(ConditionPng())
    conditions.append(ConditionSvg())
    conditions.append(ConditionJs())
    conditions.append(ConditionCss())
    conditions.append(ConditionPost())
    conditions.append(ConditionWoff())
    conditions.append(ConditionGz())
    # conditions.append(ConditionResponse())
    conditions.append(ConditionHead())
    logs_filter = Filter(conditions)
    commonLogsParser: AbstractParser = CommonLogsParser(logs_filter)
    for chunk_logs in tqdm(read_logs('dataset_gorod.log', SIZE_CHUNK)):
        parsed_logs = commonLogsParser.parsefile(chunk_logs)
        wr.write(parsed_logs, True)
        del parsed_logs
