from logs_parser.python_callables import (analyze_logs, extract_random_logs,
                                          parsing_logs, url_taker)

if __name__ == "__main__":
    url_file = extract_random_logs()
    logs = parsing_logs(url_file, url_taker)
    grades = analyze_logs(logs)
