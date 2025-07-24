from peewee import *
from common.db_config import BaseModel
import datetime

class PriceData(BaseModel):
    timestamp = DateTimeField(default=datetime.datetime.now(datetime.timezone.utc), index=True)
    asset = CharField()
    price = FloatField()

    class Meta:
        table_name = 'price_data'
        primary_key = CompositeKey('timestamp', 'asset')