import pika
import sys
import os
import settings
from contextlib import closing
import psycopg2
import json


class RMQServer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.SERVER_HOST, port=settings.SERVER_PORT_RMQ, credentials=pika.PlainCredentials(settings.RMQ_USER, settings.RMQ_PASSWORD)))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=settings.RMQ_QUEUE)

        self.channel.basic_consume(
            queue=settings.RMQ_QUEUE, on_message_callback=self.get_message, auto_ack=True)

    def get_message(self, ch, method, properties, body):
        data = json.loads(body.decode("utf-8"))
        try:
            with closing(
                psycopg2.connect(
                    dbname=settings.DATABASE,
                    user=settings.USER,
                    password=settings.PASSWORD,
                    host=settings.DATABASE_HOST)
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO clients (client_id, client_phone, client_email) VALUES (%s ,%s, %s) ON CONFLICT DO NOTHING",
                                   (data['client_id'], data['client_phone'], data['client_email']))
                    cursor.execute("INSERT INTO employees (employee_id, employee_name) VALUES (%s ,%s) ON CONFLICT DO NOTHING",
                                   (data['employee_id'], data['employee_name']))
                    cursor.execute("INSERT INTO orders (order_id, order_date, order_date_end, client_id, employee_id) VALUES (%s ,%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                                   (data['order_id'], data['order_date'], data['order_date_end'], data['client_id'], data['employee_id']))
                    cursor.execute("INSERT INTO models (model_id, model_date, model_name) VALUES (%s ,%s, %s) ON CONFLICT DO NOTHING",
                                   (data['model_id'], data['model_date'], data['model_name']))
                    cursor.execute("INSERT INTO products (product_id, product_date, order_id, model_id) VALUES (%s ,%s, %s, %s) ON CONFLICT DO NOTHING",
                                   (data['product_id'], data['product_date'], data['order_id'], data['model_id']))
                conn.commit()
        except KeyError as kr:
            print(kr)
        except psycopg2.Error as psger:
            print("Postgres DB is inactive")
        print("Received row")

    def start(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()


if __name__ == '__main__':
    server = RMQServer()
    server.start()
