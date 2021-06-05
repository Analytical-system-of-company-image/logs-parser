from mongoengine import Document
from mongoengine.fields import StringField, DateTimeField, DecimalField
from datetime import datetime


class GoodLog(Document):
    ip = StringField(required=True)
    user = StringField(required=True)
    date = DateTimeField(required=True)
    time = DateTimeField(required=True)
    req = StringField(required=True)
    res = DecimalField(required=True)
    byte_sent = DecimalField(required=True)
    referrer = StringField(required=True)


class BadLog(Document):
    data = StringField(required=True)
