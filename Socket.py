import socket
import asyncio
import struct
import json

import settings
from exceptions import SocketException


class Socket:
    def __init__(self):
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self.is_working = False

        self.main_loop = asyncio.new_event_loop()

    async def send_data(self, **kwargs):
        try:
            where = kwargs['where']
            del kwargs['where']

            data = self._encode_data(kwargs)
            meta_data = struct.pack(">I", len(data))
            await self.main_loop.sock_sendall(where, meta_data + data)

        except (KeyError, UnicodeEncodeError, ConnectionError, ValueError, OSError) as exc:
            raise SocketException(exc)

    async def _recv_message(self, listened_socket: socket.socket, message_len: int):
        message = bytearray()
        packet_size = 64
        while len(message) < message_len:
            if message_len - len(message) > packet_size:
                reading_size = packet_size
            else:
                reading_size = message_len - len(message)
            packet = await self.main_loop.sock_recv(listened_socket, reading_size)
            if packet is None:
                return None

            message.extend(packet)

        return message

    def _encode_data(self, data):
        return json.dumps(data).encode(settings.ENCODING)

    def _decode_data(self, data: bytes):
        return json.loads(data.decode(settings.ENCODING))

    async def listen_socket(self, listened_socket):
        try:
            meta_data = await self._recv_message(listened_socket, 4)
            meta_data = struct.unpack(">I", meta_data)[0]

            data = await self._recv_message(listened_socket, meta_data)
            return self._decode_data(data)
        except (UnicodeDecodeError, json.JSONDecodeError, IndexError, ConnectionError, OSError) as exc:
            raise SocketException(exc)

    async def main(self):
        raise NotImplementedError()

    def start(self):
        self.is_working = True
        self.main_loop.run_until_complete(self.main())

    def set_up(self):
        raise NotImplementedError()
