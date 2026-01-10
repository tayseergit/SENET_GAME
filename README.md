# SENET Game

A modular implementation of the ancient Egyptian board game **Senet** using Python and Pygame.

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
│       └── expectiminimax.py # Turn execution with UI callback
├── presentation/
│   └── display_board.py    # Pygame UI
└── main.py                 # Entry point
```

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
   - Scans the board for current player’s pieces.
   - Validates moves based on roll and special square rules.
   - Returns list of moves: `[{from_idx: to_idx}, …]`.

3. **Apply Move** (`Result.result(state, (from, to), roll)`)
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

## Running the Game

```bash
python main.py
```

- Starts with **BLACK** to move.
- Press `SPACE` to execute turns automatically via the controller.
- The game ends when one player has no pieces left.

## Key Design Decisions

- **Separation of Concerns**: Core logic knows nothing about Pygame; UI only reads state and triggers controller.
- **Board as Strings**: Simplifies serialization and UI rendering; Player enum used for type safety.
- **Controller Pattern**: `Expectiminimax` can be swapped for AI or human input without changing UI.

## Extending

- Add AI by replacing `Expectiminimax.execute_turn` with a smarter selection.
- Save/load states by serializing `SenetState.board` and counters.
- Customize special square rules in `actions.py` and `results.py`.