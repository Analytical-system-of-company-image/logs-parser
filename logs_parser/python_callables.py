import logging
import random
import tempfile
from typing import Any, Callable, Dict, List

import pandas as pd
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
from logs_parser.parser.parser import AbstractParser, CommonLogsParser, SlowCommonLogsParser


def extract_random_logs() -> str:
    """Извлекает случайный лог.
    Функция для тестов

    Returns:
        str: Название логов
    """
    logs = ["fixed_access.log-20210208", "fixed_access.log-20210209",
            "fixed_access.log-20210210", "fixed_access.log-20210211",
            "fixed_access.log-20210212", "fixed_access.log-20210213",
            "fixed_access.log-20210214", "fixed_access.log-20210215",
            "fixed_access.log-20210216", "fixed_access.log-20210217",
            "fixed_access.log-20210218", "fixed_access.log-20210219",
            "fixed_access.log-20210220", "fixed_access.log-20210221",
            "fixed_access.log-20210222", "fixed_access.log-20210223",
            "fixed_access.log-20210224", "fixed_access.log-20210225",
            "fixed_access.log-20210226", "fixed_access.log-20210227",
            "fixed_access.log-20210228", "fixed_access.log-20210301",
            "fixed_access.log-20210302", "fixed_access.log-20210303",
            "fixed_access.log-20210304", "fixed_access.log-20210305",
            "fixed_access.log-20210306", "fixed_access.log-20210307",
            "fixed_access.log-20210308", "fixed_access.log-20210309",
            "fixed_access.log-20210310", "fixed_access.log-20210311",
            "fixed_access.log-20210312", "fixed_access.log-20210313",
            "fixed_access.log-20210314", "fixed_access.log-20210315",
            "fixed_access.log-20210316", "fixed_access.log-20210317",
            "fixed_access.log-20210318", "fixed_access.log-20210319",
            "fixed_access.log-20210320", "fixed_access.log-20210321",
            "fixed_access.log-20210322", "fixed_access.log-20210323",
            "fixed_access.log-20210324", "fixed_access.log-20210325",
            "fixed_access.log-20210326", "fixed_access.log-20210327",
            "fixed_access.log-20210328", "fixed_access.log-20210329",
            "fixed_access.log-20210330", "fixed_access.log-20210331"]

    name = random.choice(logs)
    url = f"https://raw.githubusercontent.com/Analytical-system-of-company-image/logs-parser/dev/tests/logs/{name}"
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


def slow_parsing_logs(url_file: str, url_taker: Callable, size_chunk=500000):
    """Медленный парсинг файла с Логами

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

    commonLogsParser: AbstractParser = SlowCommonLogsParser(logs_filter)
    result_logs = []
    with tempfile.TemporaryDirectory() as tmpdirname:

        path_to_file = url_taker(url_file, tmpdirname)
        for chunk_logs in tqdm(read_logs(path_to_file, size_chunk)):
            parsed_logs = commonLogsParser.parsefile(chunk_logs)
            tmp_logs = parsed_logs.get_good_logs()
            result_logs.extend([log.asdict() for log in tmp_logs])
            del parsed_logs, tmp_logs
    return result_logs


def analyze_logs(logs: List[str]) -> List[Dict[str, Any]]:
    logs_analyzer: LogsAnalyzer = LogsAnalyzer()

    df_logs = pd.DataFrame(logs)
    df_logs.columns = ["IP", "USER", "REQ", "RES", "BYTESENT",
                       "REFERRER", "BROWSER", "TIME", "ZONE", "DATE"]
    df_logs["DATE"] = df_logs["DATE"] + "T" + df_logs["TIME"]
    df_logs["DATE"] = pd.to_datetime(
        df_logs["DATE"], format="%Y-%m-%dT%H:%M:%S", errors="coerce")
    df_logs["TIME"] = df_logs["DATE"].copy()
    df_logs = df_logs[~df_logs["DATE"].isna()]
    df_logs["RES"] = df_logs["RES"].astype(int)

    df_logs.sort_values(by='DATE', inplace=True)

    grades = logs_analyzer.analyze(df_logs)

    return grades.to_dict("records")
