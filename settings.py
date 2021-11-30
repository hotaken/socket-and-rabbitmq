import os
from dotenv import load_dotenv

load_dotenv('.env')

ENCODING = os.environ['ENCODING']
SERVER_HOST = os.environ['SERVER_HOST']
SERVER_PORT = int(os.environ['SERVER_PORT'])
SERVER_PORT_RMQ = int(os.environ['SERVER_PORT_RMQ'])
RMQ_USER = os.environ['RMQ_USER']
RMQ_PASSWORD = os.environ['RMQ_PASSWORD']
RMQ_QUEUE = os.environ['RMQ_QUEUE']

SERVER_ADDRESS = (os.environ['SERVER_HOST'], int(os.environ['SERVER_PORT']))
ENCRYPTION_KEY = int(os.environ['ENCRYPTION_KEY'])

DATABASE = os.environ['DATABASE']
USER = os.environ['USER']
PASSWORD = os.environ['PASSWORD']
DATABASE_HOST = os.environ['DATABASE_HOST']

MTYPE = "sockets"
MTYPE = "rmq"
