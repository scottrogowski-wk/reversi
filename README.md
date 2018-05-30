Workiva Reversi
===============

A tutorial of App Intelligence - Lunch and learn series
--------------------------------------------------------

Presentation here: https://docs.google.com/presentation/d/1SGaX-NAN6LPYKlxGdZrsihnuYbRzCCqBuPCU2P3cyfA

<img src="screenshot.png" height="300px" />

### Getting our environment setup

#### In terminal A

    sudo pip2 install virtualenvwrapper
    git clone https://github.com/Workiva/sdlc_analytics.git
    mkvirtualenv -p python2.7 sa
    cd sdlc_analytics
    pip2 install -r requirements_dev.txt
    make compile

#### In terminal B

    git clone https://github.com/scottrogowski-wk/reversi.git
    mkvirtualenv -p python2.7 reversi
    pip2 install app_intelligence

#### Once done in your reversi terminal (terminal B)

    cd reversi
    ./reversi.py

### Steps to integrate App Intelligence

1. Write an analytic
2. Generate analytic code
3. Setup our reporter
4. Insert sender code
5. Run and see results in BigQuery

### Step 1: Write an analytic

This is a a single JSON file in either the user_analytics or the sdlc_analytics repo (In this case, sdlc_analytics). The easiest way to create a new analytic is to copy and modify an existing analytic. Once done, create a PR and ping us on "ANSERS Public" in Hipchat. For this tutorial, we will be using this analytic: https://github.com/Workiva/sdlc_analytics/blob/master/analytics/learning/learning_reversi-game-turn_v1.json

### Step 2: Generate analytic code

1. In sdlc_analytics terminal `make gen-py`
2. Open gen/python/analytics/learning_v1.py
3. Copy ReversiGameTurn to the top of reversi.py

### Step 3: Add AnalyticsReporter

    # At the top of reversi.py, add
    DEV = analytics.Hosts.SDLC_DEV
    reporter = analytics.AnalyticsReporter(DEV)

### Step 4: Insert sender code

    # Sending for the human

    reporter.send(ReversiGameTurn(
        turn_num=turn_num,
        x=x,
        y=y,
        swap_count=swap_count,

        game_hash=game_hash,
        player="human",
        ))

    # Sending for the computer

    reporter.send(ReversiGameTurn(
        turn_num=turn_num,
        x=x,
        y=y,
        swap_count=swap_count,

        game_hash=game_hash,
        player="computer",
        ))

### Step 5: Run and view results in BigQuery

    1. Play the game
    2. Copy your game_hash
    3. Go to this table https://bigquery.cloud.google.com/table/workiva-analytics:sdlc_analytics.learning_reversi_game_turn_v1
    4. Query:

    SELECT *
    FROM [workiva-analytics-dev:sdlc_analytics.learning_reversi_game_turn_v1]
    WHERE game_hash = "YOUR_HASH"`
