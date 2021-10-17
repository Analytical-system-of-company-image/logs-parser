import logging
from mongoengine.connection import connect, disconnect, get_db


class DevelopingConfig():
    '''Class for connection with mongo database (docker-container) for developing'''

    def __init__(self, namedb, username, passw, port):
        self.database = namedb
        self.username = username
        self.password = passw
        self.port = port

    def check_connection(self) -> bool:
        '''check connection for database'''
        try:
            connect("testdb", host="mongodb://" + self.username
                                   + ":" + self.password + "@localhost:"
                                   + str(self.port) + '/?authSource=admin')
            data_base = get_db()
            data_base.command('dbstats')
            logging.fatal("Database connected successfully")
            disconnect()
            return True
        except Exception:
            logging.fatal("Database not connected")
            return False

    def connect_db(self) -> None:
        '''connection to database'''
        connect(self.database,
                host="mongodb://" + self.username + ":" +
                     self.password + "@localhost:" + str(self.port) + '/?authSource=admin')

    def disconnect_db(self) -> None:
        '''disconnect database'''
        disconnect()
