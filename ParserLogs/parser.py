import re
from ParserLogs.logstructure import LogStruct
from ParserLogs.filter import Filter
from abc import ABC, abstractmethod
from typing import Tuple, List
import click
from .filter import Filter


class AbstractParser(ABC):
    @abstractmethod
    def parsefile(self, listlogs):
        pass


class CommonLogsParser(AbstractParser):
    '''class for parsing coommon logs to logstructure'''

    def __init__(self, filter: Filter) -> None:
        self.filter = filter
        self.NUM_FIELDS = 9
        # Format common logs
        self.pattern = re.compile(
            "^([\\d.]+) (\\S+) (\\S+) \\[([\\w:/]+\\s[+\\-]\\d{4})\\] \"(.+?)\" (\\d{3}) (\\d+) \"([^\"]+)\" \"([^\"]+)\"")

    def parsefile(self, listlogs: List[str]) -> Tuple[List[LogStruct], List[str]]:
        '''return list with list of corrected and filtered logs and list of incorrect logs'''
        parsedlogs: LogStruct = []
        incomletelogs: str = []
        with click.progressbar(listlogs) as bar:
            for i in bar:
                p = re.match(self.pattern, i)
                if p is not None:
                    if len(p.groups()) != self.NUM_FIELDS:
                        incomletelogs.append(i + ':Not enough fields\n')
                    else:
                        curr = LogStruct(p.group(1), p.group(3), p.group(4), p.group(5), p.group(6), p.group(7),
                                         p.group(8), p.group(9))
                        try:
                            if self.filter.filtering(curr):
                                parsedlogs.append(curr)
                        except Exception as e:
                            incomletelogs.append(i + f':{e}\n')
                else:
                    incomletelogs.append(i + ":Don't match\n")
                bar.next
        return [parsedlogs, incomletelogs]
