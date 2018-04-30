A simplified Bittorrent tracker and client.

This project focues on the rate-limiting and node-selection
of bittorrent clients.

Made by Jeremy Su and Bhushan Suwal

Setup Instructions:
1. Clone the repo
2. Run '''sh setup.sh''' to install dependencies

If you want to run the demo which demonstrates the torrent
application's 'getting rare chunk first' feature, run '''sh demo1.sh'''.

If you want to run the demo which demonstrates the torrent
application's 'Choosing fastest peers'  feature, run '''sh demo2.sh'''.

If instead you want to run the torrent client interactively with control over
which file the seeding peer can upload, run

	'''python3 client.py u [delay]'''

	where the option 'u' states the peer is uploading while 
	the delay is an integer whose upload will be rate-limited 
	by delay milliseconds after every chunk.

An example command would be 
	'''python3 client.py u 1'''

Next, run the following instructions on the terminal:
	'''cd client'''
	'''echo 'cat.mp4' | python3 client.py d'''