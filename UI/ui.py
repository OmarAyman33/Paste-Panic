import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Tuple, Optional, Any
import re
import pyglet 

from engine import GameEngine, GameResult
from leaderboard import LeaderboardService, LeaderboardEntry

FONT_FILE: str = "Public Pixel.ttf"
PIXEL_FONT_NAME: str = "Public Pixel"

pyglet.font.add_file(FONT_FILE)

class Theme:
    BG: str = "#07070B"
    PANEL: str = "#0E1020"
    PANEL2: str = "#0B0C14"

    NEON_CYAN: str = "#00F5FF"
    NEON_PINK: str = "#FF2D95"
    NEON_GREEN: str = "#22FF88"
    NEON_YELLOW: str = "#FFE66D"

    TEXT: str = "#E8ECFF"
    MUTED: str = "#A7B0D6"
    DANGER: str = "#FF3B3B"

    @staticmethod
    def font(size: int, weight: str = "normal") -> Tuple[str, int, str]:
        return (PIXEL_FONT_NAME, size, weight)

    @staticmethod
    def apply_ttk_style(root: tk.Tk) -> None:
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "TButton",
            padding=(14, 10),
            relief="flat",
            background=Theme.PANEL,
            foreground=Theme.TEXT,
            borderwidth=0,
            focusthickness=0,
            focuscolor=Theme.NEON_CYAN,
            font=Theme.font(11, "bold"),
        )
        style.map(
            "TButton",
            background=[("active", Theme.PANEL2)],
            foreground=[("active", Theme.NEON_CYAN)],
        )
        style.configure(
            "TEntry",
            padding=8,
            fieldbackground=Theme.PANEL2,
            foreground=Theme.TEXT,
            insertcolor=Theme.NEON_CYAN,
            borderwidth=0,
            font=Theme.font(11, "normal"),
        )
        style.configure(
            "TCombobox",
            padding=8,
            fieldbackground=Theme.PANEL2,
            foreground=Theme.TEXT,
            background=Theme.PANEL2,
            arrowcolor=Theme.NEON_CYAN,
            borderwidth=0,
            font=Theme.font(11, "normal"),
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", Theme.PANEL2)],
            background=[("readonly", Theme.PANEL2)],
            foreground=[("readonly", Theme.TEXT)],
        )

# -------------------------
# App Root (Page manager)
# -------------------------
class PanicPasteApp(tk.Tk):
    """
    Main Application class.
    """
    
    def __init__(self) -> None:
        super().__init__()

        self.title("Panic Paste")
        self.geometry("1040x640")
        self.minsize(900, 560)
        self.configure(bg=Theme.BG)

        Theme.apply_ttk_style(self)

        self.engine: GameEngine = GameEngine()
        self.leaderboard_service: LeaderboardService = LeaderboardService()
        
        # State: last run result for highlighting
        self.last_run_result: Optional[GameResult] = None

        self.container: tk.Frame = tk.Frame(self, bg=Theme.BG)
        self.container.pack(fill="both", expand=True)

        self.pages: Dict[str, tk.Frame] = {}
        
        for PageClass in (HomePage, SetupPage, GamePage, TimeTrialPage, ResultsPage, LeaderboardPage):
            page = PageClass(parent=self.container, app=self)
            self.pages[PageClass.__name__] = page
            page.grid(row=0, column=0, sticky="NSEW")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show("HomePage")

    def show(self, page_name: str) -> None:
        page = self.pages[page_name]
        page.tkraise()
        if hasattr(page, "on_show"):
            getattr(page, "on_show")()

