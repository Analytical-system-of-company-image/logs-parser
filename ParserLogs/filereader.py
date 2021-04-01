class FileReader:
    '''class for reading nginx or apache log from text files'''

    def readlogs(self, filepath):
        '''read logs from txt file'''
        f = open(filepath)
        return f.read().split('\n')
