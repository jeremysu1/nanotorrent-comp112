import os
import requests
import sys
import random
import socket

'''
- Establish connection to tracker, get file list back /
- Pick randomly 5 from swarm /
- Set up connections with each five clients
- Calculate the throughputs
- Rank the 5 based on their throughput
- Periodically get new list from tracker
- Optimistically explore
'''

# TRACKER_URL = 'http://nanotorrent-comp112.herokuapp.com/'
TRACKER_URL = 'http://localhost:5000'
HOST_NAME = '127.0.0.1' # default 

class Server:
    def __init__(self, host_name):
        self.host_name = host_name
        self.port = random.randint(9000,9100)
        self.create_socket()

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

    def handle_client(self, clientsocket, address):
        """
            Should be able to upload to the clientsocket
        """
        print("I'm supposed to be handling client requests!")


class Client:
    def __init__(self, tracker_url, host_name):
        self.dl_conns = 5 # max number of peers to download from
        self.my_files = {}
        self.host_name = host_name
        self.tracker = tracker_url
        self.server = Server(self.host_name)
        self.port = self.server.get_port()

    def get_downloadable_file_list(self):
        ''' Queries the tracker and returns the list of
            files available to download'''
        resp = requests.get(self.tracker)
        data = resp.json()
        return list(data.keys())

    def get_filename_to_download(self):
        filenames = self.get_downloadable_file_list()
        os.system('clear') # clears the screen

        print("Hello! These are the files available for download:")
        print()
        for name in filenames:
            print(name)
        print()
        user_input = input("Pick a file to download: ")

        if self.filename_is_valid(user_input, filenames):
            return user_input

    def filename_is_valid(self, name, name_list):
        if name in name_list:   
            return True
        else:
            print("Invalid filename.")
            sys.exit()

    def load_file_from_disk(self, filename):
        f = open(filename, 'r')
        self.my_files[file_name] = f.read()
        f.close()

    def join_swarm(self, filename):
        params = {"filename":filename, "ip":self.host_name + ":" + str(self.port)}
        print(self.tracker)
        print(params)
        r = requests.post(self.tracker + "/join", data = params)
        print(r.text)

if __name__ == "__main__":
    client = Client(TRACKER_URL, HOST_NAME)
    filename = client.get_filename_to_download()
    print(filename)
    client.join_swarm(filename)