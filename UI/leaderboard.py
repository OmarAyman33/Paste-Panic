from dataclasses import dataclass, field
import time
from typing import List, Dict, Tuple, Optional

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
        LeaderboardEntry("NOVA", "Hard",    112, 28.42),
        LeaderboardEntry("BYTE", "Medium",   96, 31.10),
        LeaderboardEntry("Z3RO", "Hard",    101, 33.55),
        LeaderboardEntry("LUNA", "Easy",     72, 22.05),
        LeaderboardEntry("KAI",  "Medium",   89, 34.90),

        LeaderboardEntry("AXIS", "Hard",    118, 27.80),
        LeaderboardEntry("ECHO", "Medium",   92, 32.45),
        LeaderboardEntry("VOLT", "Hard",    109, 29.60),
        LeaderboardEntry("MIRA", "Easy",     68, 23.10),
        LeaderboardEntry("RYU",  "Medium",   85, 36.20),

        LeaderboardEntry("CYRA", "Hard",    121, 26.95),
        LeaderboardEntry("NEON", "Medium",   99, 30.75),
        LeaderboardEntry("ORION","Hard",    114, 28.90),
        LeaderboardEntry("SAGE", "Easy",     74, 21.80),
        LeaderboardEntry("PIXEL","Medium",   91, 33.40),

        LeaderboardEntry("QUARK","Hard",    125, 26.10),
        LeaderboardEntry("IRIS", "Medium",   88, 35.10),
        LeaderboardEntry("NEXUS","Hard",    117, 27.65),
        LeaderboardEntry("ARIA", "Easy",     70, 22.90),
        LeaderboardEntry("FLUX", "Medium",   95, 31.85),

        LeaderboardEntry("OMEGA","Hard",    130, 25.40),
        LeaderboardEntry("EMBER","Medium",   90, 34.25),
        LeaderboardEntry("ATLAS","Hard",    122, 26.70),
        LeaderboardEntry("ELIO", "Easy",     66, 23.75),
        LeaderboardEntry("TRACE","Medium",   97, 30.95),

        LeaderboardEntry("PULSE","Hard",    115, 28.30),
        LeaderboardEntry("LYNX", "Medium",   93, 32.80),
        LeaderboardEntry("ROOK", "Hard",    108, 29.95),
        LeaderboardEntry("NIA",  "Easy",     69, 22.60),
        LeaderboardEntry("SPARK","Medium",   87, 35.60),

        LeaderboardEntry("TITAN","Hard",    128, 25.85),
        LeaderboardEntry("KILO", "Medium",   94, 32.10),
        LeaderboardEntry("ZEN",  "Hard",    110, 29.20),
        LeaderboardEntry("IVY",  "Easy",     73, 21.95),
        LeaderboardEntry("CORE", "Medium",   98, 30.40),

        LeaderboardEntry("RIFT", "Hard",    119, 27.25),
        LeaderboardEntry("BLAZE","Medium",   91, 33.90),
        LeaderboardEntry("NODE", "Hard",    113, 28.75),
        LeaderboardEntry("UMA",  "Easy",     67, 23.30),
        LeaderboardEntry("SYNC", "Medium",   86, 36.00),

        # Time-Trial Dummy Data
        LeaderboardEntry("FLASH", "Time-Trial", 140, 30.00),
        LeaderboardEntry("SONIC", "Time-Trial", 135, 30.00),
        LeaderboardEntry("TURBO", "Time-Trial", 128, 30.00),
        LeaderboardEntry("BLUR",  "Time-Trial", 120, 30.00),
        LeaderboardEntry("DASH",  "Time-Trial", 115, 30.00),
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
