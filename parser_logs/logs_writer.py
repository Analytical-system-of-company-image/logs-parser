import csv
import datetime
import logging
from typing import List
from abc import ABC, abstractmethod
import click
from mongodb.models import GoodLog, BadLog
from mongodb.config import DevelopingConfig
from parser_logs.parser import ResultGoodBadLogs


class AbstractWriter(ABC):
    '''Absctract class writer'''

    @abstractmethod
    def write(self, logs: ResultGoodBadLogs, prefixname='logs', write_bad_logs=False) -> None:
        '''write log to target'''


class CSVWriter(AbstractWriter):
    '''class for writing log to some file'''

    def write(self, logs: ResultGoodBadLogs, prefixname='logs', write_bad_logs=False) -> None:
        '''write log to csv file'''
        good_logs = logs.get_good_logs()
        count = len(good_logs)
        filename = "good_" + prefixname + ":" + \
                   str(count) + ":" + str(datetime.date.today()) + ".csv"
        logging.info(f"filename to writing good logs:{filename}")
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file, delimiter='\t')
            with click.progressbar(good_logs, label="Writing good logs to CSV") as all_good_logs:
                for log in all_good_logs:
                    writer.writerow(log)
                    logging.info(f"{log} are wrote to CSV")
        if write_bad_logs:
            bad_logs = logs.get_bad_logs()
            count = len(bad_logs)
            filename = "bad_" + prefixname + ":" + \
                       str(count) + ":" + str(datetime.date.today()) + ".csv"
            logging.info(f"filename to writing bad logs: {filename}")
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                with click.progressbar(bad_logs, label="Writing bad logs to CSV") as all_bad_logs:
                    for log in all_bad_logs:
                        writer.writerow([log])
                        logging.info(f"{log} are wrote to CSV")

class MongodbWriter:
    '''Class for writing logs to mongo db'''

    def __init__(self, namedb, usr, pwd, port):
        self.con = DevelopingConfig(namedb, usr, pwd, port)
        if not self.con.check_connection():
            print("Database not connected")
            exit(1)
        print("Database connected successfully")
        self.con.connect_db()

    def write(self, logs: ResultGoodBadLogs, write_bad_logs=False) -> None:
        '''Write logs to mongodb'''

        buf_good_logs: List[GoodLog] = []
        buf_bad_logs: List[BadLog] = []
        with click.progressbar(logs.get_good_logs(), label="Writing good logs to MongoDB") as all_good_logs:
            count = 0
            for log in all_good_logs:
                buf_good_logs.append(GoodLog(ip=log.ip_adress, user=log.user,
                                             date=log.date, time=log.time, req=log.request,
                                             res=int(log.response),
                                             byte_sent=int(log.bytesSent), referrer=log.referer,
                                             zone=log.zone, browser=log.browser))
                buf_good_logs[count].save()
                logging.info(f"{buf_good_logs} saved to db")
                count += 1
        if write_bad_logs:
            with click.progressbar(logs.get_bad_logs(), label="Writing bad logs to MongoDB") as all_bad_logs:
                count = 0
                for log in all_bad_logs:
                    buf_bad_logs.append(BadLog(data=log))
                    buf_bad_logs[count].save()
                    logging.info(f"{buf_bad_logs} saved to db")
                    count += 1
