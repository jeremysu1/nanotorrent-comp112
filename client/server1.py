import random
import socket
import threading
import os
import struct
import uu
import time
import heapq
import sys

from chunkHandler import ChunkHandler
from connection import Connection

# globals
CHUNKSIZE = 8192
DIVISOR = 100
VIZ_LOCK = threading.Lock()
    
class Server1:
    def __init__(self, host_name):
        self.host_name = host_name
        self.port = random.randint(9000, 9100)

        # make a directory to store seeding files
        self.files_dir = 'server_files'
        os.system('mkdir ' + self.files_dir)
        self.create_seed_socket()
        self.divisor = DIVISOR

    def get_port(self):
        return self.port

    #########################################################################
    #                    UPLOADING SERVER FUNCTIONS                         #
    #########################################################################
    def set_sleep_time(self, time):
        ''' Sleep time before every packet seed.
            The time will be divided by 1000'''
        self.sleep_time = time/self.divisor

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
            print("Got a connection request for {file}".format(file=filename))

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
        if (self.sleep_time*self.divisor) % 2 == 0:
            num_bytes, data = ch.get_chunk_ids_even()
            print("Seeding every chunk")
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
        #print("Sleeping for {time}s between each chunk".format(time=sleep_time))
        for i in range(total_chunks):
            time.sleep(sleep_time) # rate-limiting!!!
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
            connections[ips[i]] = Connection(host, port, filename, 
                ch.get_chunk_size(), self.host_name)
            connections[ips[i]].start()
            self.num_active_conns += 1

        # start each connection
        # for ip in connections:
            
            

        # makes sure each connection is ready
        for ip in connections:
            while connections[ip].done == False:
                pass



        total_chunks = connections[ips[0]].total_chunks
        ch.total_num_chunks = total_chunks

        # for each connection, create the priority queue of chunks
        for ip in connections:
            chunk_ids = connections[ip].chunk_ids
            ch.all_conn_chunks =  ch.all_conn_chunks + chunk_ids
        
        ch.rarest_priority_q()
        #print("pq is {pq}".format(pq=ch.rarest_heap))
        #print("total number of chunks is {total}".format(total=total_chunks))
        
        # create the dict that maps chunk to list of ips having the chunk
        #print("All conn chunks:")
        all_chunks = set(ch.all_conn_chunks)
        chunk_owners = {}
        for chunk in all_chunks:
            chunk_owners[chunk] = []
            for ip in connections:
                if chunk in connections[ip].chunk_ids:
                    chunk_owners[chunk].append(ip)
        #print(chunk_owners)

        downloaded_from = {}
        for ip in connections:
            downloaded_from[ip] = []


        while len(ch.rarest_heap) != 0:
            id_tup = ch.next_id()
            id = id_tup[1]
            owners = chunk_owners[id]
            
            fastest_conn = connections[owners[0]].conn_time
            fastest_owner = owners[0]
            for owner in owners:
                if fastest_conn > connections[owner].conn_time:
                    fastest_conn = connections[owner].conn_time
                    fastest_owner = owner

            #print("Requesting chunk {id} from {conn}".format(id=id, conn= fastest_owner))
            downloaded_from[fastest_owner].append(id)
            chunk = connections[fastest_owner].request_chunk(id)
            ch.dl_chunk_map[id] = chunk
            ch.dl_chunk_ids.append(id)
            self.viz(ch, connections, downloaded_from, ips)

        # stop all connections because all the chunks were downloaded
        for ip in connections:
            #print("Connection time of {ip} is {time}".format(ip = ip, time = connections[ip].conn_time))
            connections[ip].stop()
       # print("downloaded {dl} chunks, expected {total} chunks".format(dl=len(ch.dl_chunk_ids), 
        #                                                                total=ch.total_num_chunks))

        # if download is complete, save file as a txt file and then decode it
        if (len(ch.dl_chunk_ids) == ch.total_num_chunks):
            self.write_file(ch, filename)

    def write_file(self, ch, filename):
        Color_Off="\033[0m"
        sys.stdout.write(Color_Off)
        final_file = ch.stitch_chunks()
        with open(self.torr_dir + '/' + filename + ".txt", 'w') as f:
            f.write(final_file)
        uu.decode(self.torr_dir + "/" + filename + ".txt", 
            self.torr_dir + "/" + filename)
        os.system("rm {file}".format(file = self.torr_dir + "/" + filename + ".txt"))
        print('Download complete!')

    def viz(self, ch, connections, downloaded_from, ips):
        peer_chunks = []
        ip1 = ips[0]
        ip2 = ips[1]
        for ip in connections:
            peer_chunks.append(connections[ip].chunk_ids)

        RED   = "\033[1;31m" 
        BLUE  = "\033[1;34m"
        WHITE = "\033[1;37m"
        GREEN = "\033[0;32m"

        global VIZ_LOCK
        VIZ_LOCK.acquire()
        time.sleep(0.08)
        os.system('clear') # clears the screen  
        sys.stdout.write(GREEN)      
        print("Chunk availabilities:")
        print("Peer 1: ")
        print("Avg chunk retrieval time: {s}".format(s=connections[ip1].conn_time))
        for i in range(ch.total_num_chunks):
            if i in peer_chunks[0]:
                sys.stdout.write(RED)
                print('*', end="")
            else:
                sys.stdout.write(GREEN)
                print('_', end="")

        sys.stdout.write(GREEN)
        print("\n\nPeer 2: ")
        print("Avg chunk retrieval time: {s}".format(s=connections[ip2].conn_time))
        for i in range(ch.total_num_chunks):
            if i in peer_chunks[1]:
                sys.stdout.write(BLUE)
                print('*', end="")
            else:
                sys.stdout.write(GREEN)
                print('_', end="")

        sys.stdout.write(GREEN)
        print("\n\nDownloaded: ")
        for i in range(ch.total_num_chunks):
            if i in ch.dl_chunk_ids:
                if i in downloaded_from[ip1]:
                    sys.stdout.write(RED)
                else:
                    sys.stdout.write(BLUE)
                sys.stdout.write('*')
            else:
                sys.stdout.write(GREEN)
                sys.stdout.write('_')
        print("\n")
        sys.stdout.write(GREEN)
        VIZ_LOCK.release()

