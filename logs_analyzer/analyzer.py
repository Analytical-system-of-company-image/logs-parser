import datetime
from typing import List
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from mongodb.config import DevelopingConfig
from mongodb.models import GoodLog, ReportLogs
from PIL import Image


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
        self.connect.connect_db()

    def read_from_db(self) -> None:
        '''Read data from DB'''
        logs = GoodLog.objects()
        return pd.DataFrame([log.to_dict() for log in logs])

    def read_from_csv(self, path: str) -> None:
        '''Read data from CSV file'''
        self.data_logs = pd.read_csv(path, delimiter='\t')
        self.data_logs.columns = ['IP', 'USER', 'DATE', 'TIME',
                                  'ZONE', 'REQ', 'RES', 'BYTESENT', 'REFERRER', 'BROWSER']

    def fig2img(self, fig):
        """Convert a Matplotlib figure to a PIL Image and return it"""
        import io
        buf = io.BytesIO()
        fig.savefig(buf)
        buf.seek(0)
        img = Image.open(buf)
        return img

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
        result_pillow_images = []

        for plot in result_plots:
            result_pdf.savefig()
            buf_pillow_image = self.fig2img(plot.gcf())
            result_pillow_images.append(buf_pillow_image)
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
        return result_pillow_images
