from dataclasses import dataclass, field
import time
from typing import List, Dict, Tuple, Optional
import leaderboard_treap

@dataclass(frozen=True)
class LeaderboardEntry:
    """
    Strict data structure representing a single leaderboard entry.
    Immutable to prevent accidental side effects.
    """
    player_name: str
    difficulty: str
    wpm: int
    time_seconds: float
    timestamp: float = field(default_factory=time.time)

class LeaderboardService:
    """
    Service responsible for all leaderboard data operations (Read/Write/Sort).
    Decoupled from UI and Game Logic.
    This module is designed to be easily replaced by an API client in the future.
    """

    def __init__(self) -> None:
        """Initialize with dummy data."""
        self._entries: List[LeaderboardEntry] = [
            LeaderboardEntry("NOVA", "Hard",    55, 35.42),
            LeaderboardEntry("BYTE", "Medium",   42, 42.10),
            LeaderboardEntry("Z3RO", "Hard",    68, 28.55),
            LeaderboardEntry("LUNA", "Easy",     31, 52.05),
            LeaderboardEntry("KAI",  "Medium",   48, 38.90),

            LeaderboardEntry("AXIS", "Hard",    72, 25.80),
            LeaderboardEntry("ECHO", "Medium",   39, 45.45),
            LeaderboardEntry("VOLT", "Hard",    58, 32.60),
            LeaderboardEntry("MIRA", "Easy",     25, 63.10),
            LeaderboardEntry("RYU",  "Medium",   44, 40.20),

            LeaderboardEntry("CYRA", "Hard",    82, 21.95),
            LeaderboardEntry("NEON", "Medium",   51, 34.75),
            LeaderboardEntry("ORION","Hard",    63, 30.90),
            LeaderboardEntry("SAGE", "Easy",     29, 55.80),
            LeaderboardEntry("PIXEL","Medium",   47, 39.40),

            LeaderboardEntry("QUARK","Hard",    88, 19.10),
            LeaderboardEntry("IRIS", "Medium",   36, 48.10),
            LeaderboardEntry("NEXUS","Hard",    65, 29.65),
            LeaderboardEntry("ARIA", "Easy",     22, 68.90),
            LeaderboardEntry("FLUX", "Medium",   53, 33.85),

            LeaderboardEntry("OMEGA","Hard",    95, 17.40),
            LeaderboardEntry("EMBER","Medium",   33, 51.25),
            LeaderboardEntry("ATLAS","Hard",    70, 26.70),
            LeaderboardEntry("ELIO", "Easy",     18, 75.75),
            LeaderboardEntry("TRACE","Medium",   50, 35.95),

            LeaderboardEntry("PULSE","Hard",    62, 31.30),
            LeaderboardEntry("LYNX", "Medium",   41, 43.80),
            LeaderboardEntry("ROOK", "Hard",    56, 33.95),
            LeaderboardEntry("NIA",  "Easy",     27, 60.60),
            LeaderboardEntry("SPARK","Medium",   45, 41.60),

            LeaderboardEntry("TITAN","Hard",    78, 23.85),
            LeaderboardEntry("KILO", "Medium",   49, 36.10),
            LeaderboardEntry("ZEN",  "Hard",    59, 31.20),
            LeaderboardEntry("IVY",  "Easy",     32, 54.95),
            LeaderboardEntry("CORE", "Medium",   52, 34.40),

            LeaderboardEntry("RIFT", "Hard",    67, 28.25),
            LeaderboardEntry("BLAZE","Medium",   40, 44.90),
            LeaderboardEntry("NODE", "Hard",    61, 30.75),
            LeaderboardEntry("UMA",  "Easy",     24, 65.30),
            LeaderboardEntry("SYNC", "Medium",   43, 42.00),

            # Time-Trial Dummy Data
            LeaderboardEntry("FLASH", "Time-Trial", 90, 30.00),
            LeaderboardEntry("SONIC", "Time-Trial", 85, 30.00),
            LeaderboardEntry("TURBO", "Time-Trial", 75, 30.00),
            LeaderboardEntry("BLUR",  "Time-Trial", 65, 30.00),
            LeaderboardEntry("DASH",  "Time-Trial", 60, 30.00),
        ]


    def insert_player(self, username: str, difficulty: str, score: int, time_seconds: float = 0.0) -> None:
        """
        Inserts a player entry into the leaderboard.
        
        Interface designed for C++ backend integration.
        
        Args:
            username (str): Player's display name.
            difficulty (str): Game difficulty level.
            score (int): Score (WPM).
            time_seconds (float, optional): Elapsed time. Defaults to 0.0 for C++ compat.
            
        Note:
            Function overloaded to accept explicit score. 
        """
        entry = LeaderboardEntry(
            player_name=username,
            difficulty=difficulty,
            wpm=score,
            time_seconds=time_seconds
        )
        self.add_entry(entry)

    def get_top_10(self, difficulty: Optional[str] = None) -> List[Tuple[str, int, float, str]]:
        """
        Retrieves the top 10 players.
        
        Args:
            difficulty (Optional[str]): If provided, filters by difficulty. 
                                        If None, returns global top 10.
                                        
        Returns:
             List of (Username, Score, Time, Difficulty) tuples.
        """
        if difficulty:
            filtered = [e for e in self._entries if e.difficulty == difficulty]
        else:
            filtered = self._entries
            
        # Sort by WPM descending
        sorted_rows = sorted(filtered, key=lambda e: -e.wpm)
        top_10 = sorted_rows[:10]
        
        # Return simple tuples for C++ interface compatibility
        return [(e.player_name, e.wpm, e.time_seconds, e.difficulty) for e in top_10]

    # -------------------------------------------------------------------------
    # Legacy / Helper Methods (Internal Logic)
    # -------------------------------------------------------------------------

    def add_entry(self, entry: LeaderboardEntry) -> None:
        """
        Internal: Add a new entry to the leaderboard.
        If an entry exists for the same player and difficulty, keep the best one.
        """
        # separate entries into "same player+diff" vs "others"
        existing_index = -1
        for i, e in enumerate(self._entries):
            if e.player_name == entry.player_name and e.difficulty == entry.difficulty:
                existing_index = i
                break
        
        if existing_index != -1:
            existing = self._entries[existing_index]
            # Check if new entry is better
            is_better_wpm = entry.wpm > existing.wpm
            # If wpm is equal, we can't judge time easily if new entry time is 0.0
            # We assume higher WPM is strictly better for this simplified interface.
            
            if is_better_wpm:
                self._entries[existing_index] = entry
        else:
            # New record
            self._entries.append(entry)

        self._sort_and_trim()

    def _sort_and_trim(self) -> None:
        """
        Internal: Sort by WPM (descending).
        """
        self._entries.sort(key=lambda e: -e.wpm)
        self._entries = self._entries[:200]
