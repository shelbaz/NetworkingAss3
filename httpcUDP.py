import socket
from urllib.parse import urlparse
import json
import click
import packet as packetObj
import ipaddress
import random


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

# CLIENT: Start connection, send SYN packet
# SERVER: Receives with SYN, sends SYN_ACK packet
# CLIENT: Sends back ACK packet with next seq number , also send Data in next packet with length
# SERVER: Responds with ACK (first packet), Responds with ACK of length
# LOOP Between Client and server: Send back and forth data until connection closed


def get():
    return


def post():
    return


def syn(connection, router_address, router_port, server_ip_address, server_port):
    message = "Starting handshake : Sending SYN"
    packet_type = packetObj.SYN
    sequence_number = random.randint(0,4294967295)  # 4 byte unsigned int (0-> 4294967295)
    response = create_and_send_packet(connection, packet_type, sequence_number, server_ip_address, server_port,
                                      (router_address, router_port), message)
    return response

def ack(connection, router_address, router_port, sequence_number, server_ip_address, server_port):
    packet_type = packetObj.ACK
    message = "Sending ACK"
    response = create_and_send_packet(connection, packet_type, sequence_number+1, server_ip_address, server_port, (str(router_address), router_port), message)
    return response

def data(connection, router_address, router_port, sequence_number, server_ip_address, server_port, message):
    packet_type = packetObj.DATA
    print("Sending DATA")
    response = create_and_send_packet(connection, packet_type, sequence_number+1, server_ip_address, server_port, (str(router_address), router_port), str(message))
    return response

def create_and_send_packet(connection, packet_type, sequence_number, server_ip_address, server_port, server_address, message):
    packet = packetObj.Packet(packet_type, sequence_number, server_ip_address, server_port, message.encode('utf-8'))
    return connection.sendto(packet.to_bytes(), server_address)

def init_connection(router_address, router_port, server_addresss, server_port, command, header, bodydata, file, output):
    server_ip_address = ipaddress.ip_address(socket.gethostbyname(server_addresss))
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timeout = 5
    try:
        syn(connection, router_address, router_port, server_ip_address, server_port)
        connection.settimeout(timeout)
        packet_type = -1
        while(packet_type != packetObj.SYN_ACK):
            response, sender = connection.recvfrom(1024)
            packet = packetObj.Packet.from_bytes(response)
            packet_type = packet.packet_type
            print("Payload:" + packet.payload.decode('utf-8'))
            print("Packet type", packet.packet_type)
            print("Seq Number", packet.seq_num)

            if (packet.packet_type == packetObj.DATA):
                print(packet)
                print('Client received final payload: ', packet.payload.decode('unicode_escape'))

            if(packet.packet_type == packetObj.SYN_ACK):
                ack(connection, packet.peer_ip_addr, packet.peer_port, packet.seq_num, server_ip_address, server_port)
                print("Connection established")
                message = [command, '/', header, bodydata] ## placeholder for path
                if (command.lower() == 'get'):
                    if (header):
                        print("we got a header - get")
                        data(connection, packet.peer_ip_addr, packet.peer_port, packet.seq_num, server_ip_address, server_port,
                             message)
                        if output:
                            print('writing file')
                            write_file(header, bodydata)
                    else:
                        print("no header - get")
                        data(connection, packet.peer_ip_addr, packet.peer_port, packet.seq_num, server_ip_address, server_port,
                             message)
                        if output:
                            print('writing file')
                            write_file(header, bodydata)


                elif (command.lower() == "post"):
                    if (header and bodydata):
                        print("we got a header and data = post")

                        data(connection, packet.peer_ip_addr, packet.peer_port,packet.seq_num, server_ip_address, server_port,
                             message)
                        if output:
                            print('writing file')
                            write_file(header, bodydata)

                    elif (header and file):
                        print("we got a header and file = post")

                        returned_data = read_file(str(bodydata))
                        print('data-read: ' + returned_data)
                        message = [header, returned_data]
                        data(connection, packet.peer_ip_addr, packet.peer_port, packet.seq_num, server_ip_address, server_port,
                             message)
                        if output:
                            print('writing file')
                            write_file(header, bodydata)

                    elif (header):
                        print("we got a header = post")
                        data(connection, packet.peer_ip_addr, packet.peer_port, packet.seq_num, server_ip_address, server_port,
                             message)
                        if output:
                            print('writing file')
                            write_file(header, bodydata)

                    else:
                        print("no header or data = post")
                        data(connection, packet.peer_ip_addr, packet.peer_port, packet.seq_num, server_ip_address, server_port,
                             message)
                        if output:
                            print('writing file')
                            write_file(header, bodydata)


    except socket.timeout:
        print('No response after {}s'.format(timeout))
    finally:
        print("Closing connection")
        connection.close()
        # connection.connect((hostname, port or 80))
        # connection.sendall(req.encode("UTF-8"))
        # response = connection.recv(4096).decode("UTF-8")
        # (response_header, response_body) = response.split(TCRLF)
        # connection.close()
        # return (response_header, response_body)

@click.command()
@click.argument('command')
@click.option('--verbose', '-v', is_flag=True, help="Will print verbose")
@click.option('--header', '-h', type=str, help="Passes a header to the request" )
@click.option('--bodydata', '-d', type=str, help="Passes data to the request")
@click.option('--file', '-f', multiple=True, help="Will include file")
@click.option('--output', '-o', multiple=True, is_flag=True, help="Will write to file")
@click.option('--routerhost', '-rh', type=str, default='localhost', help="Assign router host ip")
@click.option('--routerport', '-rp', type=str, default=3000, help="Assign router port number")
@click.option('--serverhost', '-sh', type=str, default='localhost', help="Assign server host ip")
@click.option('--serverport', '-sp', type=str, default=8007, help="Assign server port number")

def cli(verbose, routerhost, routerport, serverhost, serverport, command, header, bodydata, file, output):
    init_connection(routerhost, routerport, serverhost, serverport, command, header, bodydata, file, output)


if __name__ == '__main__':
    cli()

