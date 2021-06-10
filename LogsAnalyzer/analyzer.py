import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
import IP2Location
from Mongodb.config import DevelopingConfig
from Mongodb.models import GoodLog, ReportLogs
from matplotlib.backends.backend_pdf import PdfPages
import datetime


class LogsAnalyzer:
    '''Class for buildings grafics'''

    def __init__(self, plts=[], time_zone=10) -> None:
        self.plots = plts
        pd.options.mode.chained_assignment = None
        self.connect = None

    def connect_db(self, namedb, usr, pwd, port) -> None:
        '''Set connection with MongoDB'''
        try:
            self.connect = DevelopingConfig(namedb, usr, pwd, port)
        except Exception as ex:
            print('Failed to connect to database:', ex)

    def read_from_db(self) -> None:
        '''Read data from DB'''
        if self.connect is None:
            raise Exception("Database not connected")
        else:
            logs = GoodLog.objects()
            return pd.DataFrame([log.to_dict() for log in logs])

    def read_from_csv(self, path: str, delimeter='\t') -> None:
        '''Read data from CSV file'''
        self.df = pd.read_csv(path, delimeter=delimeter)
        self.df.columns = ['IP', 'USER', 'DATE', 'TIME', 'ZONE', 'REQ', 'RES', 'BYTESENT', 'REFERRER', 'BROWSER']

    def analyze(self, df):
        '''':return pdf with graphics and push into BD'''
        result_pdf = PdfPages('multipage_pdf.pdf')
        result_plots = []
        for plot in self.plots:
            buf = plot.get_plt(df)
            if isinstance(buf, list):
                result_plots.extend(buf)
            else:
                result_plots.append(buf)

        for plot in result_plots:
            result_pdf.savefig()
            plot.close()
        d = result_pdf.infodict()
        d['Title'] = 'Report Image Company Official cite'
        d['Author'] = u'PDA'
        d['Subject'] = 'How to create a multipage result_pdf file and set its metadata'
        d['Keywords'] = 'result_pdfPages multipage keywords author title subject'
        d['CreationDate'] = datetime.datetime.today()
        d['ModDate'] = datetime.datetime.today()
        result_pdf.close()
        with open('multipage_pdf.pdf', 'rb') as fd:
            new_report = ReportLogs()
            new_report.pdf_file.put(fd)
            new_report.save()
