 
SYMBOLS = {
   
    "WHITE": "W",
    "BLACK": "B",
 
    "EMPTY": ".",

     
    "REBIRTH": "R",      # Safe square (House of Rebirth)
    "HAPPINESS": "H",    # House of Happiness
    "THREE_TRUTHS": "T", # House of Three Truths
    "RA": "A",           # House of Ra / Atum
    "GOAL": "G",         # Final square
}
 
COLORS = {
    SYMBOLS["WHITE"]: (245, 245, 245),     # White piece
    SYMBOLS["BLACK"]: (30, 30, 30),        # Black piece
    SYMBOLS["EMPTY"]: (200, 200, 200),     # Empty cell

    SYMBOLS["REBIRTH"]: (0, 180, 0),       # Safe square
    SYMBOLS["HAPPINESS"]: (255, 215, 0),   # Gold
    SYMBOLS["THREE_TRUTHS"]: (0, 120, 255),
    SYMBOLS["RA"]: (255, 140, 0),
    SYMBOLS["GOAL"]: (128, 0, 128),
}
 
PLAYER_SYMBOLS = {
    SYMBOLS["WHITE"],
    SYMBOLS["BLACK"],
}

SPECIAL_SQUARES = {
    SYMBOLS["REBIRTH"],
    SYMBOLS["HAPPINESS"],
    SYMBOLS["THREE_TRUTHS"],
    SYMBOLS["RA"],
    SYMBOLS["GOAL"],
}

TERMINAL_SQUARES = {
    SYMBOLS["GOAL"],
}
