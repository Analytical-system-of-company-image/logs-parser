from mongoengine import Document
from mongoengine.fields import StringField, DateTimeField, DecimalField, FileField
from datetime import datetime
from typing import Dict

class GoodLog(Document):
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
    data = StringField(required=True)


class ReportLogs(Document):
    pdf_file = FileField(required=True)
    date = DateTimeField(required=True, default=datetime.today())