from peewee import *
from common.db_config import BaseModel

# On passe title, et image_url en textfield pour éviter la limite de 255 caractères
class NewsData(BaseModel):
    title = TextField()  
    link = CharField(unique=True)
    published = DateTimeField(index=True)
    summary = TextField()
    source = CharField()
    image_url = TextField(null=True)  # peut être null
    sentiment = FloatField(null=True)  # peut être null car traité après :)

    class Meta:
        table_name = 'news_data'

