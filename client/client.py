import os
import requests
import sys
import socket
import uu
import time

# our own modules
from server import Server
from server1 import Server1
from server2 import Server2
import nano_stats as stats

# TRACKER_URL = 'http://nanotorrent-comp112.herokuapp.com/'
TRACKER_URL = 'http://localhost:5000'
HOST_NAME = '127.0.0.1' # default 
demo = 0

####################### AUXILARY FUNCTIONS ################################
def parse_commandline(argv):
    global demo
    # Todo: This does not completely type check
    if (len(argv) == 3 and argv[1] == 'd'):
        demo = int(argv[2])
        return argv[1], 0
    elif (len(argv) == 4 and argv[1] == 'u'):
        demo = int(argv[3])
        return argv[1], int(argv[2])
    elif (len(argv) == 3 and argv[1] == 'u'):
        return argv[1], int(argv[2])

    #elif (len(argv) != 2 or (argv[1] != 'u' and argv[1] != 'd')):
    #    err() 
    
    return argv[1], 0

def err():
    sys.stderr.write("Usage: python3 client1.py u [speed]\n")
    sys.stderr.write("             OR\n")
    sys.stderr.write("Usage: python3 client1.py d\n")
    sys.stderr.write(" where u is for upload and d is for download\n")   
    sys.exit()
###########################################################################

class Client:
    ''' Stores loaded files in dir as txt files'''
    def __init__(self, tracker_url, host_name):
        self.dl_conns = 5 # max number of peers to download from
        self.host_name = host_name
        self.tracker = tracker_url

        # every node needs to be a serve to get an ip & port number
        if demo == 0:
            print("Normal Mode")
            self.server = Server(self.host_name) # start upload server
            self.port = self.server.get_port()
        elif demo == 1:
            print("Demo 1")
            self.server = Server1(self.host_name) # start upload server
            self.port = self.server.get_port()
        elif demo == 2:
            print("Demo 2")
            self.server = Server2(self.host_name) # start upload server
            self.port = self.server.get_port()
        
    #########################################################################
    #                    DOWNLOADING CLIENT FUNCTIONS                       #
    #########################################################################
    
    def get_downloadable_file_list(self):
        ''' Queries the tracker and returns the list of
            files available to download'''
        resp = requests.get(self.tracker)
        data = resp.json()
        self.file_list = data # json {filename : [ip:port, ip:port...]}
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

    def download_file(self, filename):
        ips = self.file_list[filename]
        self.server.download_file(filename, ips)
        
    #########################################################################
    #                    UPLOADING CLIENT FUNCTIONS                         #
    #########################################################################
    def load_file_from_disk(self, filename):
        ''' Opens a file and stores it in the server files directory
            as a txt file '''
        uu.encode(filename, self.server.files_dir + "/" + filename + ".txt") # for compatibility with all file types
        
    def join_swarm(self, filename):
        params = {"filename":filename, "ip":self.host_name + ":" + str(self.port)}
        r = requests.post(self.tracker + "/join", data = params)
        print("Joined Swarm for {filename}".format(filename = filename))

    def wait_for_request(self):
        self.server.run()

if __name__ == "__main__":
    mode, limiting_speed = parse_commandline(sys.argv)
    client = Client(TRACKER_URL, HOST_NAME)

    ''' if mode is u
        then it loads a file from disk and then joins the swarm
    '''
    if mode == 'u':
        # filename = input("Enter filename to upload: ")
        filename = 'cat.mp4'
        client.server.set_sleep_time(limiting_speed)
        client.load_file_from_disk(filename)
        client.join_swarm(filename)
        client.wait_for_request()
    else: # else it requests a download
        filename = client.get_filename_to_download()
        client.download_file(filename)

