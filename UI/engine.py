import time
import random
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass

@dataclass
class GameResult:
    """
    Strict data structure for passing game results around.
    """
    player_name: str
    difficulty: str
    wpm: int
    time_seconds: float

class GameEngine:
    """
    Handles the game logic, state, and stat calculations.
    This module is designed to be easily replaced by a C++ extension in the future.
    """

    PASSAGES: Dict[str, List[str]] = {
        "Easy": [
            "Neon lights glow. You type fast.",
            "Panic Paste is pure arcade chaos.",
            "Keep calm and hit the keys.",
        ],
        "Medium": [
            "When the timer starts, stay focused and keep your rhythm steady.",
            "Arcade nights feel different when your fingers move like lightning.",
            "Speed matters, but accuracy is what keeps you on the board.",
        ],
        "Hard": [
            "Cake or pie? I can tell a lot about you by which one you pick. It may seem silly, but cake people and pie people are really different. I know which one I hope you are, but that's not for me to decide. So, what is it? Cake or pie?",
            "She didn't understand how changed worked. When she looked at today compared to yesterday, there was nothing that she could see that was different. Yet, when she looked at today compared to last year, she couldn't see how anything was ever the same.",
            "It was a weird concept. Why would I really need to generate a random paragraph? Could I actually learn something from doing so? All these questions were running through her head as she pressed the generate button. To her surprise, she found what she least expected to see.",
        ],
    }

    def __init__(self) -> None:
        self.player_name: str = ""
        self.difficulty: str = "Easy"
        self.target_text: str = ""
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.wpm: int = 0
        self.is_running: bool = False
        self.completed: bool = False

    def start_game(self, name: str, difficulty: str) -> None:
        self.player_name = name
        self.difficulty = difficulty
        self.target_text = random.choice(self.PASSAGES[difficulty])
        self.start_time = None
        self.end_time = None
        self.wpm = 0
        self.is_running = False
        self.completed = False

    def start_timer(self) -> None:
        if not self.is_running and not self.completed:
            self.is_running = True
            self.start_time = time.perf_counter()

    def stop_timer(self) -> None:
        self.is_running = False

    def get_elapsed_time(self) -> float:
        if self.start_time is None:
            return 0.0
        if self.end_time is not None:
            return self.end_time - self.start_time
        return time.perf_counter() - self.start_time

    @staticmethod
    def _normalize(s: str) -> str:
        s = s.replace("\r\n", "\n")
        return s.rstrip("\n")

    def submit_text(self, current_text: str) -> Tuple[bool, bool, List[bool]]:
        norm_target = self._normalize(self.target_text)
        norm_typed = self._normalize(current_text)

        char_correctness: List[bool] = []
        for i, char in enumerate(norm_typed):
            if i < len(norm_target) and char == norm_target[i]:
                char_correctness.append(True)
            else:
                char_correctness.append(False)

        if norm_typed == norm_target:
            if self.is_running:
                self._finish_game(norm_typed)
            return True, True, char_correctness
        
        return True, False, char_correctness

    def _finish_game(self, final_typed_text: str) -> None:
        self.stop_timer()
        self.end_time = time.perf_counter()
        
        if self.start_time:
            elapsed = self.end_time - self.start_time
            minutes = max(elapsed / 60.0, 1e-6)
            self.wpm = int(((len(final_typed_text) / 5.0) / minutes) + 0.5)
        else:
            self.wpm = 0
            
        self.completed = True

    def get_results(self) -> GameResult:
        """
        Get final results of the run strictly typed.
        """
        elapsed = self.get_elapsed_time()
        return GameResult(
            player_name=self.player_name,
            difficulty=self.difficulty,
            wpm=self.wpm,
            time_seconds=elapsed
        )
