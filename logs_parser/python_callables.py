import logging
import random
import tempfile
from typing import Callable, List

import requests
from tqdm import tqdm

from logs_parser.analyzer.analyzer import LogsAnalyzer
from logs_parser.parser.filter import (ConditionCss, ConditionFilterAbstract,
                                       ConditionGz, ConditionHead, ConditionJs,
                                       ConditionPhp, ConditionPng,
                                       ConditionPost, ConditionResponse,
                                       ConditionSvg, ConditionWoff, Filter)
from logs_parser.parser.logs_reader import read_logs
from logs_parser.parser.logs_writer import AbstractWriter, CSVWriter
from logs_parser.parser.parser import AbstractParser, CommonLogsParser


def extract_random_logs() -> str:
    """Извлекает случайный лог.
    Функция для тестов

    Returns:
        str: Название логов
    """
    logs = ["access.log-20210208", "access.log-20210209",
            "access.log-20210210", "access.log-20210211",
            "access.log-20210212", "access.log-20210213",
            "access.log-20210214", "access.log-20210215",
            "access.log-20210216", "access.log-20210217",
            "access.log-20210218", "access.log-20210219",
            "access.log-20210220", "access.log-20210221",
            "access.log-20210222", "access.log-20210223",
            "access.log-20210224", "access.log-20210225",
            "access.log-20210226", "access.log-20210227",
            "access.log-20210228", "access.log-20210301",
            "access.log-20210302", "access.log-20210303",
            "access.log-20210304", "access.log-20210305",
            "access.log-20210306", "access.log-20210307",
            "access.log-20210308", "access.log-20210309",
            "access.log-20210310", "access.log-20210311",
            "access.log-20210312", "access.log-20210313",
            "access.log-20210314", "access.log-20210315",
            "access.log-20210316", "access.log-20210317",
            "access.log-20210318", "access.log-20210319",
            "access.log-20210320", "access.log-20210321",
            "access.log-20210322", "access.log-20210323",
            "access.log-20210324", "access.log-20210325",
            "access.log-20210326", "access.log-20210327",
            "access.log-20210328", "access.log-20210329",
            "access.log,-20210330", "access.log-20210331"]

    name = random.choice(logs)
    url = f"https://raw.githubusercontent.com/Analytical-system-of-company-image/logs-parser/dev/test/logs/{name}"
    return url


def url_taker(url_file: str, dest_folder: str, dest_file: str = "tmp_file.log") -> str:
    """Функция извлечения удаленного файла

    Args:
        url_file (str): URL к файлу
        dest_folder (str): Путь куда сохранить
        dest_file (str, optional): Название файла сохранения. Defaults to "tmp_file.log".

    Returns:
        str: Путь к файлу
    """
    r = requests.get(url_file)
    path_to_folder = f"{dest_folder}/{dest_file}"
    with open(path_to_folder, "w") as f:
        f.write(r.text)
    return path_to_folder


def parsing_logs(url_file: str, url_taker: Callable, size_chunk=500000):
    """Парсинг файла с Логами

    Args:
        path_to_file (str): Путь к Файлу
        size_chunk (int, optional): Размер пакета. Defaults to 500000.
    """
    logging.basicConfig(level=logging.DEBUG,
                        filename='parsing_logs.log', filemode='w')
    wr: AbstractWriter = CSVWriter()
    conditions: List[ConditionFilterAbstract] = []
    conditions.append(ConditionPhp())
    conditions.append(ConditionPng())
    conditions.append(ConditionSvg())
    conditions.append(ConditionJs())
    conditions.append(ConditionCss())
    conditions.append(ConditionPost())
    conditions.append(ConditionWoff())
    conditions.append(ConditionGz())
    conditions.append(ConditionHead())
    logs_filter = Filter(conditions)

    commonLogsParser: AbstractParser = CommonLogsParser(logs_filter)
    result_logs = []
    with tempfile.TemporaryDirectory() as tmpdirname:

        path_to_file = url_taker(url_file, tmpdirname)
        for chunk_logs in tqdm(read_logs(path_to_file, size_chunk)):
            parsed_logs = commonLogsParser.parsefile(chunk_logs)
            tmp_logs = parsed_logs.get_good_logs()
            result_logs.extend([log.asdict() for log in tmp_logs])
            del parsed_logs, tmp_logs
    return result_logs


def analyze_logs():
    path = "good_logs:2023-07-08.csv"
    logs_analyzer: LogsAnalyzer = LogsAnalyzer()

    logs = pd.read_csv(path)
    logs.columns = ["IP", "USER", "REQ", "RES", "BYTESENT",
                    "REFERRER", "BROWSER", "TIME", "ZONE", "DATE"]
    logs["DATE"] = logs["DATE"] + "T" + logs["TIME"]
    logs["DATE"] = pd.to_datetime(
        logs["DATE"], format="%Y-%m-%dT%H:%M:%S", errors="coerce")
    logs["TIME"] = logs["DATE"].copy()
    logs = logs[~logs["DATE"].isna()]

    logs.sort_values(by='DATE', inplace=True)

    grades = logs_analyzer.analyze(logs)

    grades.to_csv("grades.csv", index=False)
