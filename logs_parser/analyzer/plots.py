from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import IP2Location
from pandas import DataFrame


class AbstractPlot(ABC):
    '''Absctract class plot'''

    @abstractmethod
    def get_plt(self, data_frame):
        ''':return plt object'''


class IpPlot(AbstractPlot):
    '''Class  Ip plot'''

    def get_plt(self, data_frame: DataFrame):
        ''':return plt group count by ip'''
        group_by_ip = data_frame.loc[:, ['IP']]
        uniqip = group_by_ip.groupby(['IP'])['IP'].count()
        uniqip.to_frame()
        _, my_axis = plt.subplots(
            1, 1, sharey=True, sharex=False, figsize=(20, 20), dpi=300)
        my_axis.plot(uniqip)
        tick_spacing = 100
        my_axis.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        plt.xticks(rotation=90)
        plt.title("Group by IP")
        return plt


class TimePlot(AbstractPlot):
    '''Class all time plot'''

    def get_plt(self, data_frame: DataFrame):
        ''':return plt group ip by time'''
        group_by_hour = data_frame.loc[:, ['TIME']]
        group_by_hour['TIME'] = data_frame['TIME'].dt.hour
        uniqh = group_by_hour.groupby(['TIME'])['TIME'].count()
        uniqh.to_frame()
        _, my_axis = plt.subplots(
            1, 1, sharey=True, sharex=False, figsize=(10, 10), dpi=300)
        my_axis.plot(uniqh)
        tick_spacing = 1
        my_axis.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        plt.xticks(rotation=90)
        plt.title("Group by Time")
        return plt


class CountryPlot(AbstractPlot):
    '''Class country plot'''

    def __init__(self):
        self.ip2loc_obj = IP2Location.IP2Location(
            "logs_analyzer/data/IP2LOCATION-LITE-DB11.BIN")

    def get_plt(self, data_frame: DataFrame):
        ''':return plt group count by country'''
        group_by_area = data_frame.loc[:, ['IP']]
        uniqip = group_by_area.groupby('IP')['IP'].count()
        uniqip = uniqip.to_frame()
        uniqip['COUNTRY'] = [self.ip2loc_obj.get_country_short(i[0])
                             for i in uniqip.index.to_frame().values]
        uniqarea = uniqip.groupby('COUNTRY')['IP'].count()
        _, my_axis = plt.subplots(
            1, 1, sharey=True, sharex=False, figsize=(10, 10), dpi=300)
        my_axis.plot(uniqarea)
        tick_spacing = 1
        my_axis.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        plt.xticks(rotation=90)
        plt.title("Group by Country")
        return plt


class RegionPlot(AbstractPlot):
    '''Class region plot'''

    def __init__(self):
        self.ip2loc_obj = IP2Location.IP2Location(
            "logs_analyzer/data/IP2LOCATION-LITE-DB11.BIN")

    def get_plt(self, data_frame: DataFrame):
        ''':return plt group count by region'''
        group_by_area = data_frame.loc[:, ['IP', 'TIME']]
        group_by_area['COUNTRY'] = [self.ip2loc_obj.get_country_short(i)
                                    for i in group_by_area['IP']]
        filter_ru = group_by_area['COUNTRY'] == 'RU'
        group_by_area = group_by_area.loc[filter_ru]
        group_by_area['REGION'] = [self.ip2loc_obj.get_region(i)
                                   for i in group_by_area['IP']]
        res_group_by_area = group_by_area.groupby('REGION')['IP'].count()
        _, my_axis = plt.subplots(
            1, 1, sharey=True, sharex=False, figsize=(20, 15), dpi=300)
        my_axis.plot(res_group_by_area)
        tick_spacing = 1
        my_axis.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        plt.xticks(rotation=90)
        plt.title("Group by Region")
        return plt


class PopularRegionsPlot(AbstractPlot):
    '''Class pupular regions plot'''

    def __init__(self, num_of_regions: int, time=10):
        self.num_regions = num_of_regions
        self.ip2loc_obj = IP2Location.IP2Location(
            "logs_analyzer/data/IP2LOCATION-LITE-DB11.BIN")
        self.time_zone = time

    def get_plt(self, data_frame):
        ":return plts group time by num_regions most popular regions"

        def time_zone_to_int(zone: str, moda: str) -> int:
            if zone == "-":
                return int(str(moda)[:3])
            return int(str(zone)[:3])

        group_by_area = data_frame.loc[:, ['IP', 'TIME']]
        group_by_area['COUNTRY'] = [self.ip2loc_obj.get_country_short(i)
                                    for i in group_by_area['IP']]
        group_by_area['TIMEZONE'] = [self.ip2loc_obj.get_timezone(i)
                                     for i in group_by_area['IP']]
        moda = group_by_area['TIMEZONE'].mode()
        group_by_area['TIMEZONE'] = [time_zone_to_int(
            i, moda) for i in group_by_area['TIMEZONE']]
        filter_ru = group_by_area['COUNTRY'] == 'RU'
        group_by_area = group_by_area.loc[filter_ru]
        group_by_area['REGION'] = [
            self.ip2loc_obj.get_region(i) for i in group_by_area['IP']]
        popular_list = group_by_area['REGION'].value_counts()[
            :self.num_regions].index.tolist()
        plt_list = []
        for popular_elem in popular_list:
            filter_by_region = group_by_area['REGION'] == popular_elem
            filter_by_region = group_by_area.loc[filter_by_region]
            diff = self.time_zone - filter_by_region['TIMEZONE'].iloc[0]
            filter_by_region['TIME'] = filter_by_region['TIME'].dt.hour
            filter_by_region['TIME'] = filter_by_region['TIME']. \
                apply(lambda x: (x - diff + 24) % 24)
            uniqh_region = filter_by_region.groupby(['TIME'])['TIME'].count()
            _, my_axis = plt.subplots(
                1, 1, sharey=True, sharex=False, figsize=(20, 15), dpi=300)
            my_axis.plot(uniqh_region)
            tick_spacing = 1
            my_axis.xaxis.set_major_locator(
                ticker.MultipleLocator(tick_spacing))
            plt.xticks(rotation=90)
            plt.title(popular_elem)
            plt_list.append(plt)
        return plt_list
