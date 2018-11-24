import socket
import threading
import argparse
import os
import sys
import ipaddress

from packet import Packet
#current directory of program
directory = os.getcwd()

def run_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('', port))
        print('Echo server is listening at', port)
        while True:
            conn, sender = sock.recvfrom(1024)
            handle_client(sock, conn, sender)

    finally:
        sock.close()


def handle_client(sock, conn, sender):
    global directory
    global args
    print ('New client from', sender)

    try:
        data = Packet.from_bytes(conn)
        if not data:
            request_error = '400 Bad Request'
            request_error = request_error.encode('utf-8')
            conn.sendto(data.to_bytes(), sender)
            return
        decoded_request = data.payload.decode('utf-8')
        decoded_body = decoded_request.split('\r\n\r\n')
        decoded_body = decoded_body[1]

        if args.v: #verbose
            print('Request received: \n' + decoded_request)

        if 'GET' in decoded_request:
            get_request(conn, decoded_request, decoded_body)
        elif 'POST' in decoded_request:
            post_request(conn, decoded_request, decoded_body)
        else:
            request_error = '400 Bad Request'
            request_error = request_error.encode('utf-8')
            conn.send(request_error)
    finally:
        conn.close()

def get_directory_files():
    list_directory = os.listdir(directory)
    all_files = ''
    for file in list_directory:
        all_files += file + '\n'

    all_files = all_files.encode('utf-8')
    return all_files


def get_request(conn, decoded_request, decoded_body):
    global directory

    if '/' == decoded_body:
        directory_files = get_directory_files()
        conn.sendall(directory_files)
        return
    #security check
    in_root = False
    root_directory_list = directory.split('\\')
    decoded_body_list = directory + decoded_body
    decoded_body_list = decoded_body_list.split('\\')
    if len(root_directory_list) == (len(decoded_body_list) - 1):
        in_root = True

    if decoded_body and in_root:
        try:
            read_directory = directory + decoded_body + '.txt'
            f = open(read_directory, 'r')
            file_text = f.read()
            file_text = file_text.encode('utf-8')
            conn.sendall(file_text)
            f.close
        except Exception as e:
            e = str(e).encode('utf-8')
            conn.send(e)
    else:
        unauthorized_error = '401 Access Unauthorized'
        unauthorized_error = unauthorized_error.encode('utf-8')
        conn.send(unauthorized_error)

def post_request(conn, decoded_request, decoded_body):
    global directory

    split_body = decoded_body.split(" ")
    #security check
    length_check = split_body[0].split('\\')
    if len(length_check) != 2:
        unauthorized_error = '401 Access Unauthorized'
        unauthorized_error = unauthorized_error.encode('utf-8')
        conn.send(unauthorized_error)
        return

    # Create or overwrite the file named bar in the data directory with the content of the body of the request.
    if len(split_body) > 0:
        try:
            write_directory = directory + split_body[0] + '.txt'
            f = open(write_directory, 'w')
            for word in split_body[1:]:
                f.write(word + ' ')
            f.close
        except Exception as e:
            e = str(e).encode('utf-8')
            conn.send(e)
            return
        finally:
            success = 'Successfully written to file ' + split_body[0] + '.txt'
            success = success.encode('utf-8')
            conn.sendall(success)

    else:
        unauthorized_error = '401 Access Unauthorized'
        unauthorized_error = unauthorized_error.encode('utf-8')
        conn.send(unauthorized_error)

def handshake(sock, conn, sender):
    status = False
    p =Packet.from_bytes(data)
    try:
        ack = Packet(packet_type=3, seq_num=1, peer_ip_addr= p.peer_ip_addr, peer_port=p.peer_port, payload= p.msg.encode("utf-8"))
        print('Sending SYN-ACK to ' + p.peer_ip_addr)
        conn.settimeout(5)
        reply, sender = sock.recvfrom(1024)
        sender_response = Packet.from_bytes(reply)
        if sender_response.packet_type == 1:
            print('ACK received')
            status = True
    except socket.timeout:
        print('Connection has timed out')
        return
    return status


# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument('-v', help = 'Prints debugging message.', action = 'store_true')
parser.add_argument('-p', help = 'Specifies the port number.', type = int, default = 8080)
parser.add_argument('-d', help = 'Specifies the directory.', type = str, default = directory)
args = parser.parse_args()
if os.path.exists(args.d):
    directory = args.d
else:
    print('Directory does not exist.')
    sys.exit(1)
run_server('', args.p)