# -------------------------
# Base Page
# -------------------------
class NeonPage(tk.Frame):
    def __init__(self, parent: tk.Widget, app: PanicPasteApp) -> None:
        super().__init__(parent, bg=Theme.BG)
        self.app: PanicPasteApp = app

        self.panel: tk.Frame = tk.Frame(
            self,
            bg=Theme.PANEL,
            highlightthickness=2,
            highlightbackground=Theme.NEON_CYAN,
        )
        self.panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.86, relheight=0.84)

        self.inner: tk.Frame = tk.Frame(
            self.panel,
            bg=Theme.PANEL2,
            highlightthickness=2,
            highlightbackground=Theme.NEON_PINK,
        )
        self.inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.965, relheight=0.955)

        self.header: tk.Frame = tk.Frame(self.inner, bg=Theme.PANEL, height=70)
        self.header.pack(fill="x", side="top")

        self.header_title: tk.Label = tk.Label(
            self.header,
            text="PANIC PASTE",
            bg=Theme.PANEL,
            fg=Theme.NEON_CYAN,
            font=Theme.font(18, "bold"),
        )
        self.header_title.pack(side="left", padx=18, pady=14)

        self.header_hint: tk.Label = tk.Label(
            self.header,
            text="ARCADE TYPE RACER",
            bg=Theme.PANEL,
            fg=Theme.MUTED,
            font=Theme.font(10, "normal"),
        )
        self.header_hint.pack(side="right", padx=18)

        self.body: tk.Frame = tk.Frame(self.inner, bg=Theme.PANEL2)
        self.body.pack(fill="both", expand=True)


# ============================================================
# 1) Home Page
# ============================================================
class HomePage(NeonPage):
    def __init__(self, parent: tk.Widget, app: PanicPasteApp) -> None:
        super().__init__(parent, app)
        self.header_title.configure(text="PANIC PASTE")
        self.header_hint.configure(text="PRESS ANY KEY")

        center = tk.Frame(self.body, bg=Theme.PANEL2)
        center.pack(expand=True)

        self.title_label = tk.Label(
            center,
            text="PANIC\nPASTE",
            bg=Theme.PANEL2,
            fg=Theme.NEON_PINK,
            font=Theme.font(44, "bold"),
            justify="center",
        )
        self.title_label.pack(pady=(10, 12))

        self.subtitle = tk.Label(
            center,
            text="TYPE RACER  -  ARCADE EDITION",
            bg=Theme.PANEL2,
            fg=Theme.NEON_CYAN,
            font=Theme.font(14, "bold"),
        )
        self.subtitle.pack(pady=(0, 26))
        # flashing press to start label
        self.flash = tk.Label(
            center,
            text=">>> PRESS ANY BUTTON TO START <<<",
            bg=Theme.PANEL2,
            fg=Theme.NEON_YELLOW,
            font=Theme.font(14, "bold"),
        )
        self.flash.pack(pady=(0, 18))

        self.tip = tk.Label(
            center,
            text="(A DS project made by Ain Shams Engineering Students)",
            bg=Theme.PANEL2,
            fg=Theme.MUTED,
            font=Theme.font(10, "normal"),
        )
        self.tip.pack()

        self._flash_on: bool = True
        self._flash_job: Optional[str] = None

    def on_show(self) -> None:
        self._bind_start_keys()
        self._start_flashing()

    def _bind_start_keys(self) -> None:
        self.bind_all("<Key>", self._go)
        self.bind_all("<Button-1>", self._go)

    def _unbind_start_keys(self) -> None:
        self.unbind_all("<Key>")
        self.unbind_all("<Button-1>")

    def _start_flashing(self) -> None:
        # Cancel any existing flash job to prevent multiple concurrent loops
        if self._flash_job is not None:
            self.after_cancel(self._flash_job)
        self._flash_on = True
        self._flash_tick()

    def _flash_tick(self) -> None:
        # Toggle the boolean state for the flashing effect
        self._flash_on = not self._flash_on
        # Update the label color: NEON_YELLOW when on, same as background (PANEL2) when off
        self.flash.configure(fg=Theme.NEON_YELLOW if self._flash_on else Theme.PANEL2)
        # Schedule the next execution of this method in 450ms to create a continuous loop
        self._flash_job = self.after(450, self._flash_tick)

    def _go(self, _event: Optional[tk.Event] = None) -> None:
        self._unbind_start_keys()
        if self._flash_job is not None:
            self.after_cancel(self._flash_job)
            self._flash_job = None
        self.app.show("SetupPage")


