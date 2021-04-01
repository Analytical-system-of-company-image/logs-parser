import re
from ParserLogs.logstructure import LogStruct
from ParserLogs.filter import Filer


class Parser:
    '''class for parsing nginx or apache logs to logstructure'''

    def __init__(self):
        self.NUM_FIELDS = 9
        self.filter = Filer()

    def parsefile(self, listlogs):
        '''return list with list of corrected and filtered logs and list of incorrect logs'''
        pattern = re.compile(
            "^([\\d.]+) (\\S+) (\\S+) \\[([\\w:/]+\\s[+\\-]\\d{4})\\] \"(.+?)\" (\\d{3}) (\\d+) \"([^\"]+)\" \"([^\"]+)\"")
        parsedlogs = []
        incomletelogs = []
        for i in listlogs:
            p = re.match(pattern, i)
            if p is not None:
                if len(p.groups()) != self.NUM_FIELDS or p.group(5).find(".html") < 0:
                    incomletelogs.append(i + '\n')
                else:
                    curr = LogStruct(p.group(1), p.group(3), p.group(4), p.group(5), p.group(6), p.group(7),
                                     p.group(8), p.group(9))
                    if self.filter.filtering(curr):
                        parsedlogs.append(curr)
                    else:
                        incomletelogs.append(i + '\n')
        return [parsedlogs, incomletelogs]
