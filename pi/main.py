# main.py - top level logic for analogue lichess board

###
# IMPORTS
###
from lichess_api import client
from game import start_game

###
# MAIN LOGIC
###

# searching 
print("Searching for incoming games...")

# setup permanent loop to accept incoming events using the api
# starting a game on lichess triggers a gameStart event, and this is used to start the game loop with start_game()
for event in client.board.stream_incoming_events():

    if event['type'] == 'gameStart':

        # set game id and my colour from event and start game loop with start_game function
        game_id = event['game']['id']
        my_colour = event['game']['color']

        print(f"Game starting: {game_id}")
        start_game(client, game_id, my_colour)

    # if game finishes print to cli and wait for next game 
    elif event['type'] == 'gameFinish':

        # get some info about the game from event to print to CLI:
        game = event['game']
        winner = game.get('winner', 'draw')
        opponent = game['opponent']['username']
        last_move = game['lastMove']
        status = game['status']['name']

        # print info about game outcome to CLI:
        print()
        if status == 'mate':
            print(f"Game over - {winner} wins by checkmate!")
        elif status == 'resign':
            print(f"Game over - {winner} wins by resignation!")
        elif status == 'stalemate':
            print("Game over - stalemate! It's a draw.")
        elif status == 'outoftime':
            print(f"Game over - {winner} wins on time!")
        else:
            print(f"Game over - {status}")
        print()

        # back to permanent loop...
        print("Start another game to continue playing. Searching for incoming games...")
