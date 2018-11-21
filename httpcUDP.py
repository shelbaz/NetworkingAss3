import socket
from urllib.parse import urlparse
import json
import click
import packet as Packet
import ipaddress


TCRLF = "\r\n\r\n"
CRLF = "\r\n"


def write_file(header, body):
    file = open("output.txt", "w")
    file.write(header)
    file.write(body)
    file.close()

def read_file(file_path):
    print('path:' + file_path)
    f = open(file_path, 'r')
    data_read = f.read()
    f.close()
    return data_read

def syn():
    print("Starting handshake : Sending SYN")
    packet_type = Packet.SYN




def init_connection(router_address, router_port, server_addresss, server_port):
    server_ip_address = ipaddress.ip_address(socket.gethostbyname(server_addresss))
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timeout = 5
    try:

        connection.connect((hostname, port or 80))
        connection.sendall(req.encode("UTF-8"))
        response = connection.recv(4096).decode("UTF-8")
        (response_header, response_body) = response.split(TCRLF)
        connection.close()
        return (response_header, response_body)

@click.command()
@click.option('--verbose', '-v', multiple=True, is_flag=True, help="Will print verbose")
@click.option('--routerhost', '-rh', multiple=True, help="Will print verbose messages.")
@click.option('--routerport', '-rp', multiple=True, help="Will include a header (optional)")
@click.option('--serverhost', '-sh', multiple=True, help="Will include data")
@click.option('--serverport', '-sp', multiple=True, help="Will include file")

def cli(command, verbose, routerhost, routerport, serverhost, serverport):
    init_connection(router_address, router_port, server_addresss, server_port)


if __name__ == '__main__':
    cli()

