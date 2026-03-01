import berserk
from dotenv import load_dotenv
import os

load_dotenv()

# set up the client with lichess api token from the .env file
session = berserk.TokenSession(os.getenv("lichess_token"))
client = berserk.Client(session=session)

# print your profile to confirm it works
print(client.account.get())

# set up start game function that streams game state for a given game id 
# print to console (for now)
def start_game(game_id):
    for event in client.board.stream_game_state(game_id):
        
        # UPDATE THIS FOR LEDs
        print(event)


# setup loop to accept incoming events using the api
# starting a game on lichess triggers a gameStart event, and this is used to start the game loop
for event in client.board.stream_incoming_events():
    if event['type'] == 'gameStart':
        game_id = event['game']['id']
        start_game(game_id)