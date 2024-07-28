"""
This module holds the configuration for the Pokerlite program.
Author: Seán Young
"""

from datetime import datetime
import logging
from typing import Literal, TypedDict

#############################################
# Set the game configuration parameters here

# The file names of all player code files
ALL_PLAYER_FILES: list[str] = ["player1", "player2", "player3", "player4"]
# Two of the numbers 1, 2, 3, 4 corresponding to the 4 files in ALL_PLAYER_FILES
CURRENT_PLAYER_FILE_NUMBERS: list[int] = [1, 4]
# The name of the class to be defined in each player file 
PLAYER_CLASS = "PlayerCode"
# The game consists of this many betting rounds
NUMBER_ROUNDS: int = 1_000_000
# Each player gets a card with a number between 1 and this value
CARD_HIGH_NUMBER = 9
# Ante amount paid into the pot at the start of each betting round by each player
ANTE_BET: int = 10
# Three allowed values for the opening bet
OPEN_BET_OPTIONS: dict[str, int] = {
    "L": ANTE_BET * 1, # Open with the low amount
    "M": ANTE_BET * 2, # Open with the medium amount
    "H": ANTE_BET * 5, # Open with the high amount
}
# Factors by which an incoming bet is multiplied to give an amount to add to an incoming bet to see or raise a bet
SEE_BET_OPTIONS: dict[str, float] = {
    "S": 0, # See the bet => leave at 0 (and any other value is ignored anyway)
    "M": 0.5, # Medium raise 
    "H": 1.0, # High raise
}
# Number of raises allowed - simulator supports 1 raise maximum
MAX_RAISES: int = 1 
# True to carry the pot when a game is checked, false to give the pot back to the players
IS_CARRY_POT = True

#############################################

# Load the player files from the numbers entered above
current_player_files: list[str] = []
for i in CURRENT_PLAYER_FILE_NUMBERS:
    current_player_files.append(ALL_PLAYER_FILES[i-1])

# Define type for passing game configuration data
class GameConfig(TypedDict):
    PLAYER_FILES: list[str]
    PLAYER_CLASS: str
    NUMBER_ROUNDS: int
    CARD_HIGH_NUMBER: int
    ANTE_BET: int
    OPEN_BET_OPTIONS: dict[str, int]
    SEE_BET_OPTIONS: dict[str, float]
    MAX_RAISES: int
    IS_CARRY_POT: bool

GAME_CONFIG: GameConfig = {
    "PLAYER_FILES": current_player_files,
    "PLAYER_CLASS": PLAYER_CLASS,
    "NUMBER_ROUNDS": NUMBER_ROUNDS,
    "CARD_HIGH_NUMBER": CARD_HIGH_NUMBER,
    "ANTE_BET": ANTE_BET, 
    "OPEN_BET_OPTIONS": OPEN_BET_OPTIONS,
    "SEE_BET_OPTIONS": SEE_BET_OPTIONS,
    "MAX_RAISES": MAX_RAISES,
    "IS_CARRY_POT": IS_CARRY_POT
}

# Define various custom types
TypeForGameState = Literal["Game Start", "Card", "Ante", "Round Start", "Checked", "Win"]
TypeForBetType = Literal["Ante", "Check", "Open", "See", "Raise", "Fold"]
TypeForPlayState = Literal[ \
    "Dealer Opens", \
    "Dealer Sees after Non-Dealer Opens after Dealer Checks", \
    "Dealer Sees after Non-Dealer Raises after Dealer Opens", \
    "Non-Dealer Opens after Dealer Checks", \
    "Non-Dealer Sees after Dealer Opens", \
    "Non-Dealer Sees after Dealer Raises after Non-Dealer Opens after Dealer Checks", \
    "Bet after Raise", \
    "End Game", \
]


# List of card numbers and string values that will trigger actions
OpenBetValues = Literal["", "L", "M", "H"]
SeeBetValues = Literal["", "S", "M", "H"]
Strategy = TypedDict('Strategy', {
    "Dealer_Opens_Bets": dict[int, OpenBetValues],
    "Dealer_Sees_after_Non_Dealer_Opens_after_Dealer_Checks": dict[int, SeeBetValues],
    "Dealer_Sees_after_Non_Dealer_Raises_after_Dealer_Opens": dict[int, SeeBetValues],
    "Non_Dealer_Opens_after_Dealer_Checks": dict[int, OpenBetValues],
    "Non_Dealer_Sees_after_Dealer_Opens": dict[int, SeeBetValues],
    "Non_Dealer_Sees_after_Dealer_Raises_after_Non_Dealer_Opens_after_Dealer_Checks": dict[int, SeeBetValues]
}, total=True)

# Define type for a record of betting activity in a betting round
PlayerList = Literal["None", "player1", "player2", "player3", "player4"]
RoundRecord = TypedDict("RoundRecord", {
    "Round_Number": int,
    "Pot": int,
    "Bet_Type": TypeForBetType,
    "Player": PlayerList,
    "Bet": int,
}, total=True)
# Define type for a record of activity in a game
class GameRecord(TypedDict):
    Game_Id: str
    Round_Number: int
    Pot: int
    Description: TypeForGameState | TypeForBetType
    Player: PlayerList
    Value: int

# Initialize the game data list
game_records: list[GameRecord] = [{
    "Game_Id": "",
    "Round_Number": 0,
    "Pot": 0,
    "Description": "Game Start",
    "Player": "None",
    "Value": 0
}]

# Miscellaneous constants
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"

if __name__ == "__main__":
    from pokerlite import Game
    from utilities import print_records
    game_id: str = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    game = Game(game_id)
    game.play()
    if game.logger.getEffectiveLevel() == logging.DEBUG: 
        print_records(game.game_records)
    # Download game record file to a file in the downloads directory
    # download_game_records(game.game_records, 'downloads/game_records.csv')