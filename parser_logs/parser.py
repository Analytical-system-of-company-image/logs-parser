import logging
import re
from typing import List
from abc import ABC, abstractmethod
import click
from parser_logs.log_structure import LogStruct
from parser_logs.filter import Filter
from .filter import Filter


class AbstractParser(ABC):
    '''Absctract class parser'''

    @abstractmethod
    def parsefile(self, list_logs):
        '''Parsing log file'''


class ResultGoodBadLogs():
    '''Result DTO object class'''

    def __init__(self, parsed_logs: List[LogStruct], incompleted_logs: List[str]):
        self.__good_logs = parsed_logs
        self.__bad_logs = incompleted_logs

    def get_good_logs(self) -> List[LogStruct]:
        ''':return good log'''
        return self.__good_logs

    def get_bad_logs(self) -> List[str]:
        ''':return bad logs'''
        return self.__bad_logs

    def get_len_good_log(self) -> int:
        return len(self.__good_logs)

    def get_len_bad_log(self) -> int:
        return len(self.__bad_logs)


class CommonLogsParser(AbstractParser):
    '''class for parsing coommon logs to logstructure'''

    def __init__(self, logs_filter: Filter) -> None:
        self.filter: Filter = logs_filter
        logging.info("Filters are set")
        self.num_fields = 9
        logging.info(f"num fileds:{self.num_fields}")
        # Format common logs
        self.pattern = re.compile(
            "^([\\d.]+) (\\S+) (\\S+) \\[([\\w:/]+\\s[+\\-]\\d{4})\\]"
            " \"(.+?)\" (\\d{3}) (\\d+) \"([^\"]+)\" \"([^\"]+)\"")
        logging.info(f"pattern{self.pattern}")

    def parsefile(self, list_logs: List[str]) -> ResultGoodBadLogs:
        '''return list with list of corrected and filtered logs and list of incorrect logs'''
        parsed_logs: List[LogStruct] = []
        incomleted_logs: List[str] = []

        logging.info("Logs parsing:")
        with click.progressbar(list_logs, label="Logs parsing") as all_list_logs:
            for log in all_list_logs:
                my_pattern = re.match(self.pattern, log)
                logging.critical(f"my pattern for log:{my_pattern}")
                if my_pattern is not None:
                    if len(my_pattern.groups()) != self.num_fields:
                        incomleted_logs.append(f"{log}:Not enough fields\n")
                        logging.critical(f"{log}:Not enough fields")
                    else:
                        curr = LogStruct(my_pattern.group(1), my_pattern.group(3),
                                         my_pattern.group(4), my_pattern.group(5),
                                         my_pattern.group(6), my_pattern.group(7),
                                         my_pattern.group(8), my_pattern.group(9))
                        logging.info(f"{curr}")
                        try:
                            if self.filter.filtering(curr):
                                parsed_logs.append(curr)
                                logging.info(f"{curr} are added successfully")
                        except Exception as exception:
                            incomleted_logs.append(log + f':{exception}\n')
                            logging.critical(f"{log}:{exception}")
                else:
                    incomleted_logs.append(log + ":Don't match\n")
                    logging.critical(f"{log}:Don't match")

        return ResultGoodBadLogs(parsed_logs, incomleted_logs)
