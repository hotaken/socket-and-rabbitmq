import settings
import rmq_client
import socket_client

if __name__ == "__main__":
    if settings.MTYPE == "sockets":
        print("Sockets Client")
        client = socket_client.SocketClient()
        client.set_up()

        client.start()
    else:
        print("RabbitMQ Client")
        try:
            client = rmq_client.RMQClient()
            client.start()
        except KeyboardInterrupt:
            print('Interrupted')
            client.connection.close()
            exit(0)
