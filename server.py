import settings
import rmq_server
import socket_server

if __name__ == "__main__":
    if settings.MTYPE == "sockets":
        server = socket_server.SocketServer()
        server.set_up()

        server.start()
    else:
        try:
            server = rmq_server.RMQServer()
            server.start()
        except KeyboardInterrupt:
            print('Interrupted')
            server.connection.close()
            exit(0)
