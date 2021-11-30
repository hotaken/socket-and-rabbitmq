import os
import settings
from Socket import Socket
import json
from datetime import datetime
import sqlite3
from os import system
from sys import platform
import asyncio

from exceptions import SocketException


class SocketClient(Socket):
    def __init__(self):
        super(SocketClient, self).__init__()

    def set_up(self):
        try:
            self.socket.connect(settings.SERVER_ADDRESS)
        except ConnectionRefusedError:
            print("Server is inactive")
            input()
            exit(0)

        self.socket.setblocking(False)

    async def listen_socket(self, listened_socket):
        while True:
            if not self.is_working:
                return

            try:
                data = await super(SocketClient, self).listen_socket(listened_socket)
            except SocketException as exc:
                print("Server is inactive")
                self.is_working = False
                break

            decrypted_data = json.loads(data['data'])
            print(decrypted_data)

    async def read_from_sqlite(self, sqlite_path="DB/db.sqlite"):
        conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        print("Connected to sqlite")
        # cursor = conn.cursor()
        query = "SELECT * FROM orders"
        # cursor.execute("SELECT * FROM orders")
        orders = await self.main_loop.run_in_executor(
            None,
            lambda: conn.cursor().execute(query).fetchall()
        )
        orders = [dict(row) for row in orders]
        # print(orders)
        return orders

    async def send_data(self, data=None):
        while True:
            print("Type path to sqlite or 0 to exit")
            message = await self.main_loop.run_in_executor(None, input)
            if not self.is_working:
                return
            if message == "0":
                exit(0)
            try:
                if not os.path.isfile(message):
                    raise Exception
                orders = await self.read_from_sqlite(message)
            except:
                print("Smth wrong with sqlite file")
                continue

            for item in orders:
                # print(item)
                encrypted_data = json.dumps(item)
                await super(SocketClient, self).send_data(where=self.socket, data=encrypted_data)
            # print()

    async def main(self):

        await asyncio.gather(

            self.main_loop.create_task(self.listen_socket(self.socket)),
            self.main_loop.create_task(self.send_data())

        )


if __name__ == '__main__':
    client = SocketClient()
    client.set_up()

    client.start()
