import pika
from pika import connection
import settings
import json
from datetime import datetime
import sqlite3
from os import system
import os.path


class RMQClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.SERVER_HOST, port=settings.SERVER_PORT_RMQ, credentials=pika.PlainCredentials(settings.RMQ_USER, settings.RMQ_PASSWORD)))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=settings.RMQ_QUEUE)

    def send_data(self, data: str):
        self.channel.basic_publish(
            exchange='', routing_key=settings.RMQ_QUEUE, body=data)

    def read_from_sqlite(self, sqlite_path="DB/db.sqlite"):
        conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        print("Connected to sqlite")
        # cursor = conn.cursor()
        query = "SELECT * FROM orders"
        # cursor.execute("SELECT * FROM orders")
        orders = conn.cursor().execute(query).fetchall()
        orders = [dict(row) for row in orders]
        # print(orders)
        return orders

    def start(self):
        while True:
            print("Type path to sqlite or 0 to exit")
            message = input()

            if message == "0":
                self.connection.close()
                exit(0)
            try:
                if not os.path.isfile(message):
                    raise Exception
                orders = self.read_from_sqlite(message)
            except:
                print("Smth wrong with sqlite file")
                continue
            try:
                for item in orders:
                    encrypted_data = json.dumps(item)
                    self.send_data(data=encrypted_data)
            except:
                print("Server connection lost")
                self.connection.close()
                input()
                exit(0)


if __name__ == '__main__':
    try:
        client = RMQClient()
        client.start()
    except KeyboardInterrupt:
        print('Interrupted')
        client.connection.close()
        exit(0)
