# by Yael Vaisberger


# Ex 4.4 - HTTP Server Shell
# Purpose: Provide a basis for Ex. 4.4
# Note: The code is written in a simple way, without classes, log files or other utilities, for educational purpose
# Usage: Fill the missing functions and constants

# TO DO: import modules
import socket
import os

# TO DO: set constants
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 1
MAX_MSG_LENGTH = 1024
DEFAULT_URL = "file:///C:/Networks/work/webroot/webroot/index.html"
FIXED_RESPONSE = "HTTP/1.1 200 OK\r\n"
REDIRECTION_DICTIONARY = {"pageOne": "1", "pageTwo": "2", "pageThree": "3"}
CODE_404 = '<!DOCTYPE HTML PUBLIC "+"-//IETF//DTD HTML 2.0//EN"\r\n' + "<html><head>\r\n" \
           + '<title>404 Not ' + 'Found</title>\r\n' + '</head''><body>\r\n' \
           + '<h1>Not Found</h1>\r\n' + '<p>The requested URL /'


# a function that deals with code 404 not found
def code_404(client, url):
    length = 202 + len(url)
    http_header = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html;" \
                  " charset=iso-8859-1\r\nContent-Length: " + str(length) + "\r\n\r\n" + CODE_404 + \
                  url + ' was not found on this server.</p>' + '</body></html>'
    http_response = http_header.encode()
    client.send(http_response)
    return


# a function that returns files size
def get_file_size(filename):
    size = 0
    if os.path.exists(filename):
        size = os.path.getsize(filename)
    return size


# a function that opens file reads from it and returns the data
def get_file_data(filename):
    """ Get data from file """
    data = ''
    if os.path.exists(filename):
        f = open(filename, "rb")
        file_size = os.path.getsize(filename)
        data = f.read(file_size)
    return data


# a function that deals with code 302 moved temporarily and sends a different file
def redirect(client):
    fixed_response = "HTTP/1.1 302 Moved Found\r\nLocation: " +DEFAULT_URL[-11:] + "\r\n\r\n"
    response = fixed_response.encode()
    client.send(response)
    return



# a function that calculates the area of triangle from the Query
def calc_area(url, client):
    index = url.find('&')
    height = int(url[22:index])
    width = int(url[index + 7:])
    area = (height * width) / 2
    len_area = len(str(area))
    http_header = FIXED_RESPONSE + "Content-Length:" + str(len_area) + "\r\n" + "Content-Type: text/html\r\n\r\n"
    data = str(area)
    response = http_header + data
    client.send(response.encode())
    return


# a function that handles the http request and sends a response accordingly
def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    # TO DO : add code that given a resource (URL and parameters) generates the proper response
    filename = ''
    if resource == ' ':
        url = DEFAULT_URL[8:]
        filename = url
    else:
        url = resource
        filename = DEFAULT_URL[8:-10] + url
    # TO DO: check if URL had been redirected, not available or other error code. For example:
    print(url)
    val = list(REDIRECTION_DICTIONARY.keys())
    # check if a redirection should occur
    if url in val:
        redirect(client_socket)
        return
    # check for query
    if 'calculate-area' in url:
        calc_area(url, client_socket)
        return
    # check if file exists on server
    if os.path.exists(filename):
        file_size = get_file_size(filename)
        data = get_file_data(filename)
        http_header = FIXED_RESPONSE + "Content-Length:" + str(file_size) + "\r\n"
        print(filename)
        # TO DO: extract requested file tupe from URL (html, jpg etc)
        if 'html' in url or 'txt' in url:
            http_header = http_header + "Content-Type: text/html\r\n\r\n"
        elif 'jpg' in url:
            http_header = http_header + "Content-Type: image/jpeg\r\n\r\n"
        elif 'js' in url:
            http_header = http_header + "Content-Type: text/javascript\r\n\r\n"
        elif 'css' in url:
            http_header = http_header + "Content-Type: text/css\r\n\r\n"
        elif 'ico' in url:
            http_header = http_header + "Content-Type: image/octet-stream\r\n\r\n"
        elif 'gif' in url:
            http_header = http_header + "Content-Type: image/gif\r\n\r\n"
        http_response = http_header.encode() + data
        client_socket.send(http_response)
    else:
        # if the file doesnt exists returns code 404
        code_404(client_socket, url)
    return


# Checks if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
def validate_http_request(request):
    end_request = request.index("HTTP/1.1") + len("HTTP/1.1")
    url_len = request.split()
    length = len(url_len[1])
    if request[0:3] != 'GET':
        return False, ''
    if request[3] != ' ':
        return False, ''
    if request[4 + length] != ' ':
        return False, ''
    if url_len[2] != "HTTP/1.1":
        return False, ''
    if request[end_request:end_request + 2] != '\r\n':
        return False, ''
    end_dir = request.index("HTTP/1.1")
    return True, request[5:end_dir]


#  Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests
def handle_client(client_socket):
    print('Client connected')
    # while client is connected
    while True:
        client_request = client_socket.recv(MAX_MSG_LENGTH).decode()
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
            break
        else:
            print('Error: Not a valid HTTP request')
            break

    print('Closing connection')
    client_socket.close()


def main():
    # Opens a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        print(str(client_address))
        client_socket.settimeout(SOCKET_TIMEOUT)
        try:
          handle_client(client_socket)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    # Call the main handler function
    main()
