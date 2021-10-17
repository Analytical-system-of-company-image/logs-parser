import datetime
import os
import re
import time
from typing import List
import logging
import pandas as pd
import PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QDate
import matplotlib
from PIL.ImageQt import ImageQt
from PIL import Image
from gui import design

from parser_logs.logs_reader import readlogs
from parser_logs.parser import AbstractParser, ResultGoodBadLogs
from parser_logs.log_structure import LogStruct
from parser_logs.filter import ConditionGz, \
    ConditionJs, ConditionResponse, ConditionPhp, ConditionSvg, \
    ConditionRobot, ConditionHead, ConditionPost, ConditionWoff, \
    ConditionPng, ConditionCss, ConditionFilterAbstract, Filter

from logs_analyzer.analyzer import LogsAnalyzer
from logs_analyzer.plots import IpPlot, TimePlot, CountryPlot, \
    RegionPlot, PopularRegionsPlot, AbstractPlot
from mongodb.config import DevelopingConfig
from mongodb.models import GoodLog, LogFile, BadLog

matplotlib.use('Qt5Agg')


class MainApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    '''Class of gui app'''

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.path = ""
        self.prepared = False
        self.open_button_3.clicked.connect(self.__load_file)
        self.process_button_3.clicked.connect(self.__parse)
        self.pushButton_5.clicked.connect(self.__build_graphics)
        self.popular_regions_check_box_3.clicked.connect(self.__enable_edit)
        self.scrollArea.setWidgetResizable(True)
        self.__set_main_window_center()
        self.__set_alignment_table_columns()

        logging.basicConfig(
            level=logging.NOTSET,
            filename="logsparser_logs.log",
            format="%(asctime)s - %(module)s - %(levelname)s"
                   " - %(funcName)s: %(lineno)d - %(message)s",
            datefmt='%H:%M:%S',
        )
        self.config = DevelopingConfig('server_logs', 'root', 'root', 27017)
        if not self.config.check_connection():
            self.add_line_output("Database not connected")
            self.open_button_3.setEnabled(False)
            self.process_button_3.setEnabled(False)
        else:
            self.add_line_output("Database connected")
            self.open_button_3.setEnabled(True)
            self.process_button_3.setEnabled(True)
            self.config.connect_db()
            try:
                self.__set_dates()
            except:
                pass
            data = self.__read_from_db()
            if not data:
                self.tab_two.setEnabled(False)
                self.add_line_output("The database is empty, you cannot use the log analysis")
            else:
                self.tab_two.setEnabled(True)
                self.add_line_output("Load data from database")
                self.__load_data_table(data)

    def __enable_edit(self) -> None:
        if self.popular_regions_check_box_3.isChecked():
            self.num_regions_edit_3.setEnabled(True)
        else:
            self.num_regions_edit_3.setEnabled(False)

    def __set_dates(self):
        first_date = GoodLog.objects().order_by("date").first().date
        last_date = GoodLog.objects().order_by("-date").first().date
        first_date_qdate = QDate(first_date.year, first_date.month, first_date.day)
        last_date_qdate = QDate(last_date.year, last_date.month, last_date.day)
        self.first_date_edit.setMinimumDate(first_date_qdate)
        self.first_date_edit.setMaximumDate(last_date_qdate)
        self.first_date_edit.setDate(first_date_qdate)

        self.second_date_edit.setMinimumDate(first_date_qdate)
        self.second_date_edit.setMaximumDate(last_date_qdate)
        self.second_date_edit.setDate(last_date_qdate)

    def __build_graphics(self) -> None:
        corrected_flag = True
        need_plots: List[AbstractPlot] = []
        if self.ip_check_box_3.isChecked():
            need_plots.append(IpPlot())
        if self.time_check_box_3.isChecked():
            need_plots.append(TimePlot())
        if self.country_check_box_3.isChecked():
            need_plots.append(CountryPlot())
        if self.regions_check_box_3.isChecked():
            need_plots.append(RegionPlot())
        if self.popular_regions_check_box_3.isChecked():
            if not self.__check_num_regions():
                corrected_flag = False
            else:
                num = int(self.num_regions_edit_3.toPlainText())
                need_plots.append(PopularRegionsPlot(num))
        self.add_line_output("Plots are set")
        logging.info("Plots are set")

        if not need_plots:
            self.__show_error_window("Please choose type graphics")
        elif not corrected_flag:
            self.__show_error_window("Incorrected num of regions")
        else:
            self.__clear_scroll_area()
            images = self.__get_graphics(need_plots)
            size = 1000, 1000
            self.__set_images(images, size)

    def __clear_scroll_area(self) -> None:
        for i in reversed(range(self.scrollAreaWidgetContents.layout().count())):
            self.scrollAreaWidgetContents.layout().itemAt(i).widget().setParent(None)

    def __get_graphics(self, need_plots):
        first_date = self.first_date_edit.date().getDate()
        f_date = datetime.datetime(first_date[0], first_date[1], first_date[2])
        second_date = self.second_date_edit.date().getDate()
        s_date = datetime.datetime(second_date[0], second_date[1], second_date[2])
        data = GoodLog.objects(__raw__={"date": {"$gte": f_date, "$lte": s_date}})
        logs = pd.DataFrame([element.to_dict() for element in data])
        logs_analyzer: LogsAnalyzer = LogsAnalyzer(need_plots)
        images = logs_analyzer.analyze(logs)
        return images

    def __show_error_window(self, message) -> None:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def __set_images(self, images, size) -> None:
        for img in images:
            img.thumbnail(size, Image.ANTIALIAS)
            image_qt = ImageQt(img).copy()
            pixmap = QtGui.QPixmap.fromImage(image_qt)
            label = QtWidgets.QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            self.scrollAreaWidgetContents.layout().addWidget(label)
        # Effect)
        for i in range(101):
            self.progressBar_6.setValue(i)
            time.sleep(0.02)

    def __check_num_regions(self) -> bool:
        edit_text = self.num_regions_edit_3.toPlainText()
        try:
            val = int(edit_text)
            return val > 0
        except ValueError:
            return False

    def __read_from_db(self) -> List[GoodLog]:
        logs = LogFile.objects()
        return logs

    def __parse(self) -> None:
        if self.path == "":
            self.add_line_output("Please choose the file log")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please choose the file log")
            msg.setWindowTitle("Error")
            msg.exec_()
        elif not self.prepared:
            data_logs = readlogs(self.path)
            length_unfiltered = len(data_logs)
            self.add_line_output("File open and read successfully")
            conditions: List[ConditionFilterAbstract] = []
            conditions.append(ConditionRobot())
            conditions.append(ConditionPhp())
            conditions.append(ConditionPng())
            conditions.append(ConditionSvg())
            conditions.append(ConditionJs())
            conditions.append(ConditionCss())
            conditions.append(ConditionPost())
            conditions.append(ConditionWoff())
            conditions.append(ConditionGz())
            conditions.append(ConditionResponse())
            conditions.append(ConditionHead())
            logs_filter = Filter(conditions)
            common_logs_parser: AbstractParser = CommonLogsParserGui(logs_filter, self)
            start = time.process_time()
            result = common_logs_parser.parsefile(data_logs)
            end = time.process_time()
            len_good_logs = result.get_len_good_log()
            if len_good_logs == 0:
                self.add_line_output("Bad file. Don't contains logs by default format")
                self.__show_error_window("Bad file. Don't contains logs by default format")
            else:
                length_filtered = result.get_len_good_log()
                self.add_line_output(f"Percentage of records filtered"
                                     f":{length_filtered / length_unfiltered * 100}%")
                self.add_line_output(f"Time:{end - start}")

                file_name = os.path.basename(self.path)
                new_file_log = LogFile(filename=file_name,
                                       persent_filtered=length_filtered / length_unfiltered * 100,
                                       time_parsing=end - start)
                new_file_log.save()
                self.__write(result)
                self.add_line_output("The addition to the database is complete")
                self.prepared = True
                log_files = LogFile.objects()
                self.__load_data_table(log_files)
                self.__set_alignment_table_columns()
        else:
            self.add_line_output("Data already prepared.Please load other file")

    def __write(self, logs: ResultGoodBadLogs, write_bad_logs=False) -> None:
        '''Write logs to mongodb'''

        buf_good_logs: List[GoodLog] = []
        buf_bad_logs: List[BadLog] = []
        index = 0
        count = 0
        progress = 0
        length_good_logs = len(logs.get_good_logs())
        tick = length_good_logs // 100
        self.progressBar.setValue(progress)
        for log in logs.get_good_logs():
            count += 1
            if count == tick:
                progress += 1
                count = 0
                self.progressBar.setValue(progress)
            buf_good_logs.append(GoodLog(ip=log.ip_adress, user=log.user,
                                         date=log.date, time=log.time, req=log.request,
                                         res=int(log.response),
                                         byte_sent=int(log.bytesSent), referrer=log.referer,
                                         zone=log.zone, browser=log.browser))
            buf_good_logs[index].save()
            logging.info(f"{buf_good_logs} saved to db")
            index += 1

        self.add_line_output("Data saved to db")
        if write_bad_logs:
            count = 0
            for log in logs.get_bad_logs():
                buf_bad_logs.append(BadLog(data=log))
                buf_bad_logs[count].save()
                logging.info(f"{buf_bad_logs} saved to db")
                self.add_line_output(f"{buf_bad_logs} saved to db")
                count += 1

    def __set_main_window_center(self) -> None:
        '''Set main window at center'''
        frame_gm = self.frameGeometry()
        screen = PyQt5.QtWidgets.QApplication.desktop().screenNumber(
            PyQt5.QtWidgets.QApplication.desktop().cursor().pos())
        center_point = PyQt5.QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    def __set_alignment_table_columns(self) -> None:
        '''Resize width of column in rows by content'''
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

    def __load_data_table(self, data: List[LogFile]) -> None:
        '''Load MyMp3 files to table widget'''
        table = self.table
        table.setRowCount(0)
        for item in data:
            row = table.rowCount()
            table.setRowCount(row + 1)
            filename = QTableWidgetItem(item.filename)
            table.setItem(row, 0, filename)

            persent = QTableWidgetItem(str(item.persent_filtered))
            table.setItem(row, 1, persent)

            time_parsing = QTableWidgetItem(str(item.time_parsing))
            table.setItem(row, 2, time_parsing)

            date_parsing = QTableWidgetItem(str(item.date_parsing))
            table.setItem(row, 3, date_parsing)

            self.table.resizeColumnsToContents()
        # self.__disable_column(6)

    def add_line_output(self, text: str) -> None:
        now_text = self.output_text_edit_3.toPlainText()
        self.output_text_edit_3.setPlainText(f"{now_text}\n{text}")

    def __load_file(self) -> None:
        '''Open dialog for choosing mp3 file and load them to table'''
        self.path = QFileDialog.getOpenFileUrl(self, 'Open log file', filter='*')[0].path()
        if not os.path.isfile(self.path):
            self.add_line_output("Incorrect file")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Incorrect file")
            msg.setWindowTitle("Error")
            msg.exec_()
        else:
            filename = os.path.basename(self.path)
            self.add_line_output(f"File {filename} opened")
            self.path_edit_3.setText(self.path)
            self.prepared = False


