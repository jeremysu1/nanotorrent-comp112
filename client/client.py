import os
import requests
import sys
import random
import socket
import uu

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

####################### AUXILARY FUNCTIONS ################################
def parse_commandline(argv):
    if (len(argv) != 2 or (argv[1] != 'u' and argv[1] != 'd')):
        sys.stderr.write("Usage: python3 client1.py [mode]\n")
        sys.stderr.write(" [mode] = u / d\n")
        sys.stderr.write(" where u is for upload and d is for download\n")   
    return argv[1]
###########################################################################

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
        self.server.create_socket()
        self.port = self.server.get_port()


    #########################################################################
    #                    DOWNLOADING CLIENT FUNCTIONS                       #
    #########################################################################

    def get_downloadable_file_list(self):
        ''' Queries the tracker and returns the list of
            files available to download'''
        resp = requests.get(self.tracker)
        data = resp.json()
        self.file_list = data
        return list(data.keys())

    def get_filename_to_download(self):
        filenames = self.get_downloadable_file_list()
        os.system('clear') # clears the screen

        print("Hello! These are the files available for download:\n")
        for name in filenames:
            print(name)
        user_input = input("\nPick a file to download: ")

        if self.filename_is_valid(user_input, filenames):
            return user_input

    def filename_is_valid(self, name, name_list):
        if name in name_list:   
            return True
        else:
            print("Invalid filename.")
            sys.exit()

    def download_file(self):
        print(self.file_list)

    #########################################################################
    #                    UPLOADING CLIENT FUNCTIONS                         #
    #########################################################################


    def load_file_from_disk(self, filename):
        os.system('rm temp.txt')
        uu.encode(filename, "temp.txt") # for compatibility with all file types
        with open("temp.txt") as f:
            self.my_files[filename] = f.read()
        
    def join_swarm(self, filename):
        params = {"filename":filename, "ip":self.host_name + ":" + str(self.port)}
        r = requests.post(self.tracker + "/join", data = params)
        print("Joined Swarm for {filename}".format(filename = filename))

    def wait_for_request(self):
        self.server.run()

if __name__ == "__main__":
    mode = parse_commandline(sys.argv)
    client = Client(TRACKER_URL, HOST_NAME)

    ''' if mode is u
        then it loads a file from disk and then joins the swarm
    '''
    if mode == 'u':
        # filename = input("Enter filename to upload: ")
        filename = 'sec.mp4'
        client.load_file_from_disk(filename)
        client.join_swarm(filename)
        client.wait_for_request()
    else: # else it requests a download
        filename = client.get_filename_to_download()
        client.download_file()
