import socket
import click
import os
import packet as packetObj
import random
import ast

TCRLF = '\r\n\r\n'
CRLF = '\r\n'
CR = '\r'
LF = '\n'

sequence_number = 0
global_directory = ''
global_verbose = False


def fileDirectoryHandler(directory):
    print('inside directory handler')
    rootDirectory = os.path.dirname(os.path.realpath(__file__))
    if directory != '':
        rootDirectory = directory

    allFiles = os.listdir(rootDirectory)
    # if rootDirectory == os.path.dirname(os.path.realpath(__file__)):
    #     allFiles.remove("httpfs.py")

    return (rootDirectory, allFiles)


def init_request_split(request):
    values = ast.literal_eval(request)
    method = values[0]
    path = values [1]
    request_header = values[2]
    request_body = values[3]
    return (method, path, request_header, request_body)

def read_file(directory, file_path):
    f = open(directory + file_path + ".txt", 'r')
    data_read = f.read()
    f.close()
    return data_read

def write_file(directory, file_path, body):
    print('stuff', directory + " " + file_path)
    file = open(directory + file_path + ".txt", "w")
    file.write(str(body))
    file.close()

def send_response(connection, response):
    response += '\n'
    connection.sendall(bytes(response.encode('utf-8')))
    connection.close()

def getHandler(path, listOfFiles, rootDir, verbose):
    strippedPath = path.strip("/")
    strippedList = []
    for index in range(len(listOfFiles)):
        strippedList.append(os.path.splitext(listOfFiles[index])[0])
    if path == "/":
        if verbose:
            print("Responding with the list of files \n")
        return (str(listOfFiles) + '\n')
    else:
        if strippedPath in strippedList:
            if verbose:
                print("Contents of file: " + strippedPath + "\n")
            if (strippedPath + ".txt") not in listOfFiles:
                deniedMessage = "HTTP 404 - Error: You cannot access folder inside of this structure"
                if verbose:
                    print(deniedMessage)
                return deniedMessage
            else:
                return read_file(rootDir, path)
        else:
            errorMsg = "HTTP 404 - Error: File or directory non existent"
            if verbose:
                print(errorMsg)
            return errorMsg


def postHandler(path, listOfFiles, rootDir, verbose, body):
    strippedPath = path.strip("/")
    strippedList = []
    for index in range(len(listOfFiles)):
        strippedList.append(os.path.splitext(listOfFiles[index])[0])

    if strippedPath in strippedList:
        write_file(rootDir, path, body)
        return "File: " + path + " overwritten successfully"
    elif strippedPath not in strippedList:
        write_file(rootDir, path, body)
        return "File: " + path + " written successfully"
    else:
        errorMsg = "HTTP 403 - Action refused"
        if verbose:
            print(errorMsg)
        return errorMsg

