import random
CHUNKSIZE = 8192

class ChunkHandler:
    def __init__(self):
        self.chunkSize = CHUNKSIZE # in bytes
        self.up_chunks = [] # contains uploading chunks
        self.dl_chunk_ids = [] # contains downloading chunks
        self.dl_chunk_map = {}
        self.dl_total_num_chunks = 0

    def set_dl_chunk(self, chunk_id, chunk):
        self.dl_chunk_map[chunk_id] = chunk

    def get_num_up_chunks(self):
        return len(self.up_chunks)

    def get_chunk(self, index):
        if index >= self.get_num_up_chunks():
            sys.stderr.write("Chunk index out of range\n")
        return self.up_chunks[index]

    # DOWNLOADER FUNCIONS
    def stitch_chunks(self):
        ''' Returns all the chunks in the chunk array sorted and stitched
            as one large array'''
        # TODO: untested
        sorted_ids = sorted(self.dl_chunk_ids)
        chunks = []
        for id in sorted_ids:
            chunks.append(self.dl_chunk_map[id])
        return "".join(chunks)

    # UPLOADER FUNCTIONS
    def split_file_to_chunks(self, file):
        ''' Takes in a file, opens it and splits it into chunks, and
            loads them into the chunk array.
            Assumes file is already uu.encoded and is a .txt file'''
        # TODO : untested
        with open(file) as f:
            chunk = "placeholder to make len(chunk) != 0"
            while len(chunk) != 0:
                chunk = f.read(self.chunkSize)
                if (len(chunk) != 0):
                    self.up_chunks.append(chunk)

    def get_chunk_ids_even(self):
        ''' Returns: 
            * A list of chunk ids available to seed
              as a string delimted by '-' eg. 1-45-67-22 
            * Length of the string  
            '''  

        # TODO: currently just evens
        chunk_list = []
        num_chunks = self.get_num_up_chunks()
        for i in range(0, num_chunks, 2):
            chunk_list.append(str(i))

        # Delimiter '-'
        data = "-".join(chunk_list)
        return len(data), data

    def get_chunk_ids_odd(self):
        ''' Returns: 
            * A list of chunk ids available to seed
              as a string delimted by '-' eg. 1-45-67-22 
            * Length of the string  
            ''' 

        # TODO: currently just evens
        chunk_list = []
        num_chunks = self.get_num_up_chunks()
        for i in range(1, num_chunks, 2):
            chunk_list.append(str(i))

        data = "-".join(chunk_list)
        return len(data), data