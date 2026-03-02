# Lichess LED Board
Repo for code, set up, and building of an Lichess-linked and LED-activated physical chess board to play online or against a computer live with physical pieces.  

## Design approach (unfinished)  
The idea is to have a classic looking wooden board with discreet LEDs allowing the user to play against a chess computer (through Lichess or a local engine) or online with Lichess. This is the (rough) proposed setup:  
- Wooden chess set
- Raspberry pi zero 2 W with python scripts (for Lichess API game access) and to run the local engine
- Arduino connected to the rasbpi for controlling the LEDs 
- Printed circuit board with 64 soldered hall effect sensors and LEDs (one per square)
- LEDs will display the opponent's move uby lighting up origin and destination squares
- Hall effect sensors will detect when the user has moved a piece and this will be transmitted back to the game

The aim is to create as discreet a board as possible so that it can be played like normal with others without having a load of flashy LEDs or cables sticking out at all times. This is also our first time trying something like this with electronics so please provide any feedback or guidance if you can see any silly errors! Thanks


## Setup
### Pre-filled API token form:  
This is to allow access via Lichess' API token to your games  
https://lichess.org/account/oauth/token/create?scopes[]=challenge:write&scopes[]=puzzle:read&scopes[]=puzzle:write&scopes[]=board:play&description=Prefilled+token+example