# ============================================================
# 2) Setup Page
# ============================================================
class SetupPage(NeonPage):
    def __init__(self, parent: tk.Widget, app: PanicPasteApp) -> None:
        super().__init__(parent, app)
        self.header_hint.configure(text="SETUP")

        wrap = tk.Frame(self.body, bg=Theme.PANEL2)
        wrap.pack(expand=True)

        title = tk.Label(
            wrap,
            text="SELECT DIFFICULTY",
            bg=Theme.PANEL2,
            fg=Theme.NEON_CYAN,
            font=Theme.font(18, "bold"),
        )
        title.pack(pady=(8, 18))

        form = tk.Frame(wrap, bg=Theme.PANEL2)
        form.pack()

        name_lbl = tk.Label(
            form,
            text="PLAYER NAME",
            bg=Theme.PANEL2,
            fg=Theme.TEXT,
            font=Theme.font(11, "bold"),
        )
        name_lbl.grid(row=0, column=0, sticky="w", pady=(0, 8), padx=(0, 12))

        self.name_var: tk.StringVar = tk.StringVar(value="")
        self.name_entry = ttk.Entry(form, textvariable=self.name_var, width=28)
        self.name_entry.grid(row=1, column=0, sticky="we", padx=(0, 28), pady=(0, 18))

        diff_lbl = tk.Label(
            form,
            text="DIFFICULTY",
            bg=Theme.PANEL2,
            fg=Theme.TEXT,
            font=Theme.font(11, "bold"),
        )
        diff_lbl.grid(row=0, column=1, sticky="w", pady=(0, 8))

        self.difficulties: List[str] = ["Easy", "Medium", "Hard","Time-Trial"]
        self.diff_index: int = 0
        self.diff_var: tk.StringVar = tk.StringVar(value=self.difficulties[self.diff_index])

        diff_picker = tk.Frame(form, bg=Theme.PANEL2)
        diff_picker.grid(row=1, column=1, sticky="w", pady=(0, 18))

        self.left_arrow = tk.Label(
            diff_picker,
            text="<",
            bg=Theme.PANEL2,
            fg=Theme.NEON_CYAN,
            font=Theme.font(16, "bold"),
            cursor="hand2",
        )
        self.left_arrow.pack(side="left", padx=(0, 10))

        self.diff_display = tk.Label(
            diff_picker,
            textvariable=self.diff_var,
            bg=Theme.PANEL2,
            fg=Theme.NEON_PINK if self.diff_index == 3 else Theme.NEON_YELLOW,
            font=Theme.font(14, "bold"),
            width=10,
            anchor="center",
        )
        self.diff_display.pack(side="left")

        self.right_arrow = tk.Label(
            diff_picker,
            text=">",
            bg=Theme.PANEL2,
            fg=Theme.NEON_CYAN,
            font=Theme.font(16, "bold"),
            cursor="hand2",
        )
        self.right_arrow.pack(side="left", padx=(10, 0))

        self.left_arrow.bind("<Button-1>", lambda e: self._cycle_diff(-1))
        self.right_arrow.bind("<Button-1>", lambda e: self._cycle_diff(+1))

        self.error = tk.Label(
            wrap,
            text="",
            bg=Theme.PANEL2,
            fg=Theme.DANGER,
            font=Theme.font(10, "bold"),
        )
        self.error.pack(pady=(0, 10))

        btns = tk.Frame(wrap, bg=Theme.PANEL2)
        btns.pack(pady=(6, 0))

        self.start_btn = ttk.Button(btns, text="START RUN", command=self._start)
        self.start_btn.grid(row=0, column=0, padx=10)

        self.back_btn = ttk.Button(btns, text="BACK", command=lambda: self.app.show("HomePage"))
        self.back_btn.grid(row=0, column=1, padx=10)

        self.name_entry.bind("<Return>", lambda _e: self._start())

    def _cycle_diff(self, direction: int) -> None:
        self.diff_index = (self.diff_index + direction) % len(self.difficulties)
        val = self.difficulties[self.diff_index]
        self.diff_var.set(val)
        
        # Update color dynamically
        if val == "Time-Trial":
            self.diff_display.configure(fg=Theme.NEON_PINK)
        else:
            self.diff_display.configure(fg=Theme.NEON_YELLOW)

    def on_show(self) -> None:
        self.error.configure(text="")
        self.name_entry.focus_set()

    def _start(self) -> None:
        name = self.name_var.get().strip()
        diff = self.diff_var.get().strip()

        if not name:
            self.error.configure(text="ENTER A PLAYER NAME.")
            self.name_entry.focus_set()
            return

        name = re.sub(r"\s+", " ", name)[:16]

        if not re.search(r"[A-Za-z0-9]", name):
            self.error.configure(text="NAME MUST CONTAIN LETTERS OR NUMBERS.")
            self.name_entry.focus_set()
            return

        self.app.engine.start_game(name, diff)
        if diff == "Time-Trial":
             self.app.show("TimeTrialPage")
        else:
             self.app.show("GamePage")


