import os
import csv
import datetime
from .logstructure import LogStruct
from typing import List
import click
from Mongodb.models import GoodLog, BadLog
from Mongodb.config import DevelopingConfig
from ParserLogs.logstructure import LogStruct
from typing import List
from abc import ABC, abstractmethod
from ParserLogs.parser import ResultGoodBadLogs


class AbstractWriter(ABC):
    @abstractmethod
    def write(self, logs: ResultGoodBadLogs, write_bad_logs=False) -> None:
        pass


class CSVWriter(AbstractWriter):
    '''class for writing log to some file'''

    def write(self, logs: ResultGoodBadLogs, prefixname='logs', write_bad_logs=False) -> None:
        '''write log to csv file'''
        good_logs = logs.get_good_logs()
        count = len(good_logs)
        filename = "good_" + prefixname + ":" + str(count) + ":" + str(datetime.date.today()) + ".csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file, delimiter='\t')
            print("Writing good logs to CSV:")
            with click.progressbar(good_logs) as bar:
                for i in bar:
                    writer.writerow(i)
        if write_bad_logs:
            bad_logs = logs.get_bad_logs()
            count = len(bad_logs)
            filename = "bad_" + prefixname + ":" + str(count) + ":" + str(datetime.date.today()) + ".csv"
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                print("Writing bad logs to CSV")
                with click.progressbar(bad_logs) as bar:
                    for i in bar:
                        writer.writerow([i])


class TXTWriter(AbstractWriter):

    def write(self, logs: ResultGoodBadLogs, prefixname='logs', write_bad_logs=False) -> None:
        '''write los to txt log file'''
        good_logs = logs.get_good_logs()
        count = len(good_logs)
        filename = "good_" + prefixname + ":" + str(count) + ":" + str(datetime.date.today()) + ".log"
        with open(filename, 'w', newline='') as file:
            print("Writing good logs to TXT:")
            with click.progressbar(good_logs) as bar:
                for i in bar:
                    file.write(str(i))
        if write_bad_logs:
            bad_logs = logs.get_bad_logs()
            count = len(bad_logs)
            filename = "bad_" + prefixname + ":" + str(count) + ":" + str(datetime.date.today()) + ".log"
            with open(filename, 'w', newline='') as file:
                print("Writing bad logs to TXT:")
                with click.progressbar(bad_logs) as bar:
                    for i in bar:
                        file.write(i)


class MongodbWriter:
    '''Class for writing logs to mongo db'''

    def __init__(self, namedb, usr, pwd, port):
        try:
            self.connect = DevelopingConfig(namedb, usr, pwd, port)
        except Exception as ex:
            print('Не удалось подключиться к базе данных:', ex)

    def write(self, logs: ResultGoodBadLogs, write_bad_logs=False) -> None:

        buf_good_logs: List[GoodLog] = []
        buf_bad_logs: List[BadLog] = []
        print("Writing good logs to MongoDB:")
        with click.progressbar(logs.get_good_logs()) as bar:
            count = 0
            for log in bar:
                buf_good_logs.append(GoodLog(ip=log.ip, user=log.user, date=log.date, time=log.time, req=log.request,
                                             res=int(log.response), byte_sent=int(log.bytesSent), referrer=log.referer))
                buf_good_logs[count].save()
                count += 1
        if write_bad_logs:
            print("Writing bad logs to MongoDB:")
            with click.progressbar(logs.get_bad_logs()) as bar:
                count = 0
                for log in bar:
                    buf_bad_logs.append(BadLog(data=log))
                    buf_bad_logs[count].save()
                    count += 1
