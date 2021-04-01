from ParserLogs.filereader import FileReader
from ParserLogs.parser import Parser
from ParserLogs.filewriter import FileWriter

if __name__ == '__main__':
    fr = FileReader()
    datalogs = fr.readlogs('logs.txt')
    parser = Parser()
    result = parser.parsefile(datalogs)
    wr = FileWriter()
    wr.writetocsv(result[0], "goodlogs")
    wr.writetocsv(result[1], "badlogs")
