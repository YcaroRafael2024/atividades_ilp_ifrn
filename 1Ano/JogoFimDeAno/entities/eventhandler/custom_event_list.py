from pygame import USEREVENT
from enum import IntEnum, auto

class CustomEventList(IntEnum):
    NEWLEVELWARNING = USEREVENT + 1
    NEWGENERATIONWARNING = auto()
    DISABLEWARNING = auto()
    PLAYERCOLLISION = auto()
    RANDOMGAMEEND = auto()
    RESETGAME = auto()
    ACHIEVEMENTUNLOCKED = auto()
    # auto for new custom events
