import re
from typing import List
from abc import ABC, abstractmethod
from .log_structure import LogStruct


class ConditionFilterAbstract(ABC):
    '''Condition filter abstract'''
    ERROR_MASSAGE = "Abstract filter"

    def get_error_massage(self) -> str:
        ''':return error message'''
        return self.ERROR_MASSAGE

    @abstractmethod
    def filtering(self, log: LogStruct) -> bool:
        '''class for filtering log structs'''


class ConditionRobot(ConditionFilterAbstract):
    '''Class for filtering robot requests'''
    ERROR_MASSAGE = "It's robot"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log indexed by a bot'''
        return re.findall(r'B|bot', log.browser)


class ConditionHtml(ConditionFilterAbstract):
    '''Class for filtering html requests'''
    ERROR_MASSAGE = "Don't contains html"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log contains a html file in request'''
        return log.request.find(".html") < 0


class ConditionPng(ConditionFilterAbstract):
    '''Class for filtering png requests'''
    ERROR_MASSAGE = "It's png request"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log contains a png file in request'''
        return log.request.find(".png") > 0


class ConditionSvg(ConditionFilterAbstract):
    '''Class for filtering svg requests'''
    ERROR_MASSAGE = "It's svg request"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log contains a svg file in request'''
        return log.request.find(".svg") > 0


class ConditionJs(ConditionFilterAbstract):
    '''Class for filtering js requests'''
    ERROR_MASSAGE = "It's js request"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log contains a js file in request'''
        return log.request.find(".js") > 0


class ConditionWoff(ConditionFilterAbstract):
    '''Class for filtering a woff file in request'''
    ERROR_MASSAGE = "It's woff request"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log contains a woff file in request'''
        return log.request.find(".woff") > 0


class ConditionCss(ConditionFilterAbstract):
    '''Class for filtering a css file in request'''
    ERROR_MASSAGE = "It's css request"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log contains a css file in request'''
        return log.request.find(".css") > 0


class ConditionGz(ConditionFilterAbstract):
    '''Class for filtering a gz file in request'''
    ERROR_MASSAGE = "It's gz request"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log contains a gz file in request'''
        return log.request.find(".gz") > 0


class ConditionPhp(ConditionFilterAbstract):
    '''Class for filtering a php file in request'''
    ERROR_MASSAGE = "It's php request"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log contains a gz file in request'''
        return log.request.find(".php") > 0


class ConditionResponse(ConditionFilterAbstract):
    '''Class for filtering a bad response in request'''
    ERROR_MASSAGE = "It's not 200 status code"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log contains a bad response in request'''
        return log.response.find("200") < 0


class ConditionPost(ConditionFilterAbstract):
    '''Class for filtering a post request'''
    ERROR_MASSAGE = "It's post request"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log contains a post request'''
        return log.request.find("POST") > 0


class ConditionHead(ConditionFilterAbstract):
    '''Class for filtering a head request'''
    ERROR_MASSAGE = "It's HEAD request"

    def filtering(self, log: LogStruct) -> bool:
        '''Is the log contains a head request'''
        return log.request.find("HEAD") > 0


class Filter:
    '''class for filtering logs'''

    def __init__(self, conditions: List[ConditionFilterAbstract] = None) -> None:
        self.__conditions = conditions

    def filtering(self, log: LogStruct) -> bool:
        '''filtering log'''
        flag = True
        for condition in self.__conditions:
            if condition.filtering(log):
                raise Exception(condition.get_error_massage())
        return flag
