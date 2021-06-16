def readlogs(filepath: str) -> str:
    '''read logs from txt file'''
    with  open(filepath) as file:
        return file.read().split('\n')
