import random
import socket
import threading

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
        # PACKET_SIZE = 1024
        # cli_data = clientsocket.recv(PACKET_SIZE).decode() # Recieve data packet from client and decode
        # # extract host info from client request
        # host = cli_data.split("\nHost: ")[1].split("\nLine: ")[0]
        # path = cli_data.split(" HTTP/1.1")[0].split("GET ")[1]
        # key = host+path

        # if (self.cache.cache_hit(key)):
        #     resp = self.cache.get_page_from_cache(key)
        # else:
        #     try :
        #         get_str = cli_data.replace('\n', '\r\n')
        #         # connect to server
        #         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #         # s.settimeout(5)
        #         s.connect((host, 80))
        #         # sock.settimeout(None)
        #         s.send(get_str.encode('ascii')) # send req to server
        #         resp = s.recv(1000000) # get response back
        #         self.cache.put_in_cache(key,resp.decode('ascii'))

        #     except Exception as e:
        #         resp = "Could not connect to server".encode('ascii')

        # # send to client
        # clientsocket.send(resp)
        # clientsocket.close()
        # s.close()
        # print("\nCache hits so far: {h}".format(h=self.cache.get_cache_hits()))
        