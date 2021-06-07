from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
import IP2Location


class AbstractPlot(ABC):
    @abstractmethod
    def get_plt(self, df):
        pass


class IpPlot(AbstractPlot):
    def get_plt(self, df):
        ''':return plt group count by ip'''
        group_by_ip = df.loc[:, ['IP']]
        uniqip = group_by_ip.groupby(['IP'])['IP'].count()
        uniqip.to_frame()
        fig, ax = plt.subplots(1, 1, sharey=True, sharex=False, figsize=(20, 20), dpi=300)
        ax.plot(uniqip)
        tick_spacing = 100
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        plt.xticks(rotation=90)
        plt.title("Group by IP")
        return plt


class TimePlot(AbstractPlot):
    def get_plt(self, df):
        ''':return plt group ip by time'''
        group_by_hour = df.loc[:, ['TIME']]
        group_by_hour['TIME'] = df['TIME'].dt.hour
        uniqh = group_by_hour.groupby(['TIME'])['TIME'].count()
        uniqh.to_frame()
        fig, ax = plt.subplots(1, 1, sharey=True, sharex=False, figsize=(10, 10), dpi=300)
        ax.plot(uniqh)
        tick_spacing = 1
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        plt.xticks(rotation=90)
        plt.title("Group by Time")
        return plt


class CountryPlot(AbstractPlot):
    def __init__(self):
        self.IP2LocObj = IP2Location.IP2Location("LogsAnalyzer/data/IP2LOCATION-LITE-DB11.BIN")

    def get_plt(self, df):
        ''':return plt group count by country'''
        group_by_area = df.loc[:, ['IP']]
        uniqip = group_by_area.groupby('IP')['IP'].count()
        uniqip = uniqip.to_frame()
        uniqip['COUNTRY'] = [self.IP2LocObj.get_country_short(i[0]) for i in uniqip.index.to_frame().values]
        uniqarea = uniqip.groupby('COUNTRY')['IP'].count()
        fig, ax = plt.subplots(1, 1, sharey=True, sharex=False, figsize=(10, 10), dpi=300)
        ax.plot(uniqarea)
        tick_spacing = 1
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        plt.xticks(rotation=90)
        plt.title("Group by Country")
        return plt


class RegionPlot(AbstractPlot):
    def __init__(self):
        self.IP2LocObj = IP2Location.IP2Location("LogsAnalyzer/data/IP2LOCATION-LITE-DB11.BIN")

    def get_plt(self, df):
        ''':return plt group count by region'''
        group_by_area = df.loc[:, ['IP', 'TIME']]
        group_by_area['COUNTRY'] = [self.IP2LocObj.get_country_short(i) for i in group_by_area['IP']]
        filterRu = group_by_area['COUNTRY'] == 'RU'
        group_by_area = group_by_area.loc[filterRu]
        group_by_area['REGION'] = [self.IP2LocObj.get_region(i) for i in group_by_area['IP']]
        res_group_by_area = group_by_area.groupby('REGION')['IP'].count()
        fig, ax = plt.subplots(1, 1, sharey=True, sharex=False, figsize=(20, 15), dpi=300)
        ax.plot(res_group_by_area)
        tick_spacing = 1
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        plt.xticks(rotation=90)
        plt.title("Group by Region")
        return plt


class PopularRegionsPlot(AbstractPlot):
    def __init__(self, num_of_regions, time_zone=10):
        self.num_regions = num_of_regions
        self.IP2LocObj = IP2Location.IP2Location("LogsAnalyzer/data/IP2LOCATION-LITE-DB11.BIN")
        self.vladtimetm = time_zone

    def get_plt(self, df):
        ":return plts group time by num_regions most popular regions"

        def time_zone_to_int(zone: str, moda: str) -> int:
            if zone == "-":
                return int(str(moda)[:3])
            return int(str(zone)[:3])

        group_by_area = df.loc[:, ['IP', 'TIME']]
        group_by_area['COUNTRY'] = [self.IP2LocObj.get_country_short(i) for i in group_by_area['IP']]
        group_by_area['TIMEZONE'] = [self.IP2LocObj.get_timezone(i) for i in group_by_area['IP']]
        moda = group_by_area['TIMEZONE'].mode()
        group_by_area['TIMEZONE'] = [time_zone_to_int(i, moda) for i in group_by_area['TIMEZONE']]
        filterRu = group_by_area['COUNTRY'] == 'RU'
        group_by_area = group_by_area.loc[filterRu]
        group_by_area['REGION'] = [self.IP2LocObj.get_region(i) for i in group_by_area['IP']]
        popular_list = group_by_area['REGION'].value_counts()[:self.num_regions].index.tolist()
        plt_list = []
        for popular_elem in popular_list:
            filter_by_region = group_by_area['REGION'] == popular_elem
            filter_by_region = group_by_area.loc[filter_by_region]
            diff = self.vladtimetm - filter_by_region['TIMEZONE'].iloc[0]
            filter_by_region['TIME'] = filter_by_region['TIME'].dt.hour
            filter_by_region['TIME'] = filter_by_region['TIME'].apply(lambda x: (x - diff + 24) % 24)
            uniqh_region = filter_by_region.groupby(['TIME'])['TIME'].count()
            fig, ax = plt.subplots(1, 1, sharey=True, sharex=False, figsize=(20, 15), dpi=300)
            ax.plot(uniqh_region)
            tick_spacing = 1
            ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
            plt.xticks(rotation=90)
            plt.title(popular_elem)
            plt_list.append(plt)
        return plt_list
