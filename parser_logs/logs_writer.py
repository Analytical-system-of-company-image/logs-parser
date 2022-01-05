import csv
import datetime
import logging
from typing import List, Dict
from abc import ABC, abstractmethod
import click
from mongodb.models import GoodLog, BadLog
from mongodb.config import DevelopingConfig
from parser_logs.parser import ResultGoodBadLogs
from multiprocessing import Process, Manager, cpu_count
from tqdm import tqdm


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

        def add_good_logs(good_logs: List[ResultGoodBadLogs], buf_good_logs: Dict[int, GoodLog], i: int) -> None:
            """Prepearing record for bulk save 

            Args:
                logs (List[ResultGoodBadLogs]): logs
            """
            buf = []
            for log in good_logs:
                buf.append(GoodLog(ip=log.ip_adress, user=log.user,
                                   date=log.date, time=log.time, req=log.request,
                                   res=int(log.response),
                                   byte_sent=int(log.bytesSent), referrer=log.referer,
                                   zone=log.zone, browser=log.browser))
            buf_good_logs[i] = buf

        if write_bad_logs:
            bad_logs = logs.get_bad_logs()
            for part_logs in tqdm(bad_logs):
                part_logs = [{'data': value} for value in part_logs]
                records = [BadLog(**data) for data in part_logs]
                del part_logs
                BadLog.objects.insert(records)
                del records
            logging.info(f"Bad logs {len(bad_logs)} saved to db")
            del bad_logs

        n_proc = cpu_count()

        good_logs = logs.get_good_logs()
        processes = []
        manager = Manager()
        prepeared_logs = manager.dict()
        for proc_num in range(n_proc):
            p = Process(target=add_good_logs, args=(
                good_logs[proc_num], prepeared_logs, proc_num))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()
        del good_logs

        prepeared_list = [value for _, value in prepeared_logs.items()]
        del prepeared_logs
        prepeared_logs = sum(prepeared_list, [])
        GoodLog.objects.insert(prepeared_logs)
        length_prepared_logs = len(prepeared_logs)
        del prepeared_logs
        logging.info(f"Good logs {length_prepared_logs} saved to db")
