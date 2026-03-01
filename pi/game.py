# in game functions


###
# to_from function
###

# take the move string, eg e2e4, and return the origin and destination square names (will change to coordinates later)
def to_from(move_string):
    """
    returns the coordinates/squares of the move that was just made based on game state
    """

    # split move string into origin...
    origin = move_string[:2]

    # ... and destination squares (2:4 for promotion edge cases)
    destination = move_string[2:4]

    #catch promotions which have an extra character at the end eg e7e8q:
    promotion = move_string[4:] if len(move_string) > 4 else None

    return origin, destination, promotion



###
# whose_turn function - returns which player's turn it is based on game state
###

def is_my_turn(moves, my_colour):
    """
    BOOL True/False to determine if it is the opponent's turn or not based on move count and colour of each player. This is for the NEXT move.
    e.g:
    move_count = 1  -> white just moved ->  black moves next
    move_count = 2  -> black just moved ->  white moves next
    """

    # set current move count
    move_count = len(moves.split()) if moves else 0

    # white always moves first, so it is white's turn next if move_count divisible by 2
    # BOOL True/False
    whites_turn_next = move_count %2 == 0

    if my_colour == 'white':
        # if I am white and white's turn next = true, is_my_turn = true
        return whites_turn_next
    
    else:
        # if I am black and white's turn next = true, is_my_turn = false
        return not whites_turn_next
    

###
# start_game function
###
# set up start game function that streams game state for a given game id and client
# any move made in the game will trigger an update to the game state, which is streamed in real time and can be used to update the board/cli/LEDs (eventually)
def start_game(client, game_id, my_colour):
    """
    streams game state for a given game id and updates LEDs accordingly
    """

    for event in client.board.stream_game_state(game_id):

        # UPDATE THIS BLOCK FOR LEDs
        if event['type'] == 'gameState':

            # print only latest move from streamed game state:
            moves = event['moves']
            if moves:

                # latest move string
                latest_move = moves.split()[-1]
                
                # set origin/destination:
                origin, destination, promotion = to_from(latest_move)

                # my turn
                if is_my_turn(moves, my_colour):
                    
                    # print previous move (print opponent's move to CLI during my move)
                    print(f"OPPONENT'S MOVE: {origin} -> {destination}")
                
                else:
                    # print my previous move to CLI during opponent's move
                    print(f"YOU MOVE: {origin} -> {destination}")


###
# LED CONTROL LOGIC
###