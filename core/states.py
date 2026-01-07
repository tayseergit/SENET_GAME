'''
class state
atribute:

numbers of black
numbers of white
`Player` enum - WHITE, BLACK, EMPTY (File)
`Action` class - represents a move (from_position, roll)

functions :
- `copy()` - creates deep copy of state
- `get_piece_positions(player)` - returns list of positions for player's pieces
- `is_terminal()` - checks if game is over (GOAL-TEST)
- `get_winner()` - returns winning player if game over
- `__eq__()` - check if two states are equal
- `__hash__()` - make state hashable
- `create_initial_state()` - creates starting board (s₀)


'''