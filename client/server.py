import random
import socket
import threading
import os
import struct
import uu

from chunkHandler import ChunkHandler

# globals
CHUNKSIZE = 8192
    
class Server:
    def __init__(self, host_name):
        self.host_name = host_name
        self.port = random.randint(9000, 9100)
        self.chunk_size = CHUNKSIZE

        # make a directory to store seeding files
        self.files_dir = 'server_files'
        os.system('mkdir ' + self.files_dir)
        self.create_seed_socket()
        self.ch = ChunkHandler()

    def get_port(self):
        return self.port

    #########################################################################
    #                    UPLOADING SERVER FUNCTIONS                         #
    #########################################################################

    def create_seed_socket(self):
        ''' Creates a socket for the server and listens at the port'''

        # create socket
        self.up_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # remove Address in Use error
        self.up_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # find a port number to bind to
        while (True):
            try:
                print("Starting server on {host}:{port}".format(host=self.host_name, 
                    port=self.port))
                self.up_socket.bind((self.host_name, self.port))
                print("Server started on port {port}.".format(port=self.port))
                break
            except Exception as e:
                print("Error: Could not bind to port {port}, "
                    "retrying now".format(port=self.port))
                self.port = random.randint(9000,9100) # pick a new port number
            
        #listen
        self.up_socket.listen(5) 

    def run(self):
        ''' Runs the server '''
        while True:
            # listen for incoming requests
            clientsocket,addr = self.up_socket.accept()      
            print("Got a connection from %s" % str(addr))
            threading.Thread(target=self.handle_client, 
                args=(clientsocket, addr)).start()

    def handle_client(self, clientsocket, address):
        """
            Sends the leech the available packets we have to seed
            and then waits for response
        """
        PACKET_SIZE = 1024
        CRLF = "\r\n"

        # Recieve request of file from client, extract filename
        cli_data = clientsocket.recv(PACKET_SIZE).decode() 
        if (cli_data[:6] == "GET / "):
            filename = cli_data.split('Filename: ')[1].split('Downloader: ')[0].split(CRLF)[0]
            print("Got a GET request for {file}".format(file=filename))

            length = self.send_chunk_list(filename, clientsocket)

            # self.seed_file(filename, clientsocket)
            for i in range(length):
                req = clientsocket.recv(4)
                if (len(req) == 0):
                    break
                id = struct.unpack('>I', req[:4])[0]
                chunk = self.ch.get_chunk(id)
                clientsocket.send(chunk.encode('ascii'))

            clientsocket.close()

    def send_chunk_list(self, filename, clientsocket):
        ''' Opens file, determines the number of available chunks
            to seed, and sends that list to the socket'''
        
        self.ch.split_file_to_chunks(self.files_dir + "/" + filename + ".txt")
        num_bytes, data = self.ch.get_chunk_ids_even()
    
        # send total number in complete file
        length = self.ch.get_num_up_chunks()
        encoded_length = struct.pack('>I', length)
        encoded_bytes = struct.pack('>I', num_bytes)

        clientsocket.send(encoded_length) 
        clientsocket.send(encoded_bytes) 
        clientsocket.send(data.encode('ascii')) # send actual delimited data
        return length

    def seed_file(self, filename, clientsocket):
        num_chunks = self.ch.get_num_chunks()
        for i in range(0, num_chunks, 2):
            chunk = self.ch.get_chunk(i)
            self.send_msg(resp, self.utf8len(chunk), clientsocket)

    def send_msg(self, resp, resp_len, clientsocket):
        totalsent = 0
        while totalsent < resp_len:
            sent = clientsocket.send(resp[totalsent:].encode('ascii'))
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def utf8len(self, s):
        ''' Returns the size of a string in bytes'''
        return len(s.encode('utf-8'))

    #########################################################################
    #                    DOWNLOADING SERVER FUNCTIONS                       #
    #########################################################################
    
    def download_setup(self):
        # make a directory to store seeding files
        self.torr_dir = 'torrented'
        os.system('mkdir ' + self.torr_dir)

    def download_file(self, filename, ips):
        self.download_setup()
        # TODO: get a mechanism to choose which IP to download
        # from!
        # For now just download from the first in the list
        print(ips)
        host1 = ips[0].split(":")[0]
        port1 = int(ips[0].split(":")[1])

        host2 = ips[1].split(":")[0]
        port2 = int(ips[1].split(":")[1])  

        self.dl_ch = ChunkHandler()  

        threading.Thread(target=self.set_peer_conn, 
                args=(host1, port1, filename)).start()

        threading.Thread(target=self.set_peer_conn, 
                args=(host2, port2, filename)).start()

    def set_peer_conn(self, host, port, filename):
        CRLF = "\r\n"
        # create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        # remove Address in use error
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((host, port))         

        msg = "GET / HTTP/1.1" + CRLF \
                + "Filename: " + filename + CRLF \
                + "Downloader: " + self.host_name + CRLF \
                + "Port: " + str(self.port) + CRLF + CRLF
        sock.send(msg.encode('ascii'))
        
        first = sock.recv(4)
        second = sock.recv(4)
        total_num_chunks = struct.unpack('>I', first[:4])[0]
        num_bytes = struct.unpack('>I', second[:4])[0]

        self.dl_ch.total_num_chunks = total_num_chunks
        chunk_ids = self.receive_chunk_ids(sock, num_bytes)

        print(chunk_ids)
        for id in chunk_ids:
            chunk = self.request_chunk(int(id), sock)
            print("Received chunk: {id}".format(id = id))
            self.dl_ch.dl_chunk_map[int(id)] = chunk
            self.dl_ch.dl_chunk_ids.append(int(id))

        if (len(self.dl_ch.dl_chunk_ids) == self.dl_ch.total_num_chunks):
            final_file = self.build_chunk_list()

            # store the file as a txt file and then decode it
            with open(self.torr_dir + '/' + filename + ".txt", 'w') as f:
                f.write(final_file)
            
            uu.decode(self.torr_dir + "/" + filename + ".txt", 
                self.torr_dir + "/" + filename)


        print(len(self.dl_ch.dl_chunk_ids)) 
        print(self.dl_ch.total_num_chunks)

        sock.close()

    def build_chunk_list(self):
        return self.dl_ch.stitch_chunks()

    def request_chunk(self, id, sock):        
        # send request for chunk
        print("Requesting chunk: {id}".format(id = id))
        msg = struct.pack('>I', id)
        sock.send(msg)
        # get chunk back
        return sock.recv(self.chunk_size).decode('ascii')

    def receive_chunk_ids(self, sock, num_bytes):
        ''' First recieves the number of bytes in data, 
            then recieves the actual chunk_id data, parses it and
            returns as a list of numbers'''
        chunk_list = sock.recv(num_bytes).decode('ascii').split('-')

        return chunk_list

    def receive_torrented_file(self, sock, filename):
        ''' 
        '''       
        # recieve the actual file as a bytes object
        file = self.receive_msg(sock)        

        # store the file as a txt file and then decode it
        with open(self.torr_dir + '/' + filename + ".txt", 'w') as f:
            f.write(file.decode('ascii'))
        
        uu.decode(self.torr_dir + "/" + filename + ".txt", 
            self.torr_dir + "/" + filename)

    # def receive_msg(self, sock):
    #     ''' Recieves message from socket chunk by chunk and returns 
    #         complete message as a bytes object'''
    #     chunks = []
    #     bytes_recd = 0
    #     while bytes_recd < file_len:
    #         chunk = sock.recv(min(file_len - bytes_recd, 8192))
    #         if chunk == b'':
    #             raise RuntimeError("socket connection broken")
    #         chunks.append(chunk)
    #         bytes_recd = bytes_recd + len(chunk)
    #     return b''.join(chunks)
    #     