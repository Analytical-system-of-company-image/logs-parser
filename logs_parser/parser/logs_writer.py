import csv
import datetime
import logging
from abc import ABC, abstractmethod

import click
import pandas as pd

from logs_parser.parser.parser import ResultGoodBadLogs


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
        filename = "good_" + prefixname + ":" + \
            str(datetime.date.today()) + ".csv"
        logging.info(f"filename to writing good logs:{filename}")
        df = pd.DataFrame([log.asdict() for log in good_logs])
        df.to_csv(filename, index=False, mode='a')
        del df

        if write_bad_logs:
            bad_logs = logs.get_bad_logs()
            filename = "bad_" + prefixname + ":" + \
                str(datetime.date.today()) + ".csv"
            logging.info(f"filename to writing bad logs: {filename}")
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                with click.progressbar(bad_logs, label="Writing bad logs to CSV") as all_bad_logs:
                    for log in all_bad_logs:
                        writer.writerow([log])
                        logging.info(f"{log} are wrote to CSV")
