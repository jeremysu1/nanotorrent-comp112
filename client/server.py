import random
import socket
import threading
import os
import struct
import uu
import time
import heapq

from chunkHandler import ChunkHandler
from connection import Connection

# globals
CHUNKSIZE = 8192
    
class Server:
    def __init__(self, host_name):
        self.host_name = host_name
        self.port = random.randint(9000, 9100)

        # make a directory to store seeding files
        self.files_dir = 'server_files'
        os.system('mkdir ' + self.files_dir)
        self.create_seed_socket()

    def get_port(self):
        return self.port

    #########################################################################
    #                    UPLOADING SERVER FUNCTIONS                         #
    #########################################################################
    def set_sleep_time(self, time):
        ''' Sleep time before every packet seed.
            The time will be divided by 1000'''
        self.sleep_time = time/1000

    def create_seed_socket(self):
        ''' Creates a socket for the server and listens at the port'''

        # create socket, remove Address in Use error
        self.up_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            sock, addr = self.up_socket.accept()      
            print("Got a connection from %s" % str(addr))
            threading.Thread(target=self.handle_client, 
                args=(sock, addr)).start()

    def handle_client(self, sock, address):
        """
            Sends the leech the available packets we have to seed
            and then waits for response
        """
        PACKET_SIZE = 1024
        CRLF = "\r\n"
        ch = ChunkHandler() # declare a chunk handler for the upload

        # Recieve request of file from client, extract filename
        cli_data = sock.recv(PACKET_SIZE).decode() 
        if (cli_data[:6] == "GET / "):
            filename = cli_data.split('Filename: ')[1].split('Downloader: ')[0].split(CRLF)[0]
            print("Got a GET request for {file}".format(file=filename))

            total_chunks = self.send_chunk_list(ch, filename, sock)
            self.seed_file(ch, total_chunks, sock)
            sock.close()

    def send_chunk_list(self, ch, filename, sock):
        ''' ch : upload chunk handler object
            Opens file, determines the number of available chunks
            to seed, and sends :
                1. number of total packets in file
                2. number of bytes in list
                3. list as a string '''
        
        ch.split_file_to_chunks(self.files_dir + "/" + filename + ".txt")

        # multiplying by 1000 to avoid roundoff to 0
        if (self.sleep_time*1000) % 2 == 0:
            num_bytes, data = ch.get_chunk_ids_even()
            print("Seeding evens")
        else:
            num_bytes, data = ch.get_chunk_ids_odd()
            print("Seeding odds")

        # send total number in complete file
        length = ch.get_num_up_chunks()
        encoded_length = struct.pack('>I', length)
        encoded_bytes = struct.pack('>I', num_bytes)

        sock.send(encoded_length) 
        sock.send(encoded_bytes) 
        sock.send(data.encode('ascii')) # send actual delimited data

        return length

    def seed_file(self, ch, total_chunks, sock):
        sleep_time = self.sleep_time

        for i in range(total_chunks):
            #time.sleep(sleep_time) # rate-limiting!!!
            req = sock.recv(4)
            if (len(req) == 0):
                break
            id = struct.unpack('>I', req[:4])[0]
            chunk = ch.get_chunk(id)
            sock.send(chunk.encode('ascii'))

    #########################################################################
    #                    DOWNLOADING SERVER FUNCTIONS                       #
    #########################################################################
    
    def download_setup(self):
        # make a directory to store seeding files
        self.torr_dir = 'torrented'
        os.system('mkdir ' + self.torr_dir)
        self.num_active_conns = 0
        self.start_download = False

    def download_file(self, filename, ips):
        ''' For each ip that the filename is connected to,
            start a new connection '''
        self.download_setup()
        ch = ChunkHandler() 
        self.total_ips = len(ips)
        connections = {}

        # set up each connection thread
        for i in range(len(ips)):
            host = ips[i].split(":")[0]
            port = int(ips[i].split(":")[1])
            connections[ips[i]] = Connection(host, port, filename, ch.get_chunk_size(), self.host_name)
            #threading.Thread(target=self.set_peer_conn, 
            #    args=(host, port, filename, ch)).start()

        
        for ip in connections:
            connections[ip].start()
            self.num_active_conns += 1

        # makes sure each connection is ready
        for ip in connections:
            while connections[ip].done == False:
                pass

        # CODE TO REQUEST A CHUNK FROM A CONNECTION THREAD
        # peer 1 - even chunks
        # peer 2 - odd chunks

        # WITHOUT THROTTLE - 4min 30s
        # WITH THROTTLE - 4min 40s
        # SUPER THROTTLE /10 - 35min 54s

        # wait until the first connection is done getting its chunk id list
        #total_chunks = -1
        #while total_chunks == -1:
        #    total_chunks = connections[ips[0]].total_chunks
        total_chunks = connections[ips[0]].total_chunks

        # for each connection, create the priority queue of chunks
        ch.total_num_chunks = total_chunks
        for ip in connections:
            chunk_ids = connections[ip].chunk_ids
            ch.all_conn_chunks =  ch.all_conn_chunks + chunk_ids
        ch.rarest_priority_q()

        print("total number of chunks is {total}".format(total=total_chunks))
        
        while len(ch.rarest_heap) != 0:
            id = ch.next_id()[1]
            for ip in connections:
                if id in connections[ip].chunk_ids:
                    print("trying to get chunk {id}".format(id=id))
                    chunk = connections[ip].request_chunk(id)
                    ch.dl_chunk_map[id] = chunk
                    ch.dl_chunk_ids.append(id)
        # get odds

        '''
        chunk_ids = connections[ips[0]].chunk_ids
        print("size of chunks is {len}".format(len=len(chunk_ids)))
        for id in chunk_ids:
            print("trying to get chunk {id}".format(id=id))
            chunk = connections[ips[0]].request_chunk(id)
            ch.dl_chunk_map[id] = chunk
            ch.dl_chunk_ids.append(id)

        # get evens
        print("GETTING EVENS NOW")
        chunk_ids = connections[ips[1]].chunk_ids
        for id in chunk_ids:
            print("trying to get chunk {id}".format(id=id))
            chunk = connections[ips[1]].request_chunk(id)
            ch.dl_chunk_map[id] = chunk
            ch.dl_chunk_ids.append(id)
        '''
            #print("Received chunk: {id}".format(id = str(id)))
        print("Should have gotten all chunks")            

        # if download is complete, save file as a txt file and then decode it
        #start = time.time()
        for ip in connections:
            connections[ip].stop()
        print("{dl}, {total}".format(dl=len(ch.dl_chunk_ids), total=ch.total_num_chunks))
        if (len(ch.dl_chunk_ids) == ch.total_num_chunks):
            print("writing file")
            final_file = ch.stitch_chunks()
            with open(self.torr_dir + '/' + filename + ".txt", 'w') as f:
                f.write(final_file)
            uu.decode(self.torr_dir + "/" + filename + ".txt", 
                self.torr_dir + "/" + filename)

        #end = time.time()
        #print("it took {time} to stitch".format(time=end-start))


        # tell each connection thread to stop and close the socket


        # start another thread to make rarest chunk priority queue
        print("down low")
        #threading.Thread(target=self.build_rarest_pq, 
         #       args=(ch,)).start()

    def build_rarest_pq(self, ch):
        while (True):
            if self.num_active_conns == self.total_ips:
                ch.rarest_priority_q()
                self.start_download = True
                print("Priority queue built!")
                break

    def set_peer_conn(self, host, port, filename, ch):
        ''' ch: download chunk handler object '''
        
        # create a socket object, remove Address in use error
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.connect((host, port))         

        self.send_file_req(filename, sock)  
        chunk_ids = self.receive_chunk_ids(sock, ch)
        ch.all_conn_chunks += chunk_ids # for rare chunk calculations
        self.num_active_conns += 1

        if (self.start_download): # all conns have been queried
            # add each chunk to the download list and map
            for id in chunk_ids:
                chunk = self.request_chunk(id, sock, ch)
                #print("Received chunk: {id}".format(id = str(id)))
                ch.dl_chunk_map[id] = chunk
                ch.dl_chunk_ids.append(id)

            # if download is complete, save file as a txt file and then decode it
            if (len(ch.dl_chunk_ids) == ch.total_num_chunks):
                final_file = ch.stitch_chunks()
                with open(self.torr_dir + '/' + filename + ".txt", 'w') as f:
                    f.write(final_file)
                uu.decode(self.torr_dir + "/" + filename + ".txt", 
                    self.torr_dir + "/" + filename)

            print(len(ch.dl_chunk_ids)) 
            print(ch.total_num_chunks)

        sock.close()

    def send_file_req(self, filename, sock):
        ''' Sends initial request to seeder about the file
            we want to download'''
        CRLF = "\r\n"
        msg = "GET / HTTP/1.1" + CRLF \
                + "Filename: " + filename + CRLF \
                + "Downloader: " + self.host_name + CRLF \
                + "Port: " + str(self.port) + CRLF + CRLF
        sock.send(msg.encode('ascii'))

    def request_chunk(self, id, sock, ch):        
        # send request for chunk
        # print("Requesting chunk: {id}".format(id = id))
        msg = struct.pack('>I', id)
        sock.send(msg)
        # get chunk back
        return sock.recv(ch.get_chunk_size()).decode('ascii')

    def receive_chunk_ids(self, sock, ch):
        ''' Recieves the total number of chunks in the file,
            the total number of bytes in the chunk-list string
            and then the chunk-list string. Parses the
            chunk-list and returns a list of chunk-ids '''
        total_chunks = sock.recv(4)
        total_chunks = struct.unpack('>I', total_chunks[:4])[0]

        num_bytes = sock.recv(4)
        num_bytes = struct.unpack('>I', num_bytes[:4])[0]

        ch.total_num_chunks = total_chunks
        chunk_list = sock.recv(num_bytes).decode('ascii').split('-')
        chunk_list = [int(chunk) for chunk in chunk_list]
        return total_chunks, chunk_list