def handle_response(connection):
    global sequence_number
    end=False
    while not end :
        data, sender_address = connection.recvfrom(1024)
        received_packet = packetObj.Packet.from_bytes(data)
        peer_ip_address = received_packet.peer_ip_addr
        peer_port = received_packet.peer_port

        print("Packet: ", received_packet)
        print("Packet type:", received_packet.packet_type)

        if(received_packet.packet_type == packetObj.SYN):
            sequence_number = random.randint(1,4294967295)
            packet_type = packetObj.SYN_ACK
            message = "Sending SYN-ACK"
            print(message)
            sending_packet = packetObj.Packet(packet_type, sequence_number, peer_ip_address, peer_port,
                                      message.encode('utf-8'))
            connection.sendto(sending_packet.to_bytes(), sender_address)

        if(received_packet.packet_type == packetObj.ACK):
            if(received_packet.seq_num ==sequence_number+1):
                print("Connection established, beginning data receive")
                ## When data finished being sent, expect FIN

        if(received_packet.packet_type == packetObj.DATA):
            print('payload', received_packet.payload.decode('unicode_escape'))
            (method, path, header, bodyData) = init_request_split(received_packet.payload.decode('unicode_escape'))
            (rootDir, listOfFiles) = fileDirectoryHandler(global_directory)
            print('method: ', method)
            print('path: ' , path)
            print('header: ', header)
            print('bodyData: ' , bodyData)
            print('rootDir:', rootDir)
            print('listOfFiles', str(listOfFiles))
            if (method == "GET" or method == "get"):
                response = getHandler(path, listOfFiles, rootDir, global_verbose)
                print('response: ', response)
                encoded_response = response.encode('utf-8')

                buffer = bytearray()
                buffer.extend(encoded_response)

                current = 0
                payloads = []

                while current < len(buffer):
                    current_data = buffer[current:current + 1012]

                    p_send = packetObj.Packet(
                        packet_type=packetObj.DATA,
                        seq_num=sequence_number,
                        peer_ip_addr=peer_ip_address,
                        peer_port=peer_port,
                        payload=current_data
                    )
                    payloads.append(p_send)
                    current += 1013

                for payload in payloads:
                    connection.sendto(payload.to_bytes(), sender_address)


                # sending_packet = packetObj.Packet(packetObj.DATA, sequence_number + 1, peer_ip_address, peer_port,
                #                                   response.encode('utf-8'))
                # print('sending packet: ', sending_packet)
                #
                #
                #
                # data, sender_address = connection.recvfrom(1024)
                # received_packet = packetObj.Packet.from_bytes(data)
                connection.sendto(sending_packet.to_bytes(), sender_address)
            elif (method == "POST" or method == "post"):
                # body = request.split at data defining body
                response = postHandler(path, listOfFiles, rootDir, global_verbose, bodyData)

                encoded_response = response.encode('utf-8')

                buffer = bytearray()
                buffer.extend(encoded_response)

                current = 0
                payloads = []

                while current < len(buffer):
                    current_data = buffer[current:current + 1012]

                    p_send = packetObj.Packet(
                        packet_type=packetObj.DATA,
                        seq_num=sequence_number,
                        peer_ip_addr=peer_ip_address,
                        peer_port=peer_port,
                        payload=current_data
                    )
                    payloads.append(p_send)
                    current += 1013

                for payload in payloads:
                    connection.sendto(payload.to_bytes(), sender_address)


                # sending_packet = packetObj.Packet(packetObj.DATA, sequence_number + 1, peer_ip_address, peer_port,
                #                                   response.encode('utf-8'))
                # print('sending packet: ', sending_packet)
                # data, sender_address = connection.recvfrom(1024)
                # received_packet = packetObj.Packet.from_bytes(data)
                # connection.sendto(sending_packet.to_bytes(), sender_address)
            else:
                print("Incorrect request format")
                end=True

        if(received_packet.packet_type == packetObj.FIN):
            ## sending ACK for received FIN
            message = "Sending ACK"
            sending_packet = packetObj.Packet(packetObj.ACK, sequence_number+1, peer_ip_address, peer_port,
                                      message.encode('utf-8'))
            connection.sendto(sending_packet.to_bytes(), sender_address)
            ## sending FIN
            message = "Sending FIN"
            sending_packet = packetObj.Packet(packetObj.FIN, random.randint(1,4294967295), peer_ip_address, peer_port,
                                      message.encode('utf-8'))
            connection.sendto(sending_packet.to_bytes(), sender_address)
            ## wait for ACK for sent FIN
            print("Connection is closed")
            connection.close()
            end=True

    # finally:
    #     print("Connection is forcefully closed")
    #     connection.close()


def init_connection(port):
    hostname = ''
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connection.bind((hostname, port))
    print("Listening on port " + str(port))

    handle_response(connection)

    # return (request, connection, request_header, request_body)

@click.command()
@click.option('--port', '-p' , type=int, default=8007, help="Specifies a port number or default=8080")
@click.option('--directory', '-d', type=str, default='/', help="Specifies read/write directory or default is root")
@click.option('--verbose', '-v', is_flag=True, help="Will print verbose messages.")
def cli(port, directory, verbose):
    global global_verbose
    global global_directory
    init_connection(port)
    if verbose:
        global_verbose = True
    if directory:
        global_directory = directory


    # (method, path) = process_request(request)
    # (rootDir, listOfFiles) = fileDirectoryHandler(directory)
    # if verbose:
    #     print("--------------------------------------------------------------")
    #     print("headerData: \n" + str(headerData) + "\n")
    #     print("--------------------------------------------------------------")
    #     print("bodyData: \n" + str(bodyData) + "\n")
    #     print("--------------------------------------------------------------")
    #     print("listOfFiles: \n" + str(listOfFiles) + "\n")
    #
    # response = ""
    # if method == "GET":
    #     response = getHandler(path, listOfFiles, rootDir, verbose)
    # elif method == "POST":
    #     response = postHandler(path, listOfFiles, rootDir, bodyData, verbose)
    #
    # send_response(connection, response)

if __name__ == '__main__':
    cli()