# ============================================================
# 3) Game Page
# ============================================================
class GamePage(NeonPage):
    def __init__(self, parent: tk.Widget, app: PanicPasteApp) -> None:
        super().__init__(parent, app)
        self.header_hint.configure(text="RUNNING…")
        self._timer_job: Optional[str] = None
        self._completion_processed: bool = False

        top = tk.Frame(self.body, bg=Theme.PANEL2)
        top.pack(fill="both", expand=True, padx=18, pady=(18, 10))

        bottom = tk.Frame(self.body, bg=Theme.PANEL2)
        bottom.pack(fill="both", expand=True, padx=18, pady=(10, 18))

        passage_frame = tk.Frame(
            top,
            bg=Theme.PANEL,
            highlightthickness=2,
            highlightbackground=Theme.NEON_GREEN,
        )
        passage_frame.pack(side="left", fill="both", expand=True, padx=(0, 12))

        passage_title = tk.Label(
            passage_frame,
            text="PASSAGE",
            bg=Theme.PANEL,
            fg=Theme.NEON_GREEN,
            font=Theme.font(12, "bold"),
        )
        passage_title.pack(anchor="w", padx=12, pady=(10, 6))

        self.passage_text = tk.Label(
            passage_frame,
            text="",
            bg=Theme.PANEL,
            fg=Theme.TEXT,
            justify="left",
            wraplength=1280,
            font=Theme.font(12, "normal"),
        )
        self.passage_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        timer_frame = tk.Frame(
            top,
            bg=Theme.PANEL,
            highlightthickness=2,
            highlightbackground=Theme.NEON_PINK,
        )
        timer_frame.pack(side="right", fill="y")

        self.timer_header = tk.Label(
            timer_frame,
            text="TIMER",
            bg=Theme.PANEL,
            fg=Theme.NEON_PINK,
            font=Theme.font(12, "bold"),
        )
        self.timer_header.pack(padx=14, pady=(10, 6))

        self.timer_label = tk.Label(
            timer_frame,
            text="0.00s",
            bg=Theme.PANEL,
            fg=Theme.NEON_YELLOW,
            font=Theme.font(22, "bold"),
        )
        self.timer_label.pack(padx=14, pady=(0, 10))

        self.status_label = tk.Label(
            timer_frame,
            text="TYPE TO START",
            bg=Theme.PANEL,
            fg=Theme.MUTED,
            font=Theme.font(10, "bold"),
        )
        self.status_label.pack(padx=14, pady=(0, 12))

        editor_frame = tk.Frame(
            bottom,
            bg=Theme.PANEL,
            highlightthickness=2,
            highlightbackground=Theme.NEON_CYAN,
        )
        editor_frame.pack(fill="both", expand=True)

        editor_header = tk.Frame(editor_frame, bg=Theme.PANEL)
        editor_header.pack(fill="x")

        tk.Label(
            editor_header,
            text="INPUT CONSOLE",
            bg=Theme.PANEL,
            fg=Theme.NEON_CYAN,
            font=Theme.font(12, "bold"),
        ).pack(side="left", padx=12, pady=10)

        tk.Label(
            editor_header,
            text="HOOKS READY: CUT / COPY / PASTE / APPEND / DELETE / INSERT",
            bg=Theme.PANEL,
            fg=Theme.MUTED,
            font=Theme.font(9, "bold"),
        ).pack(side="right", padx=12)

        self.text = tk.Text(
            editor_frame,
            bg=Theme.PANEL2,
            fg=Theme.TEXT,
            insertbackground=Theme.NEON_CYAN,
            relief="flat",
            padx=12,
            pady=10,
            wrap="word",
            font=Theme.font(13, "normal"),
            undo=True,
        )
        self.text.tag_configure("correct", foreground=Theme.TEXT)
        self.text.tag_configure("error", foreground=Theme.DANGER)
        self.text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        controls = tk.Frame(self.body, bg=Theme.PANEL2)
        controls.pack(fill="x", padx=18, pady=(0, 16))

        ttk.Button(controls, text="RESET RUN", command=self._reset_run).pack(side="left")
        ttk.Button(controls, text="QUIT TO HOME", command=self._quit_to_home).pack(side="right")

        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<KeyRelease>", self._on_key_release)
        self.text.bind("<Control-c>", self._hook_copy)
        self.text.bind("<Control-x>", self._hook_cut)
        self.text.bind("<Control-v>", self._hook_paste)
    
    def _on_key_release(self, event: Optional[tk.Event] = None) -> None:
        curr_text = self.text.get("1.0", "end")
        
        _, complete, char_correctness = self.app.engine.submit_text(curr_text)
        
        self._apply_highlighting(char_correctness, len(self.app.engine.target_text))
        
        if complete and not self._completion_processed:
             self._handle_completion()
        else:
             target_short = self.app.engine._normalize(self.app.engine.target_text)
             typed_short = self.app.engine._normalize(curr_text)
             if typed_short != target_short:
                  # Only show keep typing if timer isn't running in standard mode? 
                  # Or just always.
                   if self.app.engine.is_running:
                        pass # keep timer
                   else:
                        self.status_label.configure(text="KEEP TYPING…")

    def _apply_highlighting(self, char_correctness: List[bool], target_len: int) -> None:
        self.text.tag_remove("error", "1.0", "end")
        self.text.tag_remove("correct", "1.0", "end")
        
        for i, is_correct in enumerate(char_correctness):
            index_start = f"1.0+{i}c"
            index_end = f"1.0+{i+1}c"

            if i >= target_len:
                self.text.tag_add("error", index_start, index_end)
            elif is_correct:
                self.text.tag_add("correct", index_start, index_end)
            else:
                self.text.tag_add("error", index_start, index_end)

    def on_show(self) -> None:
        name = self.app.engine.player_name
        diff = self.app.engine.difficulty
        passage = self.app.engine.target_text

        self.header_title.configure(text=f"PANIC PASTE — {name}")
        self.header_hint.configure(text=f"DIFFICULTY: {diff}  •  RUNNING…")

        self.passage_text.configure(text=passage)

        self.text.delete("1.0", "end")
        self.text.edit_reset()
        self.text.focus_set()

        self._reset_timer_label()
        self.status_label.configure(text="TYPE TO START")

        self.timer_header.configure(fg=Theme.NEON_PINK) # Default
        
        if self._timer_job is not None:
            self.after_cancel(self._timer_job)
            self._timer_job = None

        self.text.edit_modified(False)
        self._completion_processed = False

    def _reset_timer_label(self) -> None:
         self.timer_label.configure(text="0.00s")

    def _reset_run(self) -> None:
        self.app.engine.start_game(self.app.engine.player_name, self.app.engine.difficulty)
        self.on_show()

    def _quit_to_home(self) -> None:
        self._stop_timer()
        self.app.engine.stop_timer()
        self.app.show("HomePage")

    def _start_timer_if_needed(self) -> None:
        if self.app.engine.is_running:
            return
        
        self.app.engine.start_timer()
        self.status_label.configure(text="GO! GO! GO!")
        self._tick()

    def _stop_timer(self) -> None:
        if self._timer_job is not None:
            self.after_cancel(self._timer_job)
            self._timer_job = None

    def _tick(self) -> None:
        """Standard Timer: Count Up"""
        if not self.app.engine.is_running:
            return

        elapsed = self.app.engine.get_elapsed_time()
        self.timer_label.configure(text=f"{elapsed:0.2f}s")
        self._timer_job = self.after(33, self._tick)

    def _on_modified(self, _event: Optional[tk.Event] = None) -> None:
        if self.text.edit_modified():
            self._start_timer_if_needed()
            self.text.edit_modified(False)

    def _handle_completion(self) -> None:
        self._completion_processed = True
        # Stop UI timer visual
        self._stop_timer()
        
        # Get result from engine
        res: GameResult = self.app.engine.get_results()
        
        self._save_and_show_results(res)

    def _save_and_show_results(self, res: GameResult) -> None:
        # Create strict entry for leaderboard
        entry = LeaderboardEntry(
            player_name=res.player_name,
            difficulty=res.difficulty,
            wpm=res.wpm,
            time_seconds=round(res.time_seconds, 2)
        )
        
        # Add to leaderboard service
        self.app.leaderboard_service.add_entry(entry)
        
        # Save results for current session display
        self.app.last_run_result = res
        
        self.app.show("ResultsPage")

    def _hook_copy(self, _event: tk.Event) -> Optional[str]:
        return None

    def _hook_cut(self, _event: tk.Event) -> Optional[str]:
        return None

    def _hook_paste(self, _event: tk.Event) -> Optional[str]:
        return None


