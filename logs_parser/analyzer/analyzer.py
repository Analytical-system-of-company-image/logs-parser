import datetime
from datetime import datetime
from typing import List

import IP2Location
import numpy as np
import pandas as pd
from pandas import DataFrame
from tqdm import tqdm


class LogsAnalyzer:
    """Class for buildings grafics
    """

    def __unique_hits_per_day(self, df: DataFrame) -> float:
        """Middle percent increase unique visits (-sup,+sup)

        Args:
            df (DataFrame): logs

        Returns:
            float: grade
        """
        df = df.copy()
        df = df[df['RES'] == 200]
        df = df[~df['BROWSER'].str.contains('bot')]
        df_groupby_date = df.groupby('DATE').agg({"IP": lambda x: x.nunique()})
        df_groupby_date.reset_index(inplace=True)

        df_groupby_date['fake'] = df_groupby_date['IP'].diff(
            periods=-1).dropna()
        numerator = df_groupby_date['fake'].sum()

        denominator = df_groupby_date['IP'].sum()

        result_mark = (numerator / denominator)

        return result_mark

    def __regional_interest(self, df: DataFrame) -> float:
        """Mark region interest interest [0;+sup]

        Args:
            df (DataFrame): logs

        Returns:
            float: grade
        """
        df = df.copy()
        df = df[df['RES'] == 200]
        df = df[~df['BROWSER'].str.contains('bot')]
        ip2loc_obj = IP2Location.IP2Location(
            "logs_analyzer/data/IP2LOCATION-LITE-DB11.BIN")
        group_by_area = df.loc[:, ['IP', 'TIME']]
        group_by_area['COUNTRY'] = [ip2loc_obj.get_country_short(i)
                                    for i in group_by_area['IP']]
        filter_ru = group_by_area['COUNTRY'] == 'RU'
        group_by_area = group_by_area.loc[filter_ru]
        group_by_area['REGION'] = [ip2loc_obj.get_region(i)
                                   for i in group_by_area['IP']]
        res_group_by_area = group_by_area.groupby(
            'REGION')['IP'].agg(Count='count').reset_index()

        std = res_group_by_area['Count'].std()
        mean = res_group_by_area['Count'].mean()
        grade = mean/std

        return grade

    def __time_interests(self, df: DataFrame) -> float:
        """Time intereset

        Args:
            df (DataFrame): logs

        Returns:
            float: grade
        """
        df = df.copy()
        df = df[df['RES'] == 200]
        df = df[~df['BROWSER'].str.contains('bot')]
        group_by_hour = df.loc[:, ['TIME']]
        group_by_hour['TIME'] = df['TIME'].dt.hour
        uniqh = group_by_hour.groupby(['TIME'])['TIME'].agg(
            Count='count').reset_index()

        std = uniqh['Count'].std()
        mean = uniqh['Count'].mean()
        grade = mean/std

        return grade

    def __unique_hits_per_day_crawlers(self, df: DataFrame) -> float:
        """Unique hits per day crawlers grade

        Args:
            df (DataFrame): logs

        Returns:
            float: grade
        """
        df = df.copy()
        df = df[df['RES'] == 200]
        only_crawlers = df[df['BROWSER'].str.contains('bot')]
        df_groupby_date = only_crawlers.groupby('DATE').agg(
            {"IP": lambda x: x.nunique()})
        df_groupby_date.reset_index(inplace=True)

        df_groupby_date['fake'] = df_groupby_date['IP'].diff(
            periods=-1).dropna()
        numerator = df_groupby_date['fake'].sum()

        denominator = df_groupby_date['IP'].sum()

        result_mark = (numerator / denominator)

        return result_mark

    def __bad_requests(self, df: DataFrame) -> float:
        """Bad requests grade

        Args:
            good_requests (DataFrame): logs
            bad_requests (List[str]): bad logs

        Returns:
            float: grade
        """
        num_all_requests = len(df)
        num_bad_requests = len(df[df['RES'] != 200])

        grade = num_bad_requests/num_all_requests
        return 1/grade

    def analyze(self, df: DataFrame) -> DataFrame:
        '''':Return dataframe with grades'''
        dates = df['DATE'].dt.date.unique()
        df['DATE'] = df['DATE'].dt.date

        results = []

        for i in tqdm(range(len(dates)-1)):
            condition = (df['DATE'] == dates[i]) | (df['DATE'] == dates[i+1])
            sub_df = df[condition]
            x1 = self.__unique_hits_per_day(sub_df)
            x2 = self.__unique_hits_per_day_crawlers(sub_df)
            x3 = self.__regional_interest(sub_df)
            x4 = self.__time_interests(sub_df)
            x5 = self.__bad_requests(sub_df)
            sub_list = [dates[i+1], x1, x2, x3, x4, x5]
            results.append(sub_list)
        res_df = DataFrame(results)
        w1 = w2 = w3 = w4 = w5 = 1
        res_df.columns = ['date', 'x1', 'x2', 'x3', 'x4', 'x5']
        res_df['grade'] = np.sqrt(w1*(res_df['x1']**2)+w2*(res_df['x2']**2)+w3 *
                                  (res_df['x3']**2)+w4*(res_df['x4']**2)+w5*(res_df['x5']**2))

        res_df.columns = ['date', 'unique_by_day', 'unique_by_day_bots',
                          'regional_interests', 'time_interests', 'bad_requests', 'grade']

        return res_df
