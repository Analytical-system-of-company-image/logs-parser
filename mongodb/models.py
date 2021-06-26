from typing import Dict
from datetime import datetime
from mongoengine.fields import StringField, DateTimeField, DecimalField, FileField
from mongoengine.document import Document


class GoodLog(Document):
    '''Class with correct logs'''
    ip = StringField(required=True)
    user = StringField(required=True)
    date = DateTimeField(required=True)
    time = DateTimeField(required=True)
    req = StringField(required=True)
    res = DecimalField(required=True)
    byte_sent = DecimalField(required=True)
    referrer = StringField(required=True)
    browser = StringField(required=True)
    zone = DecimalField(required=True)

    def to_dict(self) -> Dict:
        ''':return dict from class object'''
        return {
            "IP": self.ip,
            "USER": self.user,
            "DATE": self.date,
            "TIME": self.time,
            "REQ": self.req,
            "RES": self.res,
            "BYTESENT": self.byte_sent,
            "REFERRER": self.referrer,
            "BROWSER": self.browser,
            "ZONE": self.zone
        }


class BadLog(Document):
    '''Class incorrect logs'''
    data = StringField(required=True)


class ReportLogs(Document):
    '''Class contains report pdf with plots'''
    pdf_file = FileField(required=True)
    date = DateTimeField(required=True, default=datetime.today())


class LogFile(Document):
    '''Class contains prepared files'''
    filename = StringField(required=True)
    persent_filtered = DecimalField(required=True)
    time_parsing = DecimalField(required=True)
    date_parsing = DateTimeField(required=True, default=datetime.today())
