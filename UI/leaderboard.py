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
        # initialization of the treaps for each difficulty/category
        self.leaderboard_easy = leaderboard_treap.LeaderboardTreap()
        self.leaderboard_medium = leaderboard_treap.LeaderboardTreap()
        self.leaderboard_hard = leaderboard_treap.LeaderboardTreap()
        self.leaderboard_time_trial = leaderboard_treap.LeaderboardTreap()
        
        # initialization of the list for the leaderboard
        self.add_entry(LeaderboardEntry("NOVA", "Hard",    112, 28.42))
        self.add_entry(LeaderboardEntry("BYTE", "Medium",   96, 31.10))
        self.add_entry(LeaderboardEntry("Z3RO", "Hard",    101, 33.55))
        self.add_entry(LeaderboardEntry("LUNA", "Easy",     72, 22.05))
        self.add_entry(LeaderboardEntry("KAI",  "Medium",   89, 34.90))

        self.add_entry(LeaderboardEntry("AXIS", "Hard",    118, 27.80))
        self.add_entry(LeaderboardEntry("ECHO", "Medium",   92, 32.45))
        self.add_entry(LeaderboardEntry("VOLT", "Hard",    109, 29.60))
        self.add_entry(LeaderboardEntry("MIRA", "Easy",     68, 23.10))
        self.add_entry(LeaderboardEntry("RYU",  "Medium",   85, 36.20))

        self.add_entry(LeaderboardEntry("CYRA", "Hard",    121, 26.95))
        self.add_entry(LeaderboardEntry("NEON", "Medium",   99, 30.75))
        self.add_entry(LeaderboardEntry("ORION","Hard",    114, 28.90))
        self.add_entry(LeaderboardEntry("SAGE", "Easy",     74, 21.80))
        self.add_entry(LeaderboardEntry("PIXEL","Medium",   91, 33.40))

        self.add_entry(LeaderboardEntry("QUARK","Hard",    125, 26.10))
        self.add_entry(LeaderboardEntry("IRIS", "Medium",   88, 35.10))
        self.add_entry(LeaderboardEntry("NEXUS","Hard",    117, 27.65))
        self.add_entry(LeaderboardEntry("ARIA", "Easy",     70, 22.90))
        self.add_entry(LeaderboardEntry("FLUX", "Medium",   95, 31.85))

        self.add_entry(LeaderboardEntry("OMEGA","Hard",    130, 25.40))
        self.add_entry(LeaderboardEntry("EMBER","Medium",   90, 34.25))
        self.add_entry(LeaderboardEntry("ATLAS","Hard",    122, 26.70))
        self.add_entry(LeaderboardEntry("ELIO", "Easy",     66, 23.75))
        self.add_entry(LeaderboardEntry("TRACE","Medium",   97, 30.95))

        self.add_entry(LeaderboardEntry("PULSE","Hard",    115, 28.30))
        self.add_entry(LeaderboardEntry("LYNX", "Medium",   93, 32.80))
        self.add_entry(LeaderboardEntry("ROOK", "Hard",    108, 29.95))
        self.add_entry(LeaderboardEntry("NIA",  "Easy",     69, 22.60))
        self.add_entry(LeaderboardEntry("SPARK","Medium",   87, 35.60))

        self.add_entry(LeaderboardEntry("TITAN","Hard",    128, 25.85))
        self.add_entry(LeaderboardEntry("KILO", "Medium",   94, 32.10))
        self.add_entry(LeaderboardEntry("ZEN",  "Hard",    110, 29.20))
        self.add_entry(LeaderboardEntry("IVY",  "Easy",     73, 21.95))
        self.add_entry(LeaderboardEntry("CORE", "Medium",   98, 30.40))

        self.add_entry(LeaderboardEntry("RIFT", "Hard",    119, 27.25))
        self.add_entry(LeaderboardEntry("BLAZE","Medium",   91, 33.90))
        self.add_entry(LeaderboardEntry("NODE", "Hard",    113, 28.75))
        self.add_entry(LeaderboardEntry("UMA",  "Easy",     67, 23.30))
        self.add_entry(LeaderboardEntry("SYNC", "Medium",   86, 36.00))

        self.add_entry(LeaderboardEntry("FLASH", "Time-Trial", 140, 30.00))
        self.add_entry(LeaderboardEntry("SONIC", "Time-Trial", 135, 30.00))
        self.add_entry(LeaderboardEntry("TURBO", "Time-Trial", 128, 30.00))
        self.add_entry(LeaderboardEntry("BLUR",  "Time-Trial", 120, 30.00))
        self.add_entry(LeaderboardEntry("DASH",  "Time-Trial", 115, 30.00))


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
        match difficulty:
            case "Easy":
                top10 = self.leaderboard_easy.getTop10()
            case "Medium":
                top10 = self.leaderboard_medium.getTop10()
            case "Hard":
                top10 = self.leaderboard_hard.getTop10()
            case "Time-Trial":
                top10 = self.leaderboard_time_trial.getTop10()
            case _:
                raise ValueError(f"Invalid difficulty: {difficulty}")
        list = []
        for entry in top10:
            list.append((entry.playerID, entry.wpm, entry.time, difficulty))
            
        return list
            

    # -------------------------------------------------------------------------
    # Legacy / Helper Methods (Internal Logic)
    # -------------------------------------------------------------------------

    def add_entry(self, entry: LeaderboardEntry) -> None:
        """
        Internal: Add a new entry to the leaderboard.
        If an entry exists for the same player and difficulty, keep the best one.
        """
        # # separate entries into "same player+diff" vs "others"
        # existing_index = -1
        # for i, e in enumerate(self._entries):
        #     if e.player_name == entry.player_name and e.difficulty == entry.difficulty:
        #         existing_index = i
        #         break
        
        # if existing_index != -1:
        #     existing = self._entries[existing_index]
        #     # Check if new entry is better
        #     is_better_wpm = entry.wpm > existing.wpm
        #     # If wpm is equal, we can't judge time easily if new entry time is 0.0
        #     # We assume higher WPM is strictly better for this simplified interface.
            
        #     if is_better_wpm:
        #         self._entries[existing_index] = entry
        # else:
        #     # New record
        #     self._entries.append(entry)

        # self._sort_and_trim()
        match entry.difficulty:
            case "Easy":
                self.leaderboard_easy.registerTime(entry.player_name, entry.wpm, entry.time_seconds)
            case "Medium":
                self.leaderboard_medium.registerTime(entry.player_name, entry.wpm, entry.time_seconds)
            case "Hard":
                self.leaderboard_hard.registerTime(entry.player_name, entry.wpm, entry.time_seconds)
            case "Time-Trial":
                self.leaderboard_time_trial.registerTime(entry.player_name, entry.wpm, entry.time_seconds)
            case _:
                raise ValueError(f"Invalid difficulty: {entry.difficulty}")
        

    # def _sort_and_trim(self) -> None:
    #     """
    #     Internal: Sort by WPM (descending).
    #     """
    #     self._entries.sort(key=lambda e: -e.wpm)
    #     self._entries = self._entries[:200]