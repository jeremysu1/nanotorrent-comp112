#!/bin/bash
xterm -title "Node server" -hold -e "node index.js" &
sleep 5
xterm -title "Peer 2 - Initially slower" -hold -e "cd client; python3 client.py u 20 2" &
sleep 3
xterm -title "Peer 1 - Fast, then slow" -hold -e "cd client; python3 client.py u 0 2" &



