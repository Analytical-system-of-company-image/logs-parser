import logging
import re
from abc import ABC, abstractmethod
from multiprocessing import Manager, Process, cpu_count
from typing import List

from logs_parser.parser.filter import Filter
from logs_parser.parser.log_structure import LogStruct

from .filter import Filter


class AbstractParser(ABC):
    '''Absctract class parser'''

    @abstractmethod
    def parsefile(self, list_logs):
        '''Parsing log file'''


class ResultGoodBadLogs():
    '''Result DTO object class'''

    def __init__(self, parsed_logs: List, incompleted_logs: List):
        """Init

        Args:
            parsed_logs (List): List of chunks of good logs
            incompleted_logs (List): List of chunks of incompleted logs
        """
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
    '''class for parsing common logs to logs structure'''

    def __init__(self, logs_filter: Filter) -> None:
        self.filter: Filter = logs_filter
        logging.info("Filters are set")
        self.NUM_FIELDS = 9
        logging.info(f"num fileds:{self.NUM_FIELDS}")
        # Format common logs
        self.pattern = re.compile(
            "^([\\d.]+) (\\S+) (\\S+) \\[([\\w:/]+\\s[+\\-]\\d{4})\\]"
            " \"(.+?)\" (\\d{3}) (\\d+) \"([^\"]+)\" \"([^\"]+)\"")
        logging.info(f"pattern{self.pattern}")

    def parsefile(self, list_logs: List[str]) -> ResultGoodBadLogs:
        """return list with list of corrected and filtered logs and list of incorrect logs

        Args:
            list_logs (List[str]): raw logs

        Returns:
            ResultGoodBadLogs: data transfer object
        """
        def parse_thread(logs, result, incorrected, pattern, my_filter, i):
            incomleted_logs = []
            parsed_logs = []
            NUM_FIELDS = 9
            for log in logs:
                my_pattern = re.match(pattern, log)
                # logging.critical(f"my pattern for log:{my_pattern}")
                if my_pattern is not None:
                    if len(my_pattern.groups()) != NUM_FIELDS:
                        incomleted_logs.append(f"{log}:Not enough fields\n")
                        # logging.critical(f"{log}:Not enough fields")
                    else:
                        curr = LogStruct(my_pattern.group(1), my_pattern.group(3),
                                         my_pattern.group(
                            4), my_pattern.group(5),
                            my_pattern.group(
                            6), my_pattern.group(7),
                            my_pattern.group(8), my_pattern.group(9))
                        # logging.info(f"{curr}")
                        try:
                            if my_filter.filtering(curr):
                                parsed_logs.append(curr)
                                # logging.info(f"{curr} are added successfully")
                        except Exception as filtering_error:
                            incomleted_logs.append(
                                log + f':{filtering_error}\n')
                            # logging.critical(f"{log}:{filtering_error}")
                else:
                    incomleted_logs.append(log + ":Don't match\n")
                    # logging.critical(f"{log}:Don't match")
            result[i] = parsed_logs
            incorrected[i] = incomleted_logs

        def chunker_list(seq: List[str], size: int) -> List[str]:
            """Generator of chunks

            Args:
                seq (List[str]): logs
                size (int)): size of chunk

            Returns:
                List[str]: chunk of logs
            """
            return (seq[i::size] for i in range(size))

        n_proc = cpu_count()
        chunks = chunker_list(list_logs, n_proc)
        del list_logs

        logging.info("Logs parsing:")
        processes = []
        manager = Manager()
        r_1 = manager.dict()
        r_2 = manager.dict()
        for proc_num in range(n_proc):
            p = Process(target=parse_thread, args=(
                next(chunks), r_1, r_2, self.pattern, self.filter, proc_num))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()
        del chunks
        parsed_logs = [value for _, value in r_1.items()]
        del r_1
        incomleted_logs = [value for _, value in r_2.items()]
        del r_2
        united_batches = sum(parsed_logs, [])
        del parsed_logs
        return ResultGoodBadLogs(united_batches, incomleted_logs)


class SlowCommonLogsParser(AbstractParser):
    '''class for parsing common logs to logs structure'''

    def __init__(self, logs_filter: Filter) -> None:
        self.filter: Filter = logs_filter
        logging.info("Filters are set")
        self.NUM_FIELDS = 9
        logging.info(f"num fileds:{self.NUM_FIELDS}")
        # Format common logs
        self.pattern = re.compile(
            "^([\\d.]+) (\\S+) (\\S+) \\[([\\w:/]+\\s[+\\-]\\d{4})\\]"
            " \"(.+?)\" (\\d{3}) (\\d+) \"([^\"]+)\" \"([^\"]+)\"")
        logging.info(f"pattern{self.pattern}")

    def parsefile(self, list_logs: List[str]) -> ResultGoodBadLogs:
        """return list with list of corrected and filtered logs and list of incorrect logs

        Args:
            list_logs (List[str]): raw logs

        Returns:
            ResultGoodBadLogs: data transfer object
        """
        incomleted_logs = []
        parsed_logs = []
        NUM_FIELDS = 9
        for log in list_logs:
            my_pattern = re.match(self.pattern, log)
            # logging.critical(f"my pattern for log:{my_pattern}")
            if my_pattern is not None:
                if len(my_pattern.groups()) != NUM_FIELDS:
                    incomleted_logs.append(f"{log}:Not enough fields\n")
                    # logging.critical(f"{log}:Not enough fields")
                else:
                    curr = LogStruct(my_pattern.group(1), my_pattern.group(3),
                                     my_pattern.group(
                        4), my_pattern.group(5),
                        my_pattern.group(
                        6), my_pattern.group(7),
                        my_pattern.group(8), my_pattern.group(9))
                    # logging.info(f"{curr}")
                    try:
                        if self.filter.filtering(curr):
                            parsed_logs.append(curr)
                            # logging.info(f"{curr} are added successfully")
                    except Exception as filtering_error:
                        incomleted_logs.append(
                            log + f':{filtering_error}\n')
                        # logging.critical(f"{log}:{filtering_error}")
            else:
                incomleted_logs.append(log + ":Don't match\n")
                # logging.critical(f"{log}:Don't match")

        return ResultGoodBadLogs(parsed_logs, incomleted_logs)
