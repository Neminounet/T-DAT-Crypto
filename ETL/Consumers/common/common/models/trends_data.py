from peewee import *
from common.db_config import BaseModel

class TrendsData(BaseModel):
    timestamp = DateTimeField(index=True)
    keyword = CharField()
    interest = IntegerField()
    is_partial = BooleanField()

    class Meta:
        table_name = 'trends_data'
        primary_key = CompositeKey('timestamp', 'keyword')
