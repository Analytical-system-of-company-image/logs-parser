import re
from .logstructure import LogStruct
from abc import ABC, abstractmethod
from typing import List


class ConditionFilterAbstaract(ABC):
    ERROR_MASSAGE = "Abstract filter"

    def get_error_massage(self) -> str:
        return self.ERROR_MASSAGE

    @abstractmethod
    def filtering(self, log: LogStruct) -> bool:
        pass


class ConditionRobot(ConditionFilterAbstaract):
    ERROR_MASSAGE = "It's robot"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log indexed by a bot'''
        return re.findall(r'B|bot', log.browser)


class ConditionHtml(ConditionFilterAbstaract):
    ERROR_MASSAGE = "Don't contains html"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log conatins a html file in request'''
        return log.request.find(".html") < 0


class ConditionPng(ConditionFilterAbstaract):
    ERROR_MASSAGE = "It's png request"

    def filtering(self, log: LogStruct) -> bool:
        return log.request.find(".png") > 0


class ConditionSvg(ConditionFilterAbstaract):
    ERROR_MASSAGE = "It's svg request"

    def filtering(self, log: LogStruct) -> bool:
        return log.request.find(".svg") > 0


class ConditionJs(ConditionFilterAbstaract):
    ERROR_MASSAGE = "It's js request"

    def filtering(self, log: LogStruct) -> bool:
        return log.request.find(".js") > 0


class ConditionWoff(ConditionFilterAbstaract):
    ERROR_MASSAGE = "It's woff request"

    def filtering(self, log: LogStruct) -> bool:
        return log.request.find(".woff") > 0


class ConditionCss(ConditionFilterAbstaract):
    ERROR_MASSAGE = "It's css request"

    def filtering(self, log: LogStruct) -> bool:
        return log.request.find(".css") > 0


class ConditionGz(ConditionFilterAbstaract):
    ERROR_MASSAGE = "It's gz request"

    def filtering(self, log: LogStruct) -> bool:
        return log.request.find(".gz") > 0


class ConditionPhp(ConditionFilterAbstaract):
    ERROR_MASSAGE = "It's php request"

    def filtering(self, log: LogStruct) -> bool:
        return log.request.find(".php") > 0


class ConditionResponse(ConditionFilterAbstaract):
    ERROR_MASSAGE = "It's not 200 status code"

    def filtering(self, log: LogStruct) -> bool:
        return log.response.find("200") < 0


class ConditionPost(ConditionFilterAbstaract):
    ERROR_MASSAGE = "It's post request"

    def filtering(self, log: LogStruct) -> bool:
        return log.request.find("POST") > 0


class ConditionHead(ConditionFilterAbstaract):
    ERROR_MASSAGE = "It's HEAD request"

    def filtering(self, log: LogStruct) -> bool:
        return log.request.find("HEAD") > 0


class Filter:
    '''class for filtering logs'''

    def __init__(self, conditions: List[ConditionFilterAbstaract] = None):
        self.__conditions = conditions

    def filtering(self, log: LogStruct) -> bool:
        '''filtering log'''
        flag = True
        for condition in self.__conditions:
            if condition.filtering(log):
                raise Exception(condition.get_error_massage())
        return flag
