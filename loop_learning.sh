#!/bin/bash
COUNTER=0
while [  $COUNTER -lt 10 ]; do
    echo The counter is $COUNTER
    ./playgame.py --nolaunch -e --player_seed 42 --end_wait=0.25 --verbose --log_dir game_logs --turns 500 --map_file maps/test/maze/maze_04p_02.map     "python sample_bots/python/HunterBot.py"     "python sample_bots/python/LeftyBot.py"      "python sample_bots/python/GreedyBot.py"     "python sample_bots/python/SarsaBotV8.py"
    let COUNTER=COUNTER+1 
done
