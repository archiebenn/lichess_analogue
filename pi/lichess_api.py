import berserk
from dotenv import load_dotenv
import os

load_dotenv()

# set up the client with lichess api token from the .env file
session = berserk.TokenSession(os.getenv("lichess_token"))
client = berserk.Client(session=session)

# print your profile to confirm it works
# print(client.account.get())

# set up start game function that streams game state for a given game id 
# print to console (for now)
def start_game(game_id):
    for event in client.board.stream_game_state(game_id):
        # UPDATE THIS FOR LEDs
        print(event)

# 'searching' print 
print("Searching for incoming games...")

# setup loop to accept incoming events using the api
# starting a game on lichess triggers a gameStart event, and this is used to start the game loop
for event in client.board.stream_incoming_events():
    print(f"Received event: {event}")

    # check if game even is start (run start_game) or finish
    if event['type'] == 'gameStart':
        game_id = event['game']['id']
        start_game(game_id)

    # if game finishes print to cli and wait for next game 
    elif event['type'] == 'gameFinish':
        game = event['game']
        winner = game.get('winner', 'draw')
        opponent = game['opponent']['username']
        last_move = game['lastMove']
        print()
        print(f"Game over! {winner} wins!")
        print(f"Final move: {last_move}")
        print()
        print("Start another game to continue playing. Searching for incoming games...")



