import asyncio
import socket
import threading

import select

port = 8080
host = ""


def parse_http_request(request):
    result_dict = dict()
    formatted = request.strip().split("\n")
    for line in formatted[1:]:  # first one is http method
        key = line.split(": ")[0].strip()
        value = line.split(": ")[1].strip()
        result_dict[key] = value
    return result_dict


async def handler(client):
    try:
        data = client.recv(2**16)
    except socket.error:
        data = b''

    try:
        request = data.decode("utf-8")
    except UnicodeDecodeError:
        request = data.decode("windows-1251")

    if request:
        method = request.split("\n")[0].split()[0]
        parsed_request = parse_http_request(request)
        host_header = parsed_request["Host"]
        connection_info = host_header.split(":")
        host_to_connect = connection_info[0]
        port_to_connect = int(connection_info[1])
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.connect((host_to_connect, port_to_connect))
            if method == "CONNECT":
                client.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
            elif method == "POST" or method == "GET":
                server.sendall(request)
            await channel(client, server)


async def channel(client_socket, server_socket):
    sockets = [server_socket, client_socket]
    while True:
        read_from, write_to, errors = select.select(sockets, [],
                                                    sockets, 10)  # timeout
        if len(read_from) == 0:
            server_socket.close()
            client_socket.close()
            break

        for sock in read_from:
            try:
                data = sock.recv(2**20)  # 64 kB
            except socket.error:
                data = b''
            await asyncio.gather(data)
            if len(data) == 0:
                sockets.remove(sock)
                sock.close()
                continue
            if sock == server_socket:
                try:
                    client_socket.sendall(data)
                except OSError:
                    continue
            elif sock == client_socket:
                server_socket.sendall(data)


def main():
    loop = asyncio.get_event_loop()
    coroutine = asyncio.start_server(self.handle_client_wrapper, host, port)
    server = loop.run_until_complete()


if __name__ == "__main__":
    main()
