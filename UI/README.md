
# Panic Paste UI

A neon-themed arcade typing racer built with **Tkinter** and **Python**.

## Overview

Panic Paste is a fast-paced typing game where players race against the clock to accurately type passages. The UI is a modular, page-based application with retro arcade aesthetics featuring neon colors and pixel art fonts.

## Architecture

### Core Components

**`engine.py`** - Game Logic
- `GameEngine`: Manages game state, timing, WPM calculation, and passage selection
- `GameResult`: Strict dataclass for passing run results
- 3 difficulty levels with unique passages

**`leaderboard.py`** - Leaderboard Service
- `LeaderboardEntry`: Immutable entry structure
- `LeaderboardService`: Handles ranking, deduplication, and persistence
- Sorts by WPM (descending), then time (ascending)

**`ui.py`** - User Interface
- `PanicPasteApp`: Main app root and page manager
- `NeonPage`: Base class for all pages with consistent styling
- 5 Page Views:
    - `HomePage`: Start screen with flashing "PRESS ANY KEY" prompt
    - `SetupPage`: Player name + difficulty selection
    - `GamePage`: Main typing input with live character highlighting
    - `ResultsPage`: Post-game stats display
    - `LeaderboardPage`: Top scores filtered by difficulty

**`main.py`** - Entry Point

### Styling

**`Theme` class** provides:
- Neon color palette (Cyan, Pink, Green, Yellow)
- Consistent font sizing via `Theme.font()`
- TTK style configuration for buttons and inputs

## Features

- **Live Highlighting**: Correct characters in white, errors in red
- **Real-time Timer**: Updates every 33ms during gameplay
- **Keyboard Shortcuts**: Arrow keys for difficulty selection, Enter to submit
- **Copy/Paste Hooks**: Functions ready for CLI-style command binding
- **Leaderboard**: Tracks best scores per player per difficulty
- **Responsive Layout**: Adapts to window resizing (min 900x560)

## Usage

```bash
python main.py
```

## Dependencies

- `tkinter` (built-in)
- `pyglet` (for custom font loading)
- Python 3.7+
