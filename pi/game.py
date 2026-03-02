# in game functions

###
# IMPORTS
###
import chess
from serial_comms import LED_instruction


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

    board = chess.Board()

    # set statuses indicating if a game has already finished to avoid attempting to process moves during a finished game
    finished_status = {'resign', 'mate', 'timeout', 'draw', 'stalemate', 'aborted', 'outoftime'}


    for event in client.board.stream_game_state(game_id):

        # UPDATE THIS BLOCK FOR LEDs
        if event['type'] == 'gameState':

            # check if game has finished first before attemtping to process moves
            if event['status'] in finished_status:
                print(f"Game {game_id} has finished: {event['status']}")

                # return to main.py to wait for next game
                return

            # print only latest move from streamed game state:
            moves = event['moves']
            if moves:

                # latest move string
                latest_move = moves.split()[-1]

                # set origin/destination:
                origin, destination, promotion = to_from(latest_move)

                # rebuild board from full move list to ensure correct state
                board = chess.Board()

                try:
                    for uci in moves.split():
                        board.push_uci(uci)

                # don't crash on malformed/unknown moves and skip until next update
                # if there is an error which is corrected it will print a warning but then update chess.Board() on next move anyway
                except chess.IllegalMoveError as e:

                    print(f"Warning: illegal move in moves list, skipping: {e}")
                    continue

                # print CLI chess board
                print()
                print(board)

                # my turn
                if is_my_turn(moves, my_colour):

                    # light up LEDs to show previous (opponent's) move
                    LED_instruction(origin, destination)
                
                else:
                    # stand in - will be removed too
                    print(f"(Your move) {origin} -> {destination}")
                    


###
# LED CONTROL LOGIC
###