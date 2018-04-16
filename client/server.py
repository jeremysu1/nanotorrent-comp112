import random
import socket
import threading
import os

class Server:
    def __init__(self, host_name):
        self.host_name = host_name
        self.port = random.randint(9000,9100)
        self.create_socket()

        # make a directory to store seeding files
        self.files_dir = 'server_files'
        os.system('mkdir ' + self.files_dir)
        # try:
        #     os.system('rm -rf ' + self.files_dir)
        #     os.system('mkdir ' + self.files_dir)
        # except:
        #     os.system('mkdir ' + self.files_dir)

    def get_port(self):
        return self.port

    def create_socket(self):
        '''
        creates a socket for the server and listens at the port
        '''
        # create socket
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # remove Address in Use error
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # find a port number to bind to
        while (True):
            try:
                print("Starting server on {host}:{port}".format(host=self.host_name, 
                    port=self.port))
                self.serversocket.bind((self.host_name, self.port))
                print("Server started on port {port}.".format(port=self.port))
                break
            except Exception as e:
                print("Error: Could not bind to port {port}, "
                    "retrying now".format(port=self.port))
                self.port = random.randint(9000,9100) # pick a new port number
            
        #listen
        self.serversocket.listen(5) 

    def run(self): # not called yet
        # loop that keeps the server running
        while True:
            # establish a connection
            clientsocket,addr = self.serversocket.accept()      
            print("Got a connection from %s" % str(addr))
            threading.Thread(target=self.handle_client, 
                args=(clientsocket, addr)).start()

    def utf8len(self, s):
        ''' Returns the size of a string in bytes'''
        return len(s.encode('utf-8'))

    def handle_client(self, clientsocket, address):
        """
            Should be able to upload to the clientsocket
        """
        PACKET_SIZE = 1024
        CRLF = "\r\n"
        # Recieve request of file from client, extract filename
        cli_data = clientsocket.recv(PACKET_SIZE).decode() 
        filename = cli_data.split('Filename: ')[1].split('Downloader: ')[0].split(CRLF)[0]

        self.seed_file(filename, clientsocket)
        clientsocket.close()

    def seed_file(self, filename, clientsocket):
        with open(  self.files_dir + "/" + filename + ".txt") as f:
            resp = f.read()
   
        clientsocket.send(str(self.utf8len(resp)).encode('ascii')) # send msg len
        self.send_msg(resp, self.utf8len(resp), clientsocket)

    def send_msg(self, resp, resp_len, clientsocket):
        totalsent = 0
        while totalsent < resp_len:
            sent = clientsocket.send(resp[totalsent:].encode('ascii'))
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    
        