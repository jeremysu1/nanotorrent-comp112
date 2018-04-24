

import random
import socket
import threading
import os
import struct
import uu
import time

class Connection(threading.Thread):
    def __init__(self, host, port, filename, chunk_size, host_name):
        threading.Thread.__init__(self)
        self.host = host;
        self.port = port;
        self.filename = filename;
        self.chunk_size = chunk_size
        self.host_name = host_name
        self.StopEvent = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        



    def run(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((self.host, self.port))

        self.send_file_req(self.filename, self.sock)  
        while not self.stopped():
            continue

        self.sock.close()

                # might need to wrap ch to be thread safe
        #ch.dl_chunk_map[id] = chunk
        #ch.dl_chunk_ids.append(id)


    def request_chunk(self, id):        
        # send request for chunk
        # print("Requesting chunk: {id}".format(id = id))
        msg = struct.pack('>I', id)
        self.sock.send(msg)
        # get chunk back
        return self.sock.recv(self.chunk_size).decode('ascii')

    def send_file_req(self, filename, sock):
        ''' Sends initial request to seeder about the file
            we want to download'''
        CRLF = "\r\n"
        msg = "GET / HTTP/1.1" + CRLF \
                + "Filename: " + filename + CRLF \
                + "Downloader: " + self.host_name + CRLF \
                + "Port: " + str(self.port) + CRLF + CRLF
        sock.send(msg.encode('ascii'))

    def stop(self):
        """Signals the event that this thread is looping on to stop and closes
           the socket.
     
        Args:
            Nothing
  
        Returns:
            Nothing
        """
        self.StopEvent.set()

    def stopped(self):
        """Checks to see if the event is signaled or not

        Args:
            Nothing
  
        Returns:
            True if the event is signaled, false if it is not
        """
        return self.StopEvent.isSet()


