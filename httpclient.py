#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        url = urllib.parse.urlparse(url)
        hostname = url.hostname
        port = url.port
        path = url.path

        if port == None:
            port = 80

        if not path.endswith('/'):
            path += '/'

        return hostname, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = int(data.split(' ')[1])
        return code

    def get_headers(self,data):
        header = data.split("\r\n\r\n")[0]
        return header

    def get_body(self, data):
        data = data.split("\r\n\r\n")
        body = data[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        url = self.get_host_port(url)

        header = 'GET {0} HTTP/1.1\r\n'.format(url[2])
        header += 'Host: {0}\r\n'.format(url[0])
        header += 'Connection: close\r\n'
        header += 'Accept: */*\r\n\r\n'

        self.connect(url[0], url[1])
        self.sendall(header)

        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)

        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        url = self.get_host_port(url)

        if args == None:
            length = 0
            content = ''
        else:
            content = urllib.parse.urlencode(args)
            length = len(content)
        
        header = 'POST {0} HTTP/1.1 \r\nHost: {1}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {2}\r\nConnection: close\r\n\r\n{3}'.format(url[2], url[0], length, content)
        self.connect(url[0], url[1])
        self.sendall(header)
        data = self.recvall(self.socket)
        code = self.get_code(data)
        body = self.get_body(data)

        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