class CommonLogsParserGui(AbstractParser):
    '''class for parsing coommon logs to logstructure'''

    def __init__(self, logs_filter: Filter, main_window: MainApp) -> None:
        self.filter: Filter = logs_filter
        self.main_app = main_window
        self.main_app.add_line_output("Filters are set")
        self.num_fields = 9
        self.main_app.add_line_output(f"num fileds:{self.num_fields}")
        # Format common logs
        self.pattern = re.compile(
            "^([\\d.]+) (\\S+) (\\S+) \\[([\\w:/]+\\s[+\\-]\\d{4})\\]"
            " \"(.+?)\" (\\d{3}) (\\d+) \"([^\"]+)\" \"([^\"]+)\"")
        self.main_app.add_line_output(f"pattern{self.pattern}")

    def parsefile(self, list_logs: List[str]) -> ResultGoodBadLogs:
        '''return list with list of corrected and filtered logs and list of incorrect logs'''
        parsed_logs: List[LogStruct] = []
        incomleted_logs: List[str] = []
        self.main_app.add_line_output("Logs parsing:")
        len_logs = len(list_logs)
        tick = len_logs // 100
        progress = 0
        self.main_app.progressBar_5.setValue(progress)
        count = 0
        for log in list_logs:
            count += 1
            if count == tick:
                count = 0
                progress += 1
                self.main_app.progressBar_5.setValue(progress)
            my_pattern = re.match(self.pattern, log)
            logging.critical(f"my pattern for log:{my_pattern}")
            if my_pattern is not None:
                if len(my_pattern.groups()) != self.num_fields:
                    incomleted_logs.append(f"{log}:Not enough fields\n")
                    logging.critical(f"{log}:Not enough fields")
                else:
                    curr = LogStruct(my_pattern.group(1), my_pattern.group(3),
                                     my_pattern.group(4), my_pattern.group(5),
                                     my_pattern.group(6), my_pattern.group(7),
                                     my_pattern.group(8), my_pattern.group(9))
                    logging.info(f"{curr}")
                    try:
                        if self.filter.filtering(curr):
                            parsed_logs.append(curr)
                            logging.info(f"{curr} are added successfully")
                    except Exception as exception:
                        incomleted_logs.append(log + f':{exception}\n')
                        logging.critical(f"{log}:{exception}")
            else:
                incomleted_logs.append(log + ":Don't match\n")
                logging.critical(f"{log}:Don't match")
        self.main_app.add_line_output("Logs parsing end")

        return ResultGoodBadLogs(parsed_logs, incomleted_logs)
