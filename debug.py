from logs_parser.python_callables import (analyze_logs, extract_random_logs,
                                          parsing_logs, slow_parsing_logs, url_taker)


def multiprocessing_parsing():
    url_file = extract_random_logs()
    logs = parsing_logs(url_file, url_taker)
    grades = analyze_logs(logs)


def slow_parsing():
    url_file = extract_random_logs()
    logs = slow_parsing_logs(url_file, url_taker)
    grades = analyze_logs(logs)


if __name__ == "__main__":
    slow_parsing()
