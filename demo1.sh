#!/bin/bash
xterm -title "Node server" -hold -e "node index.js" &
sleep 5
xterm -title "Peer 1 - Every Chunk" -hold -e "cd client; echo 'cat.mp4' | python3 client.py u 2 1" &
xterm -title "Peer 2 - Odd Chunks" -hold -e "cd client; echo 'cat.mp4' | python3 client.py u 3 1" &
sleep 3
xterm -title "Leech" -hold -e "cd client; echo 'cat.mp4' | python3 client.py d 1" &