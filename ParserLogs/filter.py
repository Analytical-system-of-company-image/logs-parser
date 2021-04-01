import re


class Filer:
    '''class for filtering logs'''

    def isrobot(self, log):
        '''Is the log indexed by a bot'''
        return re.findall(r'B|bot', log.browser)

    def filtering(self, log):
        '''filtering log'''
        flag = True
        if self.isrobot(log):
            return not flag
        return flag
