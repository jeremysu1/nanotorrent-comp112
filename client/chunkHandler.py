import random
import operator
import heapq
import sys
from collections import Counter

CHUNKSIZE = 8192


class ChunkHandler:
    def __init__(self):
        self.chunkSize = CHUNKSIZE # in bytes
        self.up_chunks = [] # contains uploading chunks

        self.dl_chunk_ids = [] # contains downloading chunk ids
        self.dl_chunk_map = {} # id : chunk
        self.dl_total_num_chunks = 0
        self.total_num_chunks = 352
        # helper variables to calculate rarest chunks
        self.all_conn_chunks = [] # contains chunk ids from all conns

    def get_chunk_size(self):
        return self.chunkSize

    # DOWNLOADER FUNCIONS
    def set_dl_chunk(self, chunk_id, chunk):
        self.dl_chunk_map[chunk_id] = chunk

    def stitch_chunks(self):
        ''' Returns all the chunks in the chunk array sorted and stitched
            as one large array'''
        sorted_ids = sorted(self.dl_chunk_ids)
        chunks = []
        for id in sorted_ids:
            chunks.append(self.dl_chunk_map[id])
        return "".join(chunks)

    # UPLOADER FUNCTIONS
    def rarest_priority_q(self):
        count_dict = dict(Counter(self.all_conn_chunks))    
        # make priority queue with rarest chunk at the top
        h = []
        for chunk_id in count_dict.keys():
            heapq.heappush(h, (count_dict[chunk_id], chunk_id))
        self.rarest_heap = h

    # get next rarest id from priority queue
    def next_id(self):
        next = heapq.heappop(self.rarest_heap)
        return next

    def get_chunk(self, index):
        if index >= self.get_num_up_chunks():
            sys.stderr.write("Chunk index out of range\n")
        return self.up_chunks[index]

    def get_num_up_chunks(self):
        return len(self.up_chunks)

    def split_file_to_chunks(self, file):
        ''' Takes in a file, opens it and splits it into chunks, and
            loads them into the chunk array.
            Assumes file is already uu.encoded and is a .txt file'''
        with open(file) as f:
            chunk = "placeholder to make len(chunk) != 0"
            while len(chunk) != 0:
                chunk = f.read(self.chunkSize)
                if (len(chunk) != 0):
                    self.up_chunks.append(chunk)

    # gives every chunk id
    def get_chunk_ids_even(self):
        ''' Returns: 
            * A list of chunk ids available to seed
              as a string delimted by '-' eg. 1-45-67-22 
            * Length of the string  
            '''  
        chunk_list = []
        num_chunks = self.get_num_up_chunks()
        for i in range(0, num_chunks, 1):
            chunk_list.append(str(i))

        # Delimiter '-'
        data = "-".join(chunk_list)
        return len(data), data

    # gives the odd numbered chunk ids
    def get_chunk_ids_odd(self):
        ''' Returns: 
            * A list of chunk ids available to seed
              as a string delimted by '-' eg. 1-45-67-22 
            * Length of the string  
            '''  
        chunk_list = []
        num_chunks = self.get_num_up_chunks()
        for i in range(1, num_chunks, 2):
            chunk_list.append(str(i))

        # Delimiter '-'
        data = "-".join(chunk_list)
        return len(data), data

    # gives the 1st quarter and second half of chunk ids for cat.mp4
    def get_chunk_ids_fast(self):
        ''' Returns: 
            * A list of chunk ids available to seed
              as a string delimted by '-' eg. 1-45-67-22 
            * Length of the string  
            '''  
        chunk_list = []
        num_chunks = self.get_num_up_chunks()
        for i in range(0, 88):
            chunk_list.append(str(i))
        for i in range(176, 352):
            chunk_list.append(str(i))

        # Delimiter '-'
        data = "-".join(chunk_list)
        return len(data), data

    # gives the 2nd quarter and second half of chunk ids for cat.mp4
    def get_chunk_ids_slow(self):
        ''' Returns: 
            * A list of chunk ids available to seed
              as a string delimted by '-' eg. 1-45-67-22 
            * Length of the string  
            ''' 
        chunk_list = []
        num_chunks = self.get_num_up_chunks()
        for i in range(88, 352):
            chunk_list.append(str(i))

        data = "-".join(chunk_list)
        return len(data), data