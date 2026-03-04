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
# board state function - returns the current board state based on the move list
###
def set_board_state(moves):
    """
    Rebuild board state from full move list and returns None if illegal move
    """
    # rebuild board from full move list to ensure correct state
    board = chess.Board()

    try:
        # move is valid, push to board state
        for uci in moves.split():
            board.push_uci(uci)
        return board

    # illegal move. don't crash on malformed/unknown moves and skip until next update
    except chess.IllegalMoveError as e:
        print(f"Warning: illegal move in moves list, skipping: {e}")
        return None



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
    

def handle_turn(moves, my_colour, origin, destination, white_time, black_time):
    """
    Handles whose turn it is, returns time remaining for current player for timer function, and will eventually handle LED updates
    """
    # my turn - light LEDs and set timer counting down
    if is_my_turn(moves, my_colour):

        # light up LEDs to show previous (opponent's) move
        LED_instruction(origin, destination)

        # set variables to pass to timer() for my turn time remaining
        time_ms = white_time if my_colour == 'white' else black_time
        player_label = "Your time remaining"

                
    else:
        # show previous move
        print(f"(Your move) {origin} -> {destination}")

        # set variables to pass to timer() for opponent's time remaining
        time_ms = white_time if my_colour != 'white' else black_time
        player_label = "Opponent time remaining"

    return time_ms, player_label
    


###
# timer function - returns players' remaining times at 1s intervals
###
def timer(time_ms, player_label, stop_event):
    """
    Converts ms to seconds and formats for display
    """
    stop_event.clear()

    # convert timedelta to secondds
    if hasattr(time_ms, 'total_seconds'):
        remaining_secs = time_ms.total_seconds()
    else:
        remaining_secs = time_ms / 1000

    # calculate only when time on clock and set as integers
    while not stop_event.is_set() and remaining_secs > 0:
        minutes = int(remaining_secs)//60
        seconds = int(remaining_secs) % 60

        # output remaining player time to CLI
        print(f"\r{player_label}: {minutes:02d}:{seconds:02d}", end="", flush=True)

        # print every 0.1s interval
        time.sleep(1)
        remaining_secs -= 1
    print()



###
# start stop timer function - controls starting and stopping of timer thread based on game state and turn
### 
def start_stop_timer(clock_thread, stop_clock, white_time, black_time, time_ms, player_label):

    # only start timer on timed games where times != None
    if white_time and black_time:

        # stop any  previous countdown if running
        if clock_thread and clock_thread.is_alive():
            stop_clock.set()
            clock_thread.join()

        # create new stop event for this timer
        stop_clock = threading.Event()

        # run timer() function in separate thread to avoid blocking main game loop
        clock_thread = threading.Thread(target=timer, args=(time_ms, player_label, stop_clock), daemon=True)
        clock_thread.start()
                
    else:

        # unlimited time games, stop any running timer if it exists
        if clock_thread and clock_thread.is_alive():
            stop_clock.set()
            clock_thread.join()

    return clock_thread, stop_clock



###
# start_game function
###
# set up start game function that streams game state for a given game id and client
# any move made in the game will trigger an update to the game state, which is streamed in real time and can be used to update the board/cli/LEDs (eventually)
def start_game(client, game_id, my_colour):
    """
    Streams game state for a given game id and updates LEDs/CLI accordingly
    """

    board = chess.Board()
    
    # timers 
    _clock_thread = None
    _stop_clock = None

    # set statuses indicating if a game has already finished to avoid attempting to process moves during a finished game
    finished_status = {'resign', 'mate', 'timeout', 'draw', 'stalemate', 'aborted', 'outoftime'}

    # this is the main game loop which streams each move in real time and updates LEDs accordingly
    # continues until game finishes, then returns to main.py for next game
    for event in client.board.stream_game_state(game_id):

        if event['type'] == 'gameState':

            # check if game has finished first before attemtping to process moves
            if event['status'] in finished_status:

                # stop any running timer before returning to main.py (stops timer running into next game)
                if _clock_thread and _clock_thread.is_alive():
                    _stop_clock.set()
                    _clock_thread.join()

                # return to main.py to wait for next game
                return
            
            # PROCESS MOVE STUFF
            # print only latest move from streamed game state:
            moves = event['moves']

            if moves:

                # latest move string
                latest_move = moves.split()[-1]

                # set origin/destination:
                origin, destination, promotion = to_from(latest_move)

                # rebuild board from full move list to ensure correct state
                board = set_board_state(moves)

                # skip on error
                if board is None:
                    continue

                # print CLI chess board
                print()
                print(board)

                if board.is_check():
                    print("CHECK!")

                # fetch the times for each player. 'None' if untimed game
                white_time = event.get('wtime')
                black_time = event.get('btime')

                # HANDLE TURN, TIMERS AND LEDS
                time_ms, player_label = handle_turn(moves, my_colour, origin, destination, white_time, black_time)                

                # TIMER STUFF
                _clock_thread, _stop_clock = start_stop_timer(_clock_thread, _stop_clock, white_time, black_time, time_ms, player_label)


            
                    