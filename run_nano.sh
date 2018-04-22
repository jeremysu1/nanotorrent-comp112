#!/bin/bash
xterm -title "Node server" -hold -e "node index.js" &
sleep 1
xterm -title "Seed 1" -hold -e "cd client; python3 client.py u 2" &
xterm -title "Seed 2" -hold -e "cd client; python3 client.py u 3" &

