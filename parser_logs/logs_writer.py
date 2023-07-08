import csv
import datetime
import logging
from abc import ABC, abstractmethod
from multiprocessing import Manager, Process, cpu_count
from typing import Dict, List

import click
from tqdm import tqdm

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
