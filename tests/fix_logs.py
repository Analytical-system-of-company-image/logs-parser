import os
import re

from tqdm import tqdm

from logs_parser.parser.logs_reader import read_logs
from logs_parser.parser.logs_writer import CSVWriter

names_logs = ["access.log-20210208", "access.log-20210209",
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
              "access.log-20210330", "access.log-20210331"]


def fix_logs():
    path_dir = os.getcwd() + "/tests/logs"
    for name_file in tqdm(names_logs, "processing files"):
        path_to_file = f"{path_dir}/{name_file}"
        data_logs = next(read_logs(path_to_file))
        with open(f"{path_dir}/fixed_{name_file}", 'w') as f:
            for line in tqdm(data_logs, name_file):
                newline = re.sub(r'\s-.{1,10}]', ']', line)
                try:
                    res_status = re.search(r']\s\d\d\d\s\"', newline)
                    status = newline[res_status.start() +
                                     2:res_status.end() - 2]
                except Exception as e:
                    f.write(line + "\n")
                    continue
                newline = newline.replace(f" {status}", '')
                res_request = re.search(r'\".*HTTP.*\"\s\d', newline)
                try:
                    request = newline[res_request.start():res_request.end() - 2]
                except Exception:
                    request = "\"\""
                newline = newline.replace(request, request + f' {status}')
                newline = newline[:len(newline) - 4]
                f.write(newline + "\n")
