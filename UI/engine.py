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
        "May the Force be with you.",
        "There's no place like home.",
        "I'm going to make him an offer he can't refuse.",
    ],
    "Medium": [
        "Life moves pretty fast. If you don't stop and look around once in a while, you could miss it.",
        "Mama always said life was like a box of chocolates. You never know what you're gonna get.",
        "The first rule of Fight Club is: you do not talk about Fight Club.",
    ],
    "Hard": [
        "I've seen things you people wouldn't believe. Attack ships on fire off the shoulder of Orion. I watched C-beams glitter in the dark near the Tannhäuser Gate. All those moments will be lost in time, like tears in rain. Time to die.",
        "The path of the righteous man is beset on all sides by the inequities of the selfish and the tyranny of evil men. Blessed is he who, in the name of charity and good will, shepherds the weak through the valley of the darkness.",
        "It's like in the great stories, Mr. Frodo. The ones that really mattered. Full of darkness and danger they were. And sometimes you didn't want to know the end, because how could the end be happy? How could the world go back to the way it was when so much bad had happened?",
    ],
    "Time-Trial": [
        "Let me tell you something you already know. The world ain't all sunshine and rainbows. It's a very mean and nasty place and I don't care how tough you are it will beat you to your knees and keep you there permanently if you let it. You, me, or nobody is gonna hit as hard as life. But it ain't about how hard you hit. It's about how hard you can get hit and keep moving forward.",
        "I don't have to tell you things are bad. Everybody knows things are bad. It's a depression. Everybody's out of work or scared of losing their job. The dollar buys a nickel's worth, banks are going bust, shopkeepers keep a gun under the counter. We know the air is unfit to breathe and our food is unfit to eat, and we sit watching our TVs while some local newscaster tells us that today we had fifteen homicides.",
        "We think too much and feel too little. More than machinery we need humanity. More than cleverness we need kindness and gentleness. Without these qualities, life will be violent and all will be lost. The aeroplane and the radio have brought us closer together. The very nature of these inventions cries out for the goodness in men, cries out for universal brotherhood.",
        "Good morning. In less than an hour, aircraft from here will join others from around the world. And you will be launching the largest aerial battle in the history of mankind. Mankind. That word should have new meaning for all of us today. We can't be consumed by our petty differences anymore. We will be united in our common interests.",
        "Son, we live in a world that has walls, and those walls have to be guarded by men with guns. Who's gonna do it? You? You, Lt. Weinberg? I have a greater responsibility than you could possibly fathom. You weep for Santiago, and you curse the Marines. You have that luxury. You have the luxury of not knowing what I know."
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
