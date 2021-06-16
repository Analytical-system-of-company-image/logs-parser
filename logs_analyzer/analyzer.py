import datetime
from typing import List
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from mongodb.config import DevelopingConfig
from mongodb.models import GoodLog, ReportLogs


class LogsAnalyzer:
    '''Class for buildings grafics'''

    def __init__(self, plts: List = None, time_zone=10) -> None:
        if plts is None:
            self.plots = []
        else:
            self.plots = plts
        self.logs_time_zone = time_zone
        pd.options.mode.chained_assignment = None
        self.connect = None
        self.data_logs = []

    def connect_db(self, namedb, usr, pwd, port) -> None:
        '''Set connection with MongoDB'''
        self.connect = DevelopingConfig(namedb, usr, pwd, port)

    def read_from_db(self) -> None:
        '''Read data from DB'''
        logs = GoodLog.objects()
        return pd.DataFrame([log.to_dict() for log in logs])

    def read_from_csv(self, path: str) -> None:
        '''Read data from CSV file'''
        self.data_logs = pd.read_csv(path, delimiter='\t')
        self.data_logs.columns = ['IP', 'USER', 'DATE', 'TIME',
                                  'ZONE', 'REQ', 'RES', 'BYTESENT', 'REFERRER', 'BROWSER']

    def analyze(self, data_frame):
        '''':return pdf with graphics and push into BD'''
        result_pdf = PdfPages('report.pdf')
        result_plots = []
        for plot in self.plots:
            buf = plot.get_plt(data_frame)
            if isinstance(buf, list):
                result_plots.extend(buf)
            else:
                result_plots.append(buf)

        for plot in result_plots:
            result_pdf.savefig()
            plot.close()
        report = result_pdf.infodict()
        report['Title'] = 'Report Image Company Official cite'
        report['Author'] = u'PDA'
        report['Subject'] = 'How to create a multipage result_pdf file and set its metadata'
        report['Keywords'] = 'result_pdfPages multipage keywords author title subject'
        report['CreationDate'] = datetime.datetime.today()
        report['ModDate'] = datetime.datetime.today()
        result_pdf.close()
        with open('report.pdf', 'rb') as pdf_file:
            new_report = ReportLogs()
            new_report.pdf_file.put(pdf_file)
            new_report.save()