# ============================================================
# 3.5) Time Trial Page
# ============================================================
class TimeTrialPage(GamePage):
    """
    Inherits from GamePage but alters the timer logic to countdown from 30s.
    """
    def on_show(self) -> None:
        super().on_show()
        # Visual Tweaks for Time Trial
        self.header_hint.configure(text="TIME TRIAL  •  SURVIVE")
        self.timer_header.configure(fg=Theme.NEON_PINK)
        self.timer_label.configure(text="30.00s", fg=Theme.NEON_PINK)

    def _reset_timer_label(self) -> None:
        self.timer_label.configure(text="30.00s")

    def _tick(self) -> None:
        """Countdown Timer: 30s -> 0s"""
        if not self.app.engine.is_running:
            return

        elapsed = self.app.engine.get_elapsed_time()
        remaining = 30.0 - elapsed
        
        if remaining <= 0:
            remaining = 0.0
            self.timer_label.configure(text="0.00s")
            self._handle_timeout()
            return
        
        self.timer_label.configure(text=f"{remaining:0.2f}s")
        self._timer_job = self.after(33, self._tick)

    def _handle_timeout(self) -> None:
        self._completion_processed = True
        self._stop_timer()
        
        # Force finish in engine to calc stats based on what we have
        curr_text = self.text.get("1.0", "end")
        self.app.engine.force_finish(curr_text)
        
        res: GameResult = self.app.engine.get_results()
        # Override time to 30.00 for consistency in result display
        res.time_seconds = 30.00
        
        self._save_and_show_results(res)


