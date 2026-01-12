# SENET Game

A modular implementation of the ancient Egyptian board game **Senet** using Python and Pygame, featuring an intelligent AI opponent with search tree visualization.

## Features

- **Two Game Modes**: Human vs Human or Human vs AI
- **Intelligent AI**: Expectiminimax algorithm with adjustable difficulty (depth 1-5)
- **Search Tree Visualization**: View AI decision-making process in console
- **Interactive GUI**: Beautiful Pygame interface with move highlighting
- **Authentic Rules**: Special squares including House of Rebirth, House of Water, etc.

## Project Structure

```
SENET_GAME/
├── core/                    # Game logic (no UI)
│   ├── actions.py           # Move generation and validation
│   ├── states.py            # Game state representation
│   ├── results.py           # Applying moves to the state
│   ├── component/
│   │   ├── player.py       # Player enum (WHITE, BLACK, EMPTY)
│   │   └── main_house.py  # Special square constants
│   └── controller/
│       ├── probability.py   # Stick-throw probabilities
│       ├── heuristic.py    # Board evaluation function
│       └── expectiminimax.py # AI with path tracking
├── presentation/
│   └── display_board.py    # Pygame UI
└── main.py                 # Entry point
```

## Running the Game

```bash
python main.py
```

## Controls

- **SPACE**: Roll the dice
- **Click**: Select pieces to move (highlighted in green)
- **Mode Button**: Toggle Human vs Human / Human vs AI
- **+/- Buttons**: Adjust AI depth (1-5)
- **AI Move**: Get AI suggestion (Human vs Human mode)
- **Skip Turn**: Pass your turn
- **ESC**: Exit game

## Game Scenario & Flow

### Core Logic

- **Board**: 1D list of 30 cells using string symbols:
  - `"W"` = White piece
  - `"B"` = Black piece
  - `"."` = Empty
- **Players**: `Player` enum (`WHITE`, `BLACK`). Current player is stored as enum; board stores strings.
- **Special Squares**: Defined in `core/component/main_house.py` (e.g., House of Rebirth, House of Water).

### Turn Execution via Expectiminimax Controller

The `Expectiminimax` class in `core/controller/expectiminimax.py` orchestrates each turn:

1. **Roll Sticks** (`Probability.throw_sticks()`)
   - Returns a value 1–5 with weighted probabilities.

2. **Get Available Actions** (`Action.available_actions(state, roll)`)
   - Scans the board for current player's pieces.
   - Validates moves based on roll and special square rules.
   - Returns list of moves: `[{from_idx: to_idx}, …]`.

3. **Apply Move** (`Result.result(state, (from, to))`)
   - Executes the move on a copy of the state.
   - Handles special squares (rebirth, water, exit rules).
   - Switches current player.

4. **UI Callback**
   - After state update, calls the provided UI redraw function.
   - Keeps Pygame display in sync with game state.

### UI (Pygame)

- **`presentation/display_board.py`** renders the 3×10 board.
- **Controls**:
  - `SPACE`: Execute a full turn via `Expectiminimax.execute_turn`.
  - `ESC`: Exit.
- **Visuals**:
  - Pieces shown as circles with "W"/"B" labels.
  - Current player and piece counts displayed.
  - Winner announcement when terminal.

## Game Rules

- **Objective**: Move all pieces off the board first
- **Movement**: Roll dice (1-5) and move forward

### Special Squares

- **House of Rebirth (14)**: Safe square for sent-back pieces
- **House of Happiness (25)**: Gateway to final houses
- **House of Water (26)**: Sends pieces back to rebirth
- **House of Three Truths (27)**: Protected square
- **House of Re-Atoum (28)**: Protected square
- **House of Horus (29)**: Final square before exit

## AI Features

The AI uses **Expectiminimax algorithm** with:
- MAX/MIN/CHANCE nodes for probabilistic dice rolls
- Configurable depth (1-5) for difficulty
- Transposition table for efficiency
- Heuristic evaluation based on piece advancement and strategy

### Search Tree Path Visualization

When AI moves, it prints the decision path in console:

```
======================================================================
Selected Search Tree Path
======================================================================

┌─ [ACTION NODE]
│  Depth: 3
│  Player: WHITE
│  Move: 12→15
│  Roll: 3
└─

  ┌─ [CHANCE NODE]
  │  Depth: 2
  │  Player: BLACK
  │  Expected Value: 45.30
  │  Best Roll: 2
  │  Best Action: 13→15
  └─

    ┌─ [LEAF NODE]
    │  Depth: 0
    │  Evaluation: 50.00
    │  White Pieces: 6
    │  Black Pieces: 5
    └─
```

**Node Types:**
- **ACTION**: Player's move
- **CHANCE**: Dice roll evaluation
- **LEAF**: Maximum depth reached
- **TERMINAL**: Game-ending position

## Configuration

### Disable Path Printing

In `presentation/display_board.py`:

```python
self.controller = Expectiminimax(
    ui_callback=self._trigger_redraw, 
    max_depth=self.ai_depth,
    verbose=False  # Set to False
)
```

### Adjust AI Difficulty

Use +/- buttons in-game or modify:

```python
self.ai_depth = 3  # 1-5
```

## Key Design Decisions

- **Separation of Concerns**: Core logic independent of UI
- **Board as Strings**: Simplifies rendering ("W", "B", ".")
- **Controller Pattern**: Easy to swap AI strategies
- **Path Tracking**: Only selected path stored, not entire tree

## Extending

- Adjust AI difficulty by changing depth (1-5)
- Modify heuristic in `core/controller/heuristic.py`
- Add new AI strategies
- Save/load game states
- Customize special square rules

## Documentation

- **TREE_PATH_DOCUMENTATION.md**: Detailed path visualization guide
- **README_AR.md**: Arabic documentation
- **test_tree_path.py**: Test script for AI visualization

---

**Enjoy playing Senet!** 🎲
