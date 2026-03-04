import queue
import threading

class MoveInputHandler:
    """
    Manages move inputs from CLI and (eventually) from hall sensors in physical board.
    Uses a queue so moves can be collected without blocking game loop.
    """
    def __init__(self):
        # queue that holds incoming moves - thread safe so CLI thread and game loop can access safely
        self.move_queue = queue.Queue()
        # reference to input thread toi check if it's still running
        self.input_thread = None
        # flag which can be set to signal input thread to stop
        self.stop_event = threading.Event()



    def start_cli_input(self):
        """
        If thread running and listening for input don't start another
        """
        if self.input_thread and self.input_thread.is_alive():
            return
        
        #clear stop flag - thread knows to keep running
        self.stop_event.clear()

        # create and start new thread running cli_input_loop
        # daemon=True means will die automatically if programme exits
        self.input_thread = threading.Thread(target=self.cli_input_loop, daemon=True)
        self.input_thread.start()



    def cli_input_loop(self):
        """
        keep listening for input ubntil stop_event is set
        """
        while not self.stop_event.is_set():
            try:
                # wait for user to type move and press enter
                move = input("Enter move (e.g e2e4 format): ").strip().lower()

                # only accept 4 or 5 (promotion case) character move inputs
                if move and len(move) in (4, 5):
                    # put move in queue for game to pick up
                    self.move_queue.put(move)

            except EOFError:
                # break if stdin closes unexpectedly and exit cleanly
                break



    def clear_queue(self):
        """
        Discard any stale moves from the queue (typed but not processed)
        """
        while not self.move_queue.empty():
            try:
                # prevents stale moves from previous turn being played automatically
                self.move_queue.get_nowait()

            except queue.Empty:
                break



    def hall_sensor_input(self):
        """
        Placeholder for hall effect sensor loop
        """
        pass



    def get_move(self, timeout=None):
        """
        Called by game_loop to retrieve next move from the queue.
        Blocks and waits until a move arrives or timeout expires
        returns None is timerout expires with no move
        """
        try:
            return self.move_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        """
        signal input thread to stop by setting the stop flag
        thread checks this flag at the top of its while loop
        """
        self.stop_event.set()

    