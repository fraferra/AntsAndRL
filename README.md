# Sample package instructions

## Running bots locally

We include some sample scripts `play_one_game.sh` and `play_one_game_live.sh` to get you started,
but we expect you will eventually want to play around with the main `playgame.py` script a bit more
yourself.

    cd sample_bots/java
    gradle jar
    cd ../..

    # Demo of how to use the driver script - viz runs in browser at the end
    ./play_one_game.sh

    # Similar, but viz runs continuously in an Java app
    ./play_one_game_live.sh

## Uploading bots

You must upload a zip called ants-\*.zip (\* can be anything), which contains at the top level either
a runnable Python file called MyBot.py or a runnable JAR called MyBot.jar.

To do this, you can use the scripts as follows:

    cd sample_bots/python
    ./build
    # upload ants-python.zip
    cd ../..

    cd sample_bots/java
    gradle zip
    # upload build/distributions/ants-java.zip
    cd ../..
