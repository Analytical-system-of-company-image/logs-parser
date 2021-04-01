import os
import csv
import datetime


class FileWriter:
    '''class for writing log to some file'''

    def writetocsv(self, logs, prefixname='logs'):
        '''write log to csv file'''
        count = len(logs)

        filename = prefixname + ":" + str(count) + ":" + str(datetime.date.today()) + ".csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file, delimiter='\t')
            for i in logs:
                writer.writerow(i)
