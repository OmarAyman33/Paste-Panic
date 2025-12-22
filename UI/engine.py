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
        "Time-Trial": [
            "This is a sprint against the clock. Every character counts. Do not look back, just keep typing as fast as you can before the time runs out! The pressure is on, the seconds are ticking, and your fingers must fly across the keyboard with absolute precision. There is no time for hesitation, no time for doubt. Only speed, rhythm, and the relentless pursuit of the perfect run.",
            "Thirty seconds on the clock. Focus perfectly. Speed is key, but accuracy is the lock. Can you top the leaderboard before the buzzer sounds? The neon lights of the arcade beat in time with your heart. Every keystroke brings you closer to glory or defeat. Stay calm, stay sharp, and let the flowstate take over your mind and body.",
            "Tick tock. The seconds are slipping away. Type with fury! Type with precision! The neon lights are watching your every move. A true master of the keyboard knows that hesitation is the enemy. Trust your muscle memory, let the words flow through you like digital water. The clock waits for no one, and neither should you.",
            "In the year 2084, digital typists compete in the neon-soaked arenas of the Cyber-Grid. Their fingers are blur, their minds sharper than quantum computers. You are one of them, a contender for the title of Grandmaster. The crowd roars as you step up to the terminal. The timer begins... now! Do not falter.",
            "The quick brown fox jumps over the lazy dog, but this is no simple typing test. This is an endurance run compressed into thirty seconds of adrenaline. Can you handle the heat? Can you keep your cool when the errors start to pile up? Breathe. Focus. Type. The leaderboard awaits a new champion."
        ]
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
        
        # Calculate correct characters for WPM to prevent mash-to-win
        norm_target = self._normalize(self.target_text)
        norm_typed = self._normalize(final_typed_text)
        
        correct_chars = 0
        for c1, c2 in zip(norm_typed, norm_target):
            if c1 == c2:
                correct_chars += 1

        if self.start_time:
            elapsed = self.end_time - self.start_time
            minutes = max(elapsed / 60.0, 1e-6)
            self.wpm = int(((correct_chars / 5.0) / minutes) + 0.5)
        else:
            self.wpm = 0
            
        self.completed = True

    def force_finish(self, current_text: str) -> None:
        """
        Manually trigger game end (e.g., for time trial timeout).
        """
        if not self.completed:
            self._finish_game(current_text)

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
