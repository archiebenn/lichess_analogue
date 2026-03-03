# in game functions

###
# IMPORTS
###
import chess
from serial_comms import LED_instruction
import threading
import time

###
# SETUP
###
# timer setup
_stop_clock = threading.Event()
_clock_thread = None

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
# timer function - returns players' remaining times at 0.1s intervals
###
def timer(time_ms, player_label):
    """
    converts ms to seconds and formats for display
    """
    _stop_clock.clear()

    # convert timedelta to seconds if needed
    if hasattr(time_ms, 'total_seconds'):
        remaining_secs = time_ms.total_seconds()
    else:
        remaining_secs = time_ms / 1000

    # calculate only when time on clock and set as integers
    while not _stop_clock.is_set() and remaining_secs > 0:
        minutes = int(remaining_secs)//60
        seconds = int(remaining_secs) % 60

        # output remaining player time to CLI
        print(f"\r{player_label}: {minutes:02d}:{seconds:02d}", end="", flush=True)

        # print every 0.1s interval
        time.sleep(0.1)
        remaining_secs -= 0.1
    print()



###
# start_game function
###
# set up start game function that streams game state for a given game id and client
# any move made in the game will trigger an update to the game state, which is streamed in real time and can be used to update the board/cli/LEDs (eventually)
def start_game(client, game_id, my_colour):
    """
    streams game state for a given game id and updates LEDs/CLI accordingly
    """

    board = chess.Board()
    
    # timers 
    _clock_thread = None
    _stop_clock = threading.Event()

    # set statuses indicating if a game has already finished to avoid attempting to process moves during a finished game
    finished_status = {'resign', 'mate', 'timeout', 'draw', 'stalemate', 'aborted', 'outoftime'}

    # this is the main game loop which streams each move in real time and updates LEDs accordingly
    # continues until game finishes, then returns to main.py for next game
    for event in client.board.stream_game_state(game_id):

        if event['type'] == 'gameState':

            # check if game has finished first before attemtping to process moves
            if event['status'] in finished_status:
                print(f"Game {game_id} has finished: {event['status']}")

                # return to main.py to wait for next game
                return
            
            # print only latest move from streamed game state:
            moves = event['moves']

            # TIMER STUFF
            # try and fetch time remaining for each player from event (in ms). get produces None if non-timed game so skips timer()
            white_time = event.get('wtime')
            black_time = event.get('btime') 

            # set time for countdown on first move
            if white_time and black_time:

                # stop any  previous countdown if running
                if _clock_thread and _clock_thread.is_alive():
                    _stop_clock.set()
                    _clock_thread.join()

                # figure out whose clock is ticking 
                time_ms = white_time if my_colour == 'white' else black_time
                player_label = "You" if is_my_turn(moves, my_colour) else "Opponent"

                # run timer() function
                _clock_thread = threading.Thread(target=timer, args=(time_ms, player_label), daemon=True)
                _clock_thread.start()


            # MOVE STUFF
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

                if board.is_check():
                    print("CHECK!")

                # my turn - light LEDs and set timer counting down
                if is_my_turn(moves, my_colour):

                    # light up LEDs to show previous (opponent's) move
                    LED_instruction(origin, destination)

                    # set variables to pass to timer() for my turn time remaining
                    time_ms = white_time if my_colour == 'white' else black_time
                    player_label = "You"

                
                else:
                    # show previous move
                    print(f"(Your move) {origin} -> {destination}")

                    # set variables to pass to timer() for opponent's time remaining
                    time_ms = white_time if my_colour != 'white' else black_time
                    player_label = "Opponent"

            
                    