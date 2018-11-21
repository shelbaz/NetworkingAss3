import socket
from urllib.parse import urlparse
import json
import click
from packet import Packet
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


def get(full_url, headers=None, verbose=False, output=False):

    (request, hostname, port) = build_request("GET", full_url, headers)
    (response_header, response_body) = init_connection(request, hostname, port)

    if verbose:
        print(response_header)

    if output:
        write_file(response_header, response_body)

    print(response_body)

def post(full_url, headers=None, data="", verbose=False, output=False):

    (request, hostname, port) = build_request("POST", full_url, headers, data)
    (response_header, response_body) = init_connection(request, hostname, port)

    if verbose:
        print(response_header)

    print(response_body)

    if output:
        write_file(response_header, response_body)

    return None


def init_connection(req, hostname, port):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    connection.connect((hostname, port or 80))
    connection.sendall(req.encode("UTF-8"))
    response = connection.recv(4096).decode("UTF-8")
    (response_header, response_body) = response.split(TCRLF)
    connection.close()
    return (response_header, response_body)

def build_request(req_type, url, headers=None, body=""):

    if headers == None:
        headers = {}

    url = urlparse(url)

    hostname = url.hostname
    path = url.path or "/"
    query = url.query
    port = url.port or 80

    uri = "{}?{}".format(path, query) if query else path

    formatted_headers = "".join(
        '{}:{}'.format(k, v) for k, v in headers.items())

    if req_type == "POST":
        requestPost = "POST " + uri + " HTTP/1.1" + CRLF + "Host: " + hostname + CRLF + "Content-Length: " + str(
            len(body)) + CRLF + "Content-Type: application/json"  + CRLF + formatted_headers + TCRLF + body
        return (requestPost, hostname, port)
    else:
        requestGet = "GET " + uri + " HTTP/1.1" + CRLF + "Host:" + hostname + CRLF + formatted_headers + TCRLF
        return (requestGet, hostname, port)

@click.command()
@click.argument('command')
@click.argument('url')
@click.option('--verbose', '-v', multiple=True, is_flag=True, help="Will print verbose messages.")
@click.option('--header', '-h', multiple=True, help="Will include a header (optional)")
@click.option('--data', '-d', multiple=True, help="Will include data")
@click.option('--file', '-f', multiple=True, help="Will include file")
@click.option('--output', '-o', multiple=True, is_flag=True, help="Will write to file")

def cli(command, url, verbose, header, data, file, output):

    if(command.lower() == 'get'):
        if(header):
            print("we got a header")
            get(url, json.loads(header) , verbose, output)
        else:
            print("no header")
            get(url , verbose=verbose, output=output)
    elif (command.lower() == "post"):
        if (header and data):
            print("we got a header and data")
            post(url, json.loads(header), data=data, verbose=verbose, output=output)
        elif(header and file):
            returned_data = read_file(str(data))
            print('data-read: ' + returned_data)
            post(url, json.loads(header), data=returned_data, verbose=verbose, output=output)
        elif (header):
            print("we got a header")
            post(url, json.loads(header), data="", verbose=verbose, output=output)
        else:
            print("no header or data")
            post(full_url=url, verbose=verbose, output=output)

if __name__ == '__main__':
    cli()