# ============================================================
# 4) Results Page
# ============================================================
class ResultsPage(NeonPage):
    def __init__(self, parent: tk.Widget, app: PanicPasteApp) -> None:
        super().__init__(parent, app)
        self.header_hint.configure(text="RESULTS")

        wrap = tk.Frame(self.body, bg=Theme.PANEL2)
        wrap.pack(expand=True)

        self.big = tk.Label(
            wrap,
            text="RUN COMPLETE!",
            bg=Theme.PANEL2,
            fg=Theme.NEON_GREEN,
            font=Theme.font(26, "bold"),
        )
        self.big.pack(pady=(6, 16))

        self.stats = tk.Label(
            wrap,
            text="",
            bg=Theme.PANEL2,
            fg=Theme.TEXT,
            font=Theme.font(13, "normal"),
            justify="left",
        )
        self.stats.pack(pady=(0, 18))

        btns = tk.Frame(wrap, bg=Theme.PANEL2)
        btns.pack(pady=6)

        ttk.Button(btns, text="VIEW LEADERBOARD", command=lambda: self.app.show("LeaderboardPage")).grid(row=0, column=0, padx=10)
        ttk.Button(btns, text="RETRY", command=lambda: self.app.show("GamePage") if self.app.last_run_result and self.app.last_run_result.difficulty != "Time-Trial" else self.app.show("TimeTrialPage")).grid(row=0, column=1, padx=10)
        ttk.Button(btns, text="HOME", command=lambda: self.app.show("HomePage")).grid(row=0, column=2, padx=10)

    def on_show(self) -> None:
        res = self.app.last_run_result
        if not res:
            return

        self.header_title.configure(text=f"PANIC PASTE — {res.player_name}")
        self.header_hint.configure(text="RESULTS")
        
        # Different message for Time Trial?
        if res.difficulty == "Time-Trial":
             self.big.configure(text="TIME'S UP!", fg=Theme.NEON_PINK)
        else:
             self.big.configure(text="RUN COMPLETE!", fg=Theme.NEON_GREEN)

        self.stats.configure(
            text=(
                f"PLAYER:   {res.player_name}\n"
                f"MODE:     {res.difficulty}\n"
                f"TIME:     {res.time_seconds:0.2f}s\n"
                f"WPM:      {res.wpm}\n"
            )
        )


