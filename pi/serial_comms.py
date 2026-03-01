# serial_comms.py - for communications to the microcontroller/arduino from pi

###
# led_instruction function
###
def LED_instruction(origin, destination):
    """
    Define which LEDs to light up on the board and only during the opponent's turn.
    """
    # this will output as LEDs eventually
    print(f"(LED): {origin} -> {destination}")