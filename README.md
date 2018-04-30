A simplified Bittorrent tracker and client.
Made by Jeremy Su and Bhushan Suwal

This project focuses on investigating and visualizing two main features
of a bittorrent application:
1. How a peer chooses which chunks of the file to download first (rarest-first) 
2. How a peer chooses clients to leech from (fastest bandwidth)

Setup Instructions:
1. Clone the repo
2. To install dependencies, run
	
	sh setup.sh

If you want to run the demo which demonstrates the torrent
application's 'getting rare chunk first' feature, run 
	
	sh demo1.sh

If you want to run the demo which demonstrates the torrent
application's 'Choosing fastest peers'  feature, run 
	
	sh demo2.sh

If instead you want to run the torrent client interactively with control over
which file the seeding peer can upload, run
	
	python3 client.py u [delay]

where the option 'u' states the peer is uploading while 
the delay is an integer whose upload will be rate-limited 
by delay milliseconds after every chunk.

An example command would be 
	
	python3 client.py u 1

Next, run the following instructions on the terminal:
	
	cd client
	echo 'cat.mp4' | python3 client.py d