# ============================================================
# 5) Leaderboard Page
# ============================================================
class LeaderboardPage(NeonPage):
    def __init__(self, parent: tk.Widget, app: PanicPasteApp) -> None:
        super().__init__(parent, app)
        self.header_hint.configure(text="LEADERBOARD")

        outer = tk.Frame(self.body, bg=Theme.PANEL2)
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        title = tk.Label(
            outer,
            text="TOP 10 PILOTS",
            bg=Theme.PANEL2,
            fg=Theme.NEON_YELLOW,
            font=Theme.font(18, "bold"),
        )
        title.pack(anchor="w", pady=(0, 10))

        self.selected_diff: tk.StringVar = tk.StringVar(value="Easy")
        tabbar = tk.Frame(outer, bg=Theme.PANEL2)
        tabbar.pack(fill="x", pady=(0, 10))
        self.tab_buttons: Dict[str, tk.Label] = {}

        for diff in ["Easy", "Medium", "Hard", "Time-Trial"]:
            btn = tk.Label(
                tabbar,
                text=f"[ {diff.upper()} ]",
                bg=Theme.PANEL2,
                fg=Theme.MUTED,
                font=Theme.font(12, "bold"),
                cursor="hand2",
                padx=12,
                pady=6,
            )
            btn.pack(side="left", padx=(0, 10))
            btn.bind("<Button-1>", lambda e, d=diff: self._set_tab(d))
            self.tab_buttons[diff] = btn

        self.table_container: tk.Frame = tk.Frame(
            outer,
            bg=Theme.PANEL,
            highlightthickness=2,
            highlightbackground=Theme.NEON_CYAN,
        )
        self.table_container.pack(fill="both", expand=True)

        self.note = tk.Label(
            outer,
            text="",
            bg=Theme.PANEL2,
            fg=Theme.MUTED,
            font=Theme.font(10, "bold"),
        )
        self.note.pack(anchor="w", pady=(10, 0))

        footer = tk.Frame(outer, bg=Theme.PANEL2)
        footer.pack(fill="x", pady=(12, 0))

        ttk.Button(footer, text="RETRY", command=lambda: self.app.show("GamePage")).pack(side="left")
        ttk.Button(footer, text="HOME", command=lambda: self.app.show("HomePage")).pack(side="right")

    def on_show(self) -> None:
        self._update_tab_styles()
        self._render_table()

    def _set_tab(self, diff: str) -> None:
        self.selected_diff.set(diff)
        self._update_tab_styles()
        self._render_table()

    def _update_tab_styles(self) -> None:
        current = self.selected_diff.get()
        for diff, lbl in self.tab_buttons.items():
            if diff == current:
                lbl.configure(fg=Theme.NEON_PINK if diff == "Time-Trial" else Theme.NEON_CYAN)
            else:
                lbl.configure(fg=Theme.MUTED)

    def _render_table(self) -> None:
        for child in self.table_container.winfo_children():
            child.destroy()

        difficulty = self.selected_diff.get()
        last_result = self.app.last_run_result
        
        # Get strict-typed entries
        entries = self.app.leaderboard_service.get_top_scores(difficulty)

        header = tk.Frame(self.table_container, bg=Theme.PANEL)
        header.pack(fill="x")

        if difficulty == "Time-Trial":
             cols = [("RANK", 6), ("NAME", 20), ("WPM", 10)]
        else:
             cols = [("RANK", 6), ("NAME", 16), ("WPM", 8), ("TIME", 10)]
        for i, (c, w) in enumerate(cols):
            tk.Label(
                header,
                text=c,
                bg=Theme.PANEL,
                fg=Theme.NEON_PINK if difficulty == "Time-Trial" else Theme.NEON_CYAN,
                font=Theme.font(11, "bold"),
                width=w,
                anchor="w",
                padx=8,
            ).grid(row=0, column=i, sticky="w", pady=10)

        body = tk.Frame(self.table_container, bg=Theme.PANEL2)
        body.pack(fill="both", expand=True)

        for idx, entry in enumerate(entries, start=1):
            is_me = False
            # Check if this entry corresponds to our last run
            if last_result:
                # Basic check on equality of values
                if (entry.player_name == last_result.player_name and
                    entry.difficulty == last_result.difficulty and
                    entry.wpm == last_result.wpm and
                    abs(entry.time_seconds - last_result.time_seconds) < 0.01):
                    is_me = True

            bg = Theme.PANEL if is_me else Theme.PANEL2
            fg = Theme.NEON_PINK if is_me else Theme.TEXT

            row = tk.Frame(
                body,
                bg=bg,
                highlightthickness=2 if is_me else 0,
                highlightbackground=Theme.NEON_PINK if is_me else bg,
            )
            row.pack(fill="x", padx=10, pady=6)

            if difficulty == "Time-Trial":
                 values = [f"#{idx}", entry.player_name, str(entry.wpm)]
                 widths = [6, 20, 10]
            else:
                 values = [f"#{idx}", entry.player_name, str(entry.wpm), f"{entry.time_seconds:.2f}s"]
                 widths = [6, 16, 8, 10]

            for i, (val, w) in enumerate(zip(values, widths)):
                tk.Label(
                    row,
                    text=val,
                    bg=bg,
                    fg=fg,
                    font=Theme.font(11, "bold" if is_me else "normal"),
                    width=w,
                    anchor="w",
                    padx=8,
                ).grid(row=0, column=i, sticky="w", pady=6)

        # Update footer note
        color_name = "PINK" if difficulty == "Time-Trial" else "CYAN"
        
        if last_result is None:
            self.note.configure(text="PLAY A RUN TO GET ON THE BOARD.")
        else:
            if last_result.difficulty != difficulty:
                self.note.configure(text=f"SHOWING {difficulty.upper()} — YOUR RUN MAY BE ON ANOTHER TAB.")
            else:
                 # Check if we are in the displayed list
                 in_list = False
                 for entry in entries:
                     if (entry.player_name == last_result.player_name and
                         entry.wpm == last_result.wpm and
                         abs(entry.time_seconds - last_result.time_seconds) < 0.01):
                         in_list = True
                         break
                 
                 if in_list:
                     self.note.configure(text=f"YOUR RUN IS HIGHLIGHTED ({difficulty.upper()}).")
                 else:
                     self.note.configure(text=f"YOUR RUN DID NOT MAKE THE TOP 10 ({difficulty.upper()}).")
