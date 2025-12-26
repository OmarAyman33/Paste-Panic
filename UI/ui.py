import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Tuple, Optional, Any
import re
import pyglet 
import implicit_treap

from engine import GameEngine, GameResult
from leaderboard import LeaderboardService, LeaderboardEntry
from text_editor import TextEditor

FONT_FILE: str = "Public Pixel.ttf"
PIXEL_FONT_NAME: str = "Public Pixel"

pyglet.font.add_file(FONT_FILE)

class Theme: # Theme class for storing colors and fonts (consider it a .css file, might be moved to a separate file in the future)
    # arcade style colors
    BG: str = "#07070B"
    PANEL: str = "#0E1020"
    PANEL2: str = "#0B0C14"

    NEON_CYAN: str = "#00F5FF"
    NEON_PINK: str = "#FF2D95"
    NEON_GREEN: str = "#22FF88"
    NEON_YELLOW: str = "#FFE66D"
    NEON_PURPLE: str = "#D500F9"

    TEXT: str = "#E8ECFF"
    MUTED: str = "#A7B0D6"
    DANGER: str = "#FF3B3B"

    # method to create a font tuple
    @staticmethod
    def font(size: int, weight: str = "normal") -> Tuple[str, int, str]:
        return (PIXEL_FONT_NAME, size, weight)

    @staticmethod # method to apply ttk styles to every root window.
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
    def __init__(self) -> None:
        super().__init__()

        self.title("Panic Paste")
        self.geometry("1040x640")
        self.minsize(900, 560)
        self.configure(bg=Theme.BG)

        Theme.apply_ttk_style(self)

        self.engine = GameEngine()
        self.leaderboard_service = LeaderboardService()
        
        # State: last run result for highlighting
        self.last_run_result = None

        self.container = tk.Frame(self, bg=Theme.BG)
        self.container.pack(fill="both", expand=True)

        self.pages = {}
        
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
# Base Page - > used as a template for other pages
# -------------------------
class NeonPage(tk.Frame):
    def __init__(self, parent: tk.Widget, app: PanicPasteApp) -> None:
        super().__init__(parent, bg=Theme.BG)
        self.app: PanicPasteApp = app

        self.panel: tk.Frame = tk.Frame(
            self,
            bg=Theme.PANEL,
            highlightthickness=2,
            highlightbackground=Theme.NEON_CYAN, # cool arcade style border
        )
        self.panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.86, relheight=0.84)

        self.inner: tk.Frame = tk.Frame(
            self.panel,
            bg=Theme.PANEL2,
            highlightthickness=2,
            highlightbackground=Theme.NEON_PINK, # cool arcade style border (chose two different colors for that retro look)
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
        
        """
            note about tkinter: 
            - each frame is a container for other widgets
            - each widget is a container for other widgets
            - each widget has a pack, grid, place method to position it
            - the order of packing inside of a frame determines the position, similar to a Vbox & Hbox in JavaFx
        """
        
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
        """
        on_show is called when the page is shown, used to define dynamic behavior such as this flashing text effect
        """
        self._bind_start_keys()
        self._start_flashing()


    def _bind_start_keys(self) -> None:
        """
        _bind_start_keys is used to bind the start keys, in this case any key or mouse click
        """
        self.bind_all("<Key>", self._go)
        self.bind_all("<Button-1>", self._go)


    def _unbind_start_keys(self) -> None:
        """
        _unbind_start_keys is used to unbind the start keys, in this case any key or mouse click
        """
        self.unbind_all("<Key>")
        self.unbind_all("<Button-1>")


    def _start_flashing(self) -> None:
        """
        _start_flashing is used to start the flashing effect
        """
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
        """
        _go is called when the start keys are pressed, in this case any key or mouse click
        """
        self._unbind_start_keys()
        if self._flash_job is not None:
            self.after_cancel(self._flash_job)
            self._flash_job = None
        self.app.show("SetupPage") # switch to next page.


# ============================================================
# 2) Setup Page
# ============================================================
class SetupPage(NeonPage):
    """
    Page for player configuration (Name, Difficulty).
    Handles input validation and dynamic difficulty toggling.
    """
    def __init__(self, parent: tk.Widget, app: PanicPasteApp) -> None:
        super().__init__(parent, app)
        self.header_hint.configure(text="SETUP")
        # wrapper frame to center the content
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
        """
        Cycles through difficulty options (Easy, Medium, Hard, Time-Trial).
        Updates the displayed text and color theme dynamically.
        """
        self.diff_index = (self.diff_index + direction) % len(self.difficulties)
        val = self.difficulties[self.diff_index]
        self.diff_var.set(val)
        
        # Update color dynamically for visual feedback
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
    """
    Core Gameplay Page.
    Displays passage text, typing input area, and real-time statistics (Timer).
    Handles real-time text validation and game loop management.
    """
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
        # self.text.bind("<KeyRelease>", self._on_key_release) # Moved logic to specific handlers
        self.text.bind("<Key>", self._on_key)
        self.text.bind("<Control-c>", self._hook_copy)
        self.text.bind("<Control-x>", self._hook_cut)
        self.text.bind("<Control-v>", self._hook_paste)
        self.text.bind("<BackSpace>", self._handle_backspace)
        self.text.bind("<Delete>", self._handle_delete)

    def _get_cursor_index(self) -> int:
        """
        Robustly get the cursor index as a flat integer character offset.
        """
        try:
            # count returns a tuple often, or None if ranges invalid
            count = self.text.count("1.0", "insert", "chars") 
            return count[0] if count else 0
        except tk.TclError:
            return 0

    def _get_selection_indices(self) -> Tuple[int, int]:
        """
        Robustly get selection start/end as flat integer character offsets.
        Returns (-1, -1) if no selection exists.
        """
        try:
            # Check if selection tag exists first
            ranges = self.text.tag_ranges("sel")
            if not ranges:
                return -1, -1
            
            start_idx = ranges[0]
            end_idx = ranges[1]
            
            # Use 'count' to get precise char offset
            count_start = self.text.count("1.0", start_idx, "chars")
            count_end = self.text.count("1.0", end_idx, "chars")
            
            s = count_start[0] if count_start else 0
            e = count_end[0] if count_end else 0
            
            return s, e
        except tk.TclError:
            return -1, -1

    def _update_text_and_cursor(self, new_text: str, new_cursor: int) -> None:
        self.text.delete("1.0", "end")
        self.text.insert("1.0", new_text)
        
        # Restore cursor
        self.text.mark_set("insert", f"1.0+{new_cursor}c")
        self.text.see("insert")
        
        # Trigger correctness check
        self._check_correctness(new_text)


    #OK so imma break tradion and personal beliefs and actually explain this function
    #I basically put the target and the current text ito variables and call the impilcit treap function we made to compare the string to thetreap content
    #after returning where the error is i set it up to turn every letter red if it is after the error
    #I am mainly doing this to keep in mind what i change as i go though the code as i have the attention span of a butterfly
    def _check_correctness(self, curr_text: str) -> None:
        #what do
        target_short = self.app.engine._normalize(self.app.engine.target_text)
        typed_short = self.app.engine._normalize(curr_text)

        first_error_pos, complete = self.WriteTreap.check_equal_so_far(target_short)
        
        char_correctness = []

        for i in range(len(typed_short)):
            if first_error_pos == -1:
                char_correctness.append(True)
            elif i < first_error_pos:
                char_correctness.append(True)
            else:
                char_correctness.append(False)
        
        self._apply_highlighting(char_correctness, len(target_short))

        if complete and not self._completion_processed:
             self._handle_completion()

    #i am not sure of this somthing feels off primarily that we are dealing with two different things being the treap and the text sulmontainously i know thats what we want but it feels wrong
    def _on_key(self, event: tk.Event) -> Optional[str]:
        # Allow navigation keys and shortcuts to pass through (handled by hooks or default)
        if event.keysym in ("Left", "Right", "Up", "Down", "Home", "End", "Return", "Escape"):
            return None
        if event.state & 4: # Control key
            return None

        if event.char and event.char.isprintable():
            current_text = self.text.get("1.0", "end-1c") # -1c to exclude trailing newline
            cursor = self._get_cursor_index()
            
            # Handle selection overwrite
            start, end = self._get_selection_indices()
            if start != -1:
                current_text, cursor = TextEditor.range_delete(current_text, start, end)
                self.WriteTreap.delete_range(start, end)
                # After delete, cursor is at start
            
            new_text, new_cursor = TextEditor.type_char(current_text, cursor, event.char)
            self.WriteTreap.insert(new_cursor -1, event.char) 
            self._update_text_and_cursor(new_text, new_cursor)
            
            self._start_timer_if_needed()
            return "break" # Stop default insertion
        
        return None
    
    # special note: the selection IS already exclusive so when using any implicit treaps use the end selection normally
    # our treaps are made with exclusive end in mind so no need to adjust for that
    def _handle_backspace(self, event: tk.Event) -> Optional[str]:
        current_text = self.text.get("1.0", "end-1c")
        start, end = self._get_selection_indices()
        
        if start != -1:
            # Selection delete
            new_text, new_cursor = TextEditor.range_delete(current_text, start, end)
            self.WriteTreap.delete_range(start, end)
        else:
            # Single char delete
            cursor = self._get_cursor_index()
            if cursor > 0:
                new_text, new_cursor = TextEditor.range_delete(current_text, cursor - 1, cursor)
                self.WriteTreap.erase(cursor - 1);
            else:
                return "break"
                
        self._update_text_and_cursor(new_text, new_cursor)
        self._start_timer_if_needed()
        return "break"

    #clairification the blinking cursor position is the char after it so if the word is hel|lo the cursor index is 3
    #by deleting whats after the cursor we mean deleting the l in hello or rather the position itself
    def _handle_delete(self, event: tk.Event) -> Optional[str]:
        current_text = self.text.get("1.0", "end-1c")
        start, end = self._get_selection_indices()
        
        if start != -1:
            # Selection delete
            new_text, new_cursor = TextEditor.range_delete(current_text, start, end)
            self.WriteTreap.delete_range(start, end)
        else:
            # Single char delete forward
            cursor = self._get_cursor_index()
            if cursor < len(current_text):
                new_text, new_cursor = TextEditor.range_delete(current_text, cursor, cursor + 1)
                self.WriteTreap.erase(cursor);
            else:
                return "break"
                
        self._update_text_and_cursor(new_text, new_cursor)
        self._start_timer_if_needed()
        return "break"

    def _apply_highlighting(self, char_correctness, target_len: int) -> None:
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

    #initialize the treap here and delete previous instances before starting a new run
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

        
        self.WriteTreap = implicit_treap.implicittreap() 

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
        # res: GameResult = self.app.engine.get_results()
        res = GameResult(self.app.engine.player_name, 
                         self.app.engine.difficulty,
                         int(self.WriteTreap.size() / 5 / self.app.engine.get_elapsed_time() * 60),
                         self.app.engine.get_elapsed_time())
        self._save_and_show_results(res)

    def _save_and_show_results(self, res: GameResult) -> None:
        # Use modular insert_player interface
        self.app.leaderboard_service.insert_player(
            username=res.player_name,
            difficulty=res.difficulty,
            score=res.wpm,
            time_seconds=res.time_seconds # Optional param I added for Python fix
        )
        
        
        # Note: insert_player in the requested C++ interface might be strict (username, diff, score).
        # We overloaded it in Python to allow passing time_seconds for better UI feedback.
        # If strict adherence is required, time would be dropped or handled internally.
        # Current insert_player defaults time to 0.0 or handles it internally.
        
        # Save results for current session display
        self.app.last_run_result = res
        
        self.app.show("ResultsPage")

    # -------------------------------------------------------------------------
    # Text Editing Hooks
    # -------------------------------------------------------------------------
    # These methods intercept system events to route text manipulation through
    # the modular TextEditor class. This decoupling is critical for the 
    # planned migration to a C++ backend.
    # -------------------------------------------------------------------------

    def _hook_copy(self, _event: tk.Event) -> Optional[str]:

        current_text = self.text.get("1.0", "end-1c")
        start, end = self._get_selection_indices()
   

        if start != -1:
            self.clipboard_content = self.WriteTreap.copy(start, end)  
            
            
        return "break" # Prevent default Tkinter handling

    def _hook_cut(self, _event: tk.Event) -> Optional[str]:
   
        current_text = self.text.get("1.0", "end-1c") # getting text via tkinter
        start, end = self._get_selection_indices()


        if start != -1:
            # Atomic cut operation via TextEditor
            
            self.clipboard_content = self.WriteTreap.cut(start, end) 

            new_text, new_cursor, _ = TextEditor.range_delete(current_text, start, end)
            
            # Update Editor State
            self._update_text_and_cursor(new_text, new_cursor)
            self._start_timer_if_needed()
            
        return "break"

    def _hook_paste(self, _event: tk.Event) -> Optional[str]:
        """
        Intercepts Paste event.
        Retrieves system clipboard, normalizes, and injects via TextEditor.
        """
        try:
            content = self.clipboard_content.to_string() 
        except tk.TclError:
            return "break" # Clipboard empty or unavailable
            
        if not content:
            return "break"
            
        current_text = self.text.get("1.0", "end-1c")
        cursor = self._get_cursor_index()
        
        # If selection exists, Paste acts as "Replace Selection"
        start, end = self._get_selection_indices()
        if start != -1:
             current_text, cursor = TextEditor.range_delete(current_text, start, end)
             self.WriteTreap.delete_range(start, end)

        # Insert content
        new_text, new_cursor = TextEditor.paste(current_text, cursor, content)
        self.WriteTreap.paste(cursor, self.clipboard_content)
        
        self._update_text_and_cursor(new_text, new_cursor)
        self._start_timer_if_needed()
        
        return "break"


# ============================================================
# 3.5) Time Trial Page
# ============================================================
class TimeTrialPage(GamePage):
    """
    Subclass of GamePage for the 'Time Trial' mode.
    
    Key Differences:
    - Timer counts DOWN from 30 seconds instead of UP.
    - Game ends automatically when time expires.
    - Visual theme adjustments (Pink timer).
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
        """
        Countdown Timer Logic.
        Calculates remaining time (30s - elapsed) and handles timeout event.
        Overrides GamePage._tick.
        """
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
    """
    Displays the outcome of a finished run (WPM, Time, Correctness).
    Providers options to Retry, Return Home, or View Leaderboard.
    """
    def __init__(self, parent: tk.Widget, app: PanicPasteApp) -> None:
        super().__init__(parent, app)
        self.header_hint.configure(text="RESULTS")

        # Top frame for title and hint
        top = tk.Frame(self.body, bg=Theme.PANEL2)
        top.pack(fill="x", padx=18, pady=(18, 10))

        # Center frame for main content
        center = tk.Frame(self.body, bg=Theme.PANEL2)
        center.pack(expand=True, padx=20, pady=20)

        # Result Details Container
        self.stats_frame = tk.Frame(
            center, 
            bg=Theme.PANEL, 
            highlightthickness=2, 
            highlightbackground=Theme.NEON_PURPLE # Distinct border color for Results
        )
        self.stats_frame.pack(fill="x", pady=(0, 20), ipadx=20, ipady=10)

        # Big message (e.g., "RUN COMPLETE!" or "TIME'S UP!")
        self.big = tk.Label(
            self.stats_frame, # Changed parent to stats_frame
            text="RUN COMPLETE!",
            bg=Theme.PANEL, # Changed background to PANEL
            fg=Theme.NEON_GREEN,
            font=Theme.font(26, "bold"),
        )
        self.big.pack(pady=(12, 16)) # Adjusted pady

        # Detailed statistics display
        self.stats = tk.Label(
            self.stats_frame, # Changed parent to stats_frame
            text="",
            bg=Theme.PANEL, # Changed background to PANEL
            fg=Theme.TEXT,
            font=Theme.font(13, "normal"),
            justify="left",
        )
        self.stats.pack(pady=(0, 12)) # Adjusted pady

        # Buttons for navigation
        btns = tk.Frame(center, bg=Theme.PANEL2) # Changed parent to center
        btns.pack(pady=(10, 0)) # Adjusted pady

        ttk.Button(btns, text="VIEW LEADERBOARD", command=lambda: self.app.show("LeaderboardPage")).grid(row=0, column=0, padx=10)
        # Retry button logic: go to GamePage for normal, TimeTrialPage for time trial
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
    """
    Displays the top 10 scores for each difficulty category.
    Features tabbed navigation and highlights the current user's latest run.
    """
    def __init__(self, parent: tk.Widget, app: PanicPasteApp) -> None:
        """
        Initializes the LeaderboardPage.
        Sets up the UI elements for displaying leaderboard data,
        including difficulty tabs and the score table.
        """
        super().__init__(parent, app)
        self.header_hint.configure(text="LEADERBOARD")

        # StringVar to hold the currently selected difficulty tab
        self.selected_diff: tk.StringVar = tk.StringVar(value="Easy")
        
        # Main layout container for the leaderboard content
        outer = tk.Frame(self.body, bg=Theme.PANEL2)
        outer.pack(fill="both", expand=True, padx=20, pady=20) # Adjusted padding

        # Title for the leaderboard
        title = tk.Label(
            outer,
            text="TOP 10 PILOTS",
            bg=Theme.PANEL2,
            fg=Theme.NEON_YELLOW,
            font=Theme.font(18, "bold"),
        )
        title.pack(anchor="w", pady=(0, 10))
        
        # Frame for difficulty selection tabs
        tabs = tk.Frame(outer, bg=Theme.PANEL2) # Renamed from tabbar
        tabs.pack(fill="x", pady=(0, 10)) # Adjusted padding
        
        # Dictionary to store references to tab buttons for dynamic styling
        self.tab_buttons: Dict[str, tk.Label] = {}
        for diff in ["Easy", "Medium", "Hard", "Time-Trial"]:
            btn = tk.Label(
                tabs, # Parent is now 'tabs'
                text=f"[ {diff.upper()} ]",
                bg=Theme.PANEL2,
                fg=Theme.MUTED,
                font=Theme.font(10, "bold"), # Changed font size
                cursor="hand2",
            )
            btn.pack(side="left", padx=(0, 15)) # Adjusted padx
            # Bind click event with partial function for strict scoping
            btn.bind("<Button-1>", lambda e, d=diff: self._set_tab(d))
            self.tab_buttons[diff] = btn

        # Leaderboard Table Container
        # Outer frame with highlight for the table
        self.table_frame = tk.Frame( # Renamed from table_container
            outer,
            bg=Theme.PANEL,
            highlightthickness=2,
            highlightbackground=Theme.NEON_CYAN,
        )

        self.table_frame.pack(fill="both", expand=True)

        # Inner frame for the actual table content, allowing for padding within the border
        self.table_container = tk.Frame(self.table_frame, bg=Theme.PANEL2)
        self.table_container.pack(fill="both", expand=True, padx=2, pady=2)

        # Note/hint label for user feedback (e.g., "Your run is highlighted")
        self.note = tk.Label(
            outer,
            text="",
            bg=Theme.PANEL2,
            fg=Theme.MUTED,
            font=Theme.font(10, "bold"),
        )
        self.note.pack(anchor="w", pady=(10, 0)) # Adjusted pady

        # Footer frame for navigation buttons
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
        
        # Get strict-typed entries via new interface
        # Returns List[Tuple[str, int, float, str]] -> (name, wpm, time, diff)
        entries = self.app.leaderboard_service.get_top_10(difficulty)

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

        # Remove unused body frame that was causing shift
        # body = tk.Frame(self.table_container, bg=Theme.PANEL2)
        # body.pack(fill="both", expand=True)

        for i, row_data in enumerate(entries):
            # Unpack tuple from get_top_10
            name, wpm, time_val, _ = row_data
            
            # Check if this row is me (last result match)
            is_me = False
            if last_result:
                if (name == last_result.player_name and 
                    wpm == last_result.wpm and 
                    abs(time_val - last_result.time_seconds) < 0.1):
                    is_me = True

            bg_color = Theme.PANEL if i % 2 == 0 else Theme.PANEL2
            fg_color = Theme.TEXT
            
            if is_me:
                bg_color = Theme.PANEL
                fg_color = Theme.NEON_PINK
            
            row = tk.Frame(self.table_container, bg=bg_color)
            if is_me:
                row.configure(highlightthickness=1, highlightbackground=Theme.NEON_PINK)
                
            row.pack(fill="x", pady=2)

            # Columns depending on difficulty
            if difficulty == "Time-Trial":
                 vals = [f"{i+1}.", name, str(wpm)]
            else:
                 vals = [f"{i+1}.", name, str(wpm), f"{time_val:.2f}s"]
            
            for j, (val) in enumerate(vals):
                # Match width from cols def
                w = cols[j][1]
                
                align = "w"
                tk.Label(
                    row, 
                    text=val,
                    bg=bg_color,
                    fg=fg_color,
                    font=Theme.font(11, "bold" if is_me else "normal"),
                    width=w,
                    anchor=align,
                    padx=8
                ).grid(row=0, column=j, sticky="w", pady=6)

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
                     player_name, wpm, time_seconds, _ = entry  
                     if (player_name == last_result.player_name and
                         wpm == last_result.wpm and
                         abs(time_seconds - last_result.time_seconds) < 0.01):
                         in_list = True
                         break
                 
                 if in_list:
                     self.note.configure(text=f"YOUR RUN IS HIGHLIGHTED ({difficulty.upper()}).")
                 else:
                     self.note.configure(text=f"YOUR RUN DID NOT MAKE THE TOP 10 ({difficulty.upper()}).")
