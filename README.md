# Panic Paste

A high-performance arcade typing/editing game built for the DSA course at the Faculty of Computer Engineering, Ain Shams University(CSE243). This project leverages C++ **Treaps** (Randomized Search Trees) for core data handling, integrated with a modern Python **Tkinter** UI.

## Team Members
1.  Omar Ayman
2.  Mohamed Osama
3.  Omar Akram
4.  Hajar Mohammed
5.  Ahmed Emara

---

## Project Overview

### The Game Perspective
"Panic Paste" is an arcade-style text editor racer. You are given a passage of text (or code) and must replicate it exactly. But it's not just typing—you have "hooks" to cut, copy, paste, delete, and insert text. The faster and more accurately you edit, the higher your score. The game features multiple difficulties and a time-trial mode.

### The Technical Perspective
This project demonstrates the power of **Treaps** (Tree + Heap) for optimizing different operations where standard arrays or lists might fall short:
1.  **Implicit Treap (Text Buffer)**: We use an implicit treap to manage the text editor's state server-side. This allows for expected $O(\log N)$ cost for insertions, deletions, and substring operations, making it efficient for handling rapid text manipulation.
2.  **Leaderboard Treap**: A standard keyed treap is used to maintain the leaderboard. It allows for efficient $O(\log N)$ insertion of new player scores and fast retrieval of the top rankings.

---

## Project Structure

### Python UI (`UI/`)
The frontend is built with Python using `tkinter` and `pyglet` for custom fonts.
-   `main.py`: The entry point of the application.
-   `ui.py`: The heart of the frontend. Handles the styling (Neon/Arcade theme), window management, and all widget interactions.
-   `engine.py`: Manages the game state, game loop, active passage text, and difficulty logic.
-   `leaderboard.py`: Python interface that bridges the UI with the C++ leaderboard backend.

### C++ Backend (`treaps/`)
The heavy data lifting is done in C++ and exposed to Python as compiled modules (`.pyd`) using **pybind11**.

#### Implicit Treap (`treaps/implicit_treap/`)
-   `implicitTreap.cpp`: Implements the `ImplicitTreap` class. This handles the logic for the text buffer (split, merge, insert, erase) without using explicit keys, relying on array-like indexing.

#### Leaderboard Treap (`treaps/leaderboard_treap/`)
-   `leaderboard_treap.cpp`: The main wrapper file that exposes the C++ functionality to Python.
-   `Leaderboard_time.cpp`: Implements the `LeaderboardTime` class which manages time-based scores.
-   `treap.h`: The header file defining the core templated `Treap` data structure node and basic BST/Heap operations.
-   `Leaderboard_playerID.h`: Defines the player attributes and comparison logic for the leaderboard.

---

## Dependencies & Installation

### Prerequisites
1.  **Python 3.10+**: Ensure Python is installed and added to your system PATH.
2.  **C++ Compiler**: MSVC (Visual Studio) is recommended for Windows, or MinGW.
3.  **CMake**: Required for building the C++ projects.
4.  **pybind11**: Required for the binding of the C++ code to Python.

### Python Dependencies
Install the required Python package (Tkinter is usually included with Python):
```bash
pip install pyglet
```

### Detailed Installation
1.  **Clone the Repository**:
    ```bash
    git clone <repo_url>
    cd <repo_directory>
    ```

2.  **Build the C++ Modules**:
    The project relies on `.pyd` (Python Extension) files generated from the C++ code.
    -   Navigate to `treaps/` (or use the provided Visual Studio solution `generic_treap.sln` if available).
    -   If using CMake:
        ```bash
        mkdir build
        cd build
        cmake ..
        cmake --build . --config Release
        ```

3.  **Move the .pyd Files**:
    **CRITICAL STEP**: After building, you will find `.pyd` files (e.g., `implicit_treap.cp313-win_amd64.pyd` and `leaderboard_treap...`).
    -   You **MUST** move these files into the `UI/` folder.
    -   The Python scripts (`ui.py`, etc.) expect these modules to be importable directly from their directory.

4.  **Run the Game**:
    Navigate to the `UI` directory and run `main.py`:
    ```bash
    cd UI
    python main.py
    ```
