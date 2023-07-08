# LogsParser
Common log parser and analyzer

## Project structure

## How to dev
```
poetry shell
poetry install
```

***
```
├── debug.py
├── docs
│   ├── context diagram.drawio
│   └── uml.drawio
├── logs_parser
│   ├── analyzer - analyzer for logs
│   │   ├── analyzer.py
│   │   ├── data - data for IP2Location Lib
│   │   │   ├── IP2LOCATION-LITE-DB11.BIN
│   │   │   ├── LICENSE_LITE.TXT
│   │   │   └── README_LITE.TXT
│   │   └── plots.py - plots (deprecated)
│   ├── parser (multithread parser)
│   │   ├── filter.py - filter decorators
│   │   ├── logs_reader.py - logs reader
│   │   ├── log_structure.py - data classes
│   │   ├── logs_writer.py - logs writers
│   │   └── parser.py - parser
│   └── python_callables.py - callables for Airflow
├── notebooks - Jupyter notebooks,some experiment
│   ├── experiment.ipynb
│   └── gorod_09102021_231021.csv
├── poetry.lock
├── pyproject.toml
├── README.md
└── scripts - utils
    ├── split_logs.py
    └── unite_logs.py

```
***
## Arhitecture contex diagram

![image](https://user-images.githubusercontent.com/25473820/138543868-2eca1741-7ae4-47ba-bd86-05437461cb20.png)

## UML diagram

![image](https://user-images.githubusercontent.com/25473820/138544987-9a0e92aa-5bf8-4589-bdab-12bbd741b155.png)

## How to public to Pypi
First you need create api on pypi

```bash
poetry config pypi-token.pypi $(cat .token)
poetry publish --build
```