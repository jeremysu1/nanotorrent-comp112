import os
import requests
import sys
'''
- Establish connection to tracker, get file list back
- Pick randomly 5 from swarm
- Set up connections with each five clients
- Calculate the throughputs
- Rank the 5 based on their throughput
- Periodically get new list from tracker
- Optimistically explore
'''

TRACKER_URL = 'http://nanotorrent-comp112.herokuapp.com/'

class Client:
    def __init__(self, tracker_url):
        self.dl_conns = 5
        self.tracker = tracker_url

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


if __name__ == "__main__":
    client = Client(TRACKER_URL)
    filename = client.get_filename_to_download()
    print(filename)
    
