import settings
from Socket import Socket
from exceptions import SocketException
from contextlib import closing
import psycopg2
import json


class SocketServer(Socket):
    def __init__(self):
        super(SocketServer, self).__init__()
        self.users = []

    def set_up(self):
        self.socket.bind(settings.SERVER_ADDRESS)

        self.socket.listen(5)
        self.socket.setblocking(False)
        print("Server is listening")

    async def send_data(self, user, **kwargs):
        try:
            await super(SocketServer, self).send_data(where=user, data=kwargs['data'])
        except SocketException as exc:
            print("User disconnected!")
            print(exc)
            user.close()

    async def listen_socket(self, listened_socket=None):
        while True:
            try:
                data = await super(SocketServer, self).listen_socket(listened_socket)
                data = json.loads(data['data'])
                # print(data)
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
                except KeyError:
                    await self.send_data(listened_socket, data=json.dumps({"notification": "Server db and yours don't match"}))
                except psycopg2.Error as psger:
                    await self.send_data(listened_socket, data=json.dumps({"notification": "Something wrong with server db"}))
                    print("Postgres DB is inactive")
                print("Received row")

            except SocketException as exc:
                print("User disconnected!")
                self.users.remove(listened_socket)
                listened_socket.close()
                return

    async def accept_sockets(self):
        while True:
            user_socket, address = await self.main_loop.sock_accept(self.socket)
            print(f"User connected!")

            self.users.append(user_socket)
            self.main_loop.create_task(self.listen_socket(user_socket))

    async def main(self):
        await self.main_loop.create_task(self.accept_sockets())


if __name__ == '__main__':
    server = SocketServer()
    server.set_up()

    server.start()
