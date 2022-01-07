import datetime
from datetime import datetime
from typing import List

import IP2Location
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from mongodb.config import DevelopingConfig
from mongodb.models import GoodLog, ReportLogs
from pandas import DataFrame
from PIL import Image
from tqdm import tqdm


class LogsAnalyzer:
    """Class for buildings grafics
    """

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
        """Connecting to database

        Args:
            namedb ([type]): namedb
            usr ([type]): username
            pwd ([type]): password
            port ([type]): port
        """
        self.connect = DevelopingConfig(namedb, usr, pwd, port)
        self.connect.connect_db()

    def read_from_db(self, start_date: datetime, end_date: datetime) -> DataFrame:
        """Read logs from database

        Args:
            start_date (datetime): start date of logs
            end_date (datetime): end date of logs

        Returns:
            DataFrame: DataFrame with logs
        """
        raw_query = {'date': {'$gte': start_date, '$lte': end_date}}
        logs = GoodLog.objects(__raw__=raw_query)
        return pd.DataFrame([log.to_dict() for log in logs])

    def read_from_csv(self, path: str) -> None:
        """Read data from CSV file

        Args:
            path (str): path to csv file
        """
        self.data_logs = pd.read_csv(path, delimiter='\t')
        self.data_logs.columns = ['IP', 'USER', 'DATE', 'TIME',
                                  'ZONE', 'REQ', 'RES', 'BYTESENT', 'REFERRER', 'BROWSER']

    def __fig2img(self, fig):
        """Convert a Matplotlib figure to a PIL Image and return it

        Args:
            fig (fig): pyplot

        Returns:
            image: image
        """
        import io
        buf = io.BytesIO()
        fig.savefig(buf)
        buf.seek(0)
        img = Image.open(buf)
        return img

    def __unique_hits_per_day(self, df: DataFrame) -> float:
        """Middle percent increase unique visits

        Args:
            df (DataFrame): logs

        Returns:
            float: grade
        """
        num_days = df['DATE'].nunique()
        df_groupby_date = df.groupby('DATE').agg({"IP": lambda x: x.nunique()})
        unique = df_groupby_date['IP'].values.tolist()

        numerator = 0
        denominator = unique[0] / num_days
        for i in range(len(unique) - 1):
            numerator = numerator + \
                abs(unique[i] - unique[i+1]) / (num_days - 1)
            denominator = denominator + unique[i + 1]/num_days
        result_mark = numerator / denominator

        return result_mark

    def __regional_interest(self, df: DataFrame) -> float:
        """Mark region interest interest

        Args:
            df (DataFrame): logs

        Returns:
            float: grade
        """
        ip2loc_obj = IP2Location.IP2Location(
            "logs_analyzer/data/IP2LOCATION-LITE-DB11.BIN")
        group_by_area = df.loc[:, ['IP', 'TIME']]
        group_by_area['COUNTRY'] = [ip2loc_obj.get_country_short(i)
                                    for i in group_by_area['IP']]
        filter_ru = group_by_area['COUNTRY'] == 'RU'
        group_by_area = group_by_area.loc[filter_ru]
        group_by_area['REGION'] = [ip2loc_obj.get_region(i)
                                   for i in group_by_area['IP']]
        res_group_by_area = group_by_area.groupby('REGION')['IP'].count()

        regions = DataFrame(res_group_by_area)
        num_regions = regions.shape[0]

        part_1 = part_2 = part_3 = part_4 = 0
        for num_region, region in enumerate(regions.iterrows()):
            count_region = region[1].to_dict()['IP']
            part_1 += num_region * count_region
            part_2 += num_region
            part_3 += count_region
            part_4 += num_region * num_region
        enumerator = num_regions * part_1 - part_2 * part_3
        denumerator = num_regions * part_4 - part_2 * part_2
        grade = 1 - (enumerator / denumerator)

        return grade

    def __time_interests(self, df: DataFrame) -> float:
        """Time intereset

        Args:
            df (DataFrame): logs

        Returns:
            float: grade
        """
        group_by_hour = df.loc[:, ['TIME']]
        group_by_hour['TIME'] = df['TIME'].dt.hour
        uniqh = group_by_hour.groupby(['TIME'])['TIME'].count()
        uniqh.to_frame()
        uniqh = uniqh.to_dict()
        num_hours = len(uniqh)

        part_1 = part_2 = part_3 = part_4 = 0
        for num_hour, count_hour in uniqh.items():
            part_1 += num_hour * count_hour
            part_2 += num_hour
            part_3 += count_hour
            part_4 += num_hour * num_hour
        enumerator = num_hours * part_1 - part_2 * part_3
        denumerator = num_hours * part_4 - part_2 * part_2
        grade = 1 - (enumerator / denumerator)

        return grade

    def analyze(self, data_frame: DataFrame):
        '''':return pdf with graphics and push into BD'''
        time_interests = self.__time_interests(data_frame)
        region_interests = self.__regional_interest(data_frame)
        unique_hits_per_day = self.__unique_hits_per_day(data_frame)
        now_date = str(datetime.now())
        result_pdf = PdfPages(f'report-{now_date}.pdf')
        result_plots = []
        for plot in tqdm(self.plots):
            buf = plot.get_plt(data_frame)
            if isinstance(buf, list):
                result_plots.extend(buf)
            else:
                result_plots.append(buf)
        result_pillow_images = []

        for plot in result_plots:
            result_pdf.savefig()
            buf_pillow_image = self.__fig2img(plot.gcf())
            result_pillow_images.append(buf_pillow_image)
            plot.close()
        report = result_pdf.infodict()
        report['Title'] = 'Report Image Company Official cite'
        report['Author'] = 'PDA'
        report['Subject'] = 'How to create a multipage result_pdf file and set its metadata'
        report['Keywords'] = 'result_pdfPages multipage keywords author title subject'
        report['CreationDate'] = datetime.today()
        report['ModDate'] = datetime.today()
        result_pdf.close()
        with open('report.pdf', 'rb') as pdf_file:
            new_report = ReportLogs()
            new_report.pdf_file.put(pdf_file)
            new_report.save()
        return result_pillow_images
