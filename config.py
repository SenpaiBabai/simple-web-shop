import os

from dotenv import load_dotenv

load_dotenv()

USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
unprocessed_queue = os.getenv('UNPROCESSED_QUEUE')
processed_queue = os.getenv('PROCESSED_QUEUE')
host = os.getenv('HOST')
local_host=os.getenv('LOCALHOST')
group_id='my_consumer_group1'
topic=os.getenv('TOPIC')
key='pupa'
