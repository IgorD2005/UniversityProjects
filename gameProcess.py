import tkinter as tk
from tkinter import messagebox
from questionsLogic import get_random_questions
from databaseLogic import Session, Player, Game
from pdfLogic import generate_game_results_pdf


class CrosswordGame:
    FONT_TITLE_GAME = ("Lucida Console", 40, "bold")
    FONT_QUESTION = ("Lucida Console", 24, "bold")
    FONT_INFO = ("Lucida Console", 20, "bold")
    FONT_ANSWER_ENTRY = ("Lucida Console", 18)
    FONT_BUTTON_GAME = ("Lucida Console", 16, "bold")
    FONT_HINT = ("Lucida Console", 18)
    FONT_CELL = ("Lucida Console", 30, "bold")
    FONT_RESULTS_TITLE = ("Lucida Console", 40, "bold")
    FONT_RESULTS_MESSAGE = ("Lucida Console", 20)
    FONT_RESULTS_WINNER = ("Lucida Console", 25, "bold")
    FONT_RESULTS_SCORES = ("Lucida Console", 18)

    COLOR_BG_GAME = "silver"
    COLOR_FG_DEFAULT = "black"
    COLOR_INFO_TIME = "#4CAF50"
    COLOR_INFO_SCORES = "#2196F3"
    COLOR_SUBMIT_BTN = "#8BC34A"
    COLOR_SUBMIT_BTN_ACTIVE = "#689F38"
    COLOR_GIVEUP_BTN = "#F44336"
    COLOR_GIVEUP_BTN_ACTIVE = "#D32F2F"
    COLOR_PAUSE_BTN = "#FFEB3B"
    COLOR_PAUSE_BTN_ACTIVE = "#FBC02D"
    COLOR_HINT_CELL_BG = "#E0E0E0"
    COLOR_HINT_CELL_FG = "#333333"
    COLOR_WINNER = "gold"
    COLOR_HINT_TEXT = "#616161"

    def __init__(self, parent, players_data, language, difficulty, mode, on_game_finish_callback):
        self.parent = parent
        self.players = [name for name, _ in players_data]
        self.language = language
        self.difficulty = difficulty
        self.mode = mode
        self.on_game_finish_callback = on_game_finish_callback

        self.current_player_index = 0
        self.scores = {name: 0 for name in self.players}
        self.player_colors = ['blue', 'red', 'green', 'yellow']

        self.timer_id = None
        self.paused = False
        self.time_left = 0

        self.time_limits = {
            "Hard": 8 * 60,
            "Medium": 10 * 60,
            "Easy": 12 * 60
        }

        self.questions = get_random_questions(language, difficulty)
        self.current_question = None
        self.original_question_text = ""

        self.game_window = None
        self.timer_label = None
        self.current_player_label = None
        self.scores_label = None
        self.question_label = None
        self.answer_hint_frame = None
        self.letter_display_labels = []
        self.length_label = None
        self.answer_entry = None
        self.submit_btn = None
        self.give_up_btn = None
        self.pause_btn = None
        self.results_frame = None

        self.create_game_window()

    def create_game_window(self):
        """Sets up the main game UI frame and widgets."""
        self.game_window = tk.Frame(self.parent, bg=self.COLOR_BG_GAME)
        self.game_window.pack(fill="both", expand=True)

        self.info_frame = tk.Frame(self.game_window, bg=self.COLOR_BG_GAME, bd=2, relief="groove")
        self.info_frame.pack(fill=tk.X, padx=20, pady=20)

        if self.mode == "For Time":
            self.time_left = self.time_limits.get(self.difficulty, 300)
            self.timer_label = tk.Label(self.info_frame,
                                        text=f"Time: {self.time_left // 60}:{self.time_left % 60:02d}",
                                        font=self.FONT_INFO, bg=self.COLOR_BG_GAME, fg=self.COLOR_INFO_TIME)
            self.timer_label.pack(side=tk.LEFT, padx=15)
            self.start_timer()
        else:
            self.timer_label = tk.Label(self.info_frame, text="", font=self.FONT_INFO, bg=self.COLOR_BG_GAME)
            self.timer_label.pack(side=tk.LEFT, padx=15)

        self.current_player_label = tk.Label(self.info_frame,
                                             text=f"Current: {self.players[self.current_player_index]}",
                                             font=self.FONT_INFO,
                                             bg=self.COLOR_BG_GAME,
                                             fg=self.player_colors[self.current_player_index])
        self.current_player_label.pack(side=tk.LEFT, padx=30)

        self.scores_label = tk.Label(self.info_frame, text=self._get_scores_text(),
                                     font=self.FONT_INFO, bg=self.COLOR_BG_GAME, fg=self.COLOR_INFO_SCORES)
        self.scores_label.pack(side=tk.RIGHT, padx=15)

        self.game_display_frame = tk.Frame(self.game_window, bg=self.COLOR_BG_GAME)
        self.game_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.question_label = tk.Label(self.game_display_frame, text="",
                                       font=self.FONT_QUESTION, bg=self.COLOR_BG_GAME,
                                       wraplength=self.parent.winfo_screenwidth() * 0.7)
        self.question_label.pack(pady=40)

        self.answer_hint_frame = tk.Frame(self.game_display_frame, bg=self.COLOR_BG_GAME)
        self.answer_hint_frame.pack(pady=20)

        self.length_label = tk.Label(self.game_display_frame, text="",
                                     font=self.FONT_HINT, bg=self.COLOR_BG_GAME, fg=self.COLOR_HINT_TEXT)
        self.length_label.pack(pady=10)

        self.input_control_frame = tk.Frame(self.game_window, bg=self.COLOR_BG_GAME, bd=2, relief="ridge")
        self.input_control_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(self.input_control_frame, text="Your answer:", font=self.FONT_ANSWER_ENTRY,
                 bg=self.COLOR_BG_GAME).pack(
            side=tk.LEFT, padx=10)

        self.answer_entry = tk.Entry(self.input_control_frame, font=self.FONT_ANSWER_ENTRY, width=25, bd=2,
                                     relief="solid")
        self.answer_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.answer_entry.bind("<Return>", self._check_answer_event)

        self.submit_btn = tk.Button(self.input_control_frame, text="Submit", font=self.FONT_BUTTON_GAME,
                                    command=self._check_answer_click, bg=self.COLOR_SUBMIT_BTN, fg="white",
                                    activebackground=self.COLOR_SUBMIT_BTN_ACTIVE)
        self.submit_btn.pack(side=tk.LEFT, padx=10)

        self.give_up_btn = tk.Button(self.input_control_frame, text="Give Up", font=self.FONT_BUTTON_GAME,
                                     command=self._give_up, bg=self.COLOR_GIVEUP_BTN, fg="white",
                                     activebackground=self.COLOR_GIVEUP_BTN_ACTIVE)
        self.give_up_btn.pack(side=tk.RIGHT, padx=20)

        if self.mode == "For Time":
            self.pause_btn = tk.Button(self.input_control_frame, text="Pause", font=self.FONT_BUTTON_GAME,
                                       command=self._toggle_pause, bg=self.COLOR_PAUSE_BTN, fg="black",
                                       activebackground=self.COLOR_PAUSE_BTN_ACTIVE)
            self.pause_btn.pack(side=tk.RIGHT, padx=10)
        else:
            self.pause_btn = None

        self._init_game_board()

    def _init_game_board(self):
        """Clears previous question UI and loads the next question."""
        for label in self.letter_display_labels:
            label.destroy()
        self.letter_display_labels = []

        if self.questions:
            self.current_question = self.questions.pop(0)
            self.original_question_text = self.current_question.question
            self.question_label.config(text=f"Question: {self.original_question_text}")
            self._display_answer_hint()
            self._enable_input()
        else:
            self._end_game("All questions answered!")

    def _display_answer_hint(self):
        """
        Creates/updates the visual hint for the answer length using individual labels.
        """
        for label in self.letter_display_labels:
            label.destroy()
        self.letter_display_labels = []

        if not self.current_question:
            return

        answer_length = len(self.current_question.answer)

        if not hasattr(self, 'answer_hint_frame') or not self.answer_hint_frame.winfo_exists():
            self.answer_hint_frame = tk.Frame(self.game_display_frame, bg=self.COLOR_BG_GAME)
            self.answer_hint_frame.pack(pady=20)

        for i in range(answer_length):
            label = tk.Label(self.answer_hint_frame, text='',
                             font=self.FONT_CELL,
                             bg=self.COLOR_HINT_CELL_BG, fg=self.COLOR_HINT_CELL_FG,
                             relief="solid", bd=1, width=3, height=1)
            label.grid(row=0, column=i, padx=2, pady=2)
            self.letter_display_labels.append(label)

        self.length_label.config(text=f"Answer has {answer_length} letters")

    def _get_scores_text(self):
        """Returns a formatted string of current player scores."""
        return " | ".join(f"{name}: {self.scores[name]}" for name in self.players)

    def start_timer(self):
        """Starts or resumes the game timer."""
        if self.paused:
            return
        if self.timer_id:
            self.game_window.after_cancel(self.timer_id)

        self.time_left -= 1
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.config(text=f"Time: {mins:02d}:{secs:02d}")

        if self.time_left <= 0:
            self._end_game("Time's up!")
        else:
            self.timer_id = self.game_window.after(1000, self.start_timer)

    def _check_answer_event(self, event=None):
        """Wrapper for check_answer called by Return key."""
        self._check_answer_logic()

    def _check_answer_click(self):
        """Wrapper for check_answer called by Submit button click."""
        self._check_answer_logic()

    def _check_answer_logic(self):
        """Performs the answer check logic."""
        if self.paused and self.mode == "For Time":
            messagebox.showinfo("Game Paused", "Cannot enter answer while game is paused.")
            return

        answer = self.answer_entry.get().strip()
        if not answer:
            return

        if not self.current_question:
            messagebox.showerror("Error", "No active question.")
            return

        if answer.lower() == self.current_question.answer.lower():
            self.scores[self.players[self.current_player_index]] += 10
            messagebox.showinfo("Correct!", "Your answer is correct!")
            self._next_question()
        else:
            messagebox.showerror("Wrong", f"Incorrect answer")
            if self.mode == "To mistake":
                self._next_question()

        self.answer_entry.delete(0, tk.END)
        self.scores_label.config(text=self._get_scores_text())

    def _give_up(self):
        """Handles the 'Give Up' action."""
        if self.paused and self.mode == "For Time":
            messagebox.showinfo("Game Paused", "Cannot give up while game is paused.")
            return
        self._next_question()

    def _next_question(self):
        """Advances to the next question or ends the game if no more questions."""
        for label in self.letter_display_labels:
            label.destroy()
        self.letter_display_labels = []

        if self.questions:
            self.current_question = self.questions.pop(0)
            self.original_question_text = self.current_question.question
            self.question_label.config(text=f"Question: {self.original_question_text}")
            self._display_answer_hint()

            if len(self.players) > 1:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
                self.current_player_label.config(
                    text=f"Current: {self.players[self.current_player_index]}",
                    fg=self.player_colors[self.current_player_index]
                )
            self._enable_input()
        else:
            self._end_game("All questions answered!")


    def _disable_input(self):
        """Disables input widgets."""
        self.answer_entry.config(state=tk.DISABLED)
        self.submit_btn.config(state=tk.DISABLED)
        self.give_up_btn.config(state=tk.DISABLED)

    def _enable_input(self):
        """Enables input widgets."""
        self.answer_entry.config(state=tk.NORMAL)
        self.submit_btn.config(state=tk.NORMAL)
        self.give_up_btn.config(state=tk.NORMAL)
        self.answer_entry.focus_set()

    def _toggle_pause(self):
        """Toggles the game's paused state."""
        if self.mode != "For Time" or self.pause_btn is None:
            return

        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="Resume", bg=self.COLOR_PAUSE_BTN_ACTIVE)
            if self.timer_id:
                self.game_window.after_cancel(self.timer_id)
                self.timer_id = None

            self._disable_input()

            self.question_label.config(text="Game Paused. Press Resume to continue.")
            for label in self.letter_display_labels:
                label.config(text="?", bg="#FFD700")
            self.length_label.config(text="Answer hint hidden.")
        else:
            self.pause_btn.config(text="Pause", bg=self.COLOR_PAUSE_BTN)
            self.start_timer()
            self._enable_input()

            self.question_label.config(text=f"Question: {self.original_question_text}")

            self._display_answer_hint()

    def _end_game(self, message):
        """Ends the game, stops the timer, and displays results."""
        if self.timer_id:
            self.game_window.after_cancel(self.timer_id)
            self.timer_id = None

        self._show_results_frame(message)
        self._save_results()

    def _show_results_frame(self, message):
        """Creates and displays the game results UI."""
        self.game_window.pack_forget()

        self.results_frame = tk.Frame(self.parent, bg=self.COLOR_BG_GAME)
        self.results_frame.pack(fill="both", expand=True)

        tk.Label(self.results_frame, text="Game Over!", font=self.FONT_RESULTS_TITLE, bg=self.COLOR_BG_GAME).pack(
            pady=30)
        tk.Label(self.results_frame, text=message, font=self.FONT_RESULTS_MESSAGE, bg=self.COLOR_BG_GAME).pack(pady=10)

        max_score = 0
        winners = []
        if self.scores:
            max_score = max(self.scores.values())
            for name, score in self.scores.items():
                if score == max_score and max_score > 0:
                    winners.append(name)

        if winners:
            if len(winners) == 1:
                winner_text = f"Winner: {winners[0]}!"
            else:
                winner_text = f"Winners: {', '.join(winners)}!"
            tk.Label(self.results_frame, text=winner_text, font=self.FONT_RESULTS_WINNER, bg=self.COLOR_BG_GAME,
                     fg=self.COLOR_WINNER).pack(pady=15)
        else:
            tk.Label(self.results_frame, text="No winners (all scores were zero or no questions answered).",
                     font=self.FONT_RESULTS_MESSAGE, bg=self.COLOR_BG_GAME).pack(pady=15)

        tk.Label(self.results_frame, text="Final Scores:", font=self.FONT_INFO, bg=self.COLOR_BG_GAME).pack(pady=10)

        for name, score in sorted(self.scores.items(), key=lambda item: item[1], reverse=True):
            tk.Label(self.results_frame, text=f"{name}: {score} points", font=self.FONT_RESULTS_SCORES,
                     bg=self.COLOR_BG_GAME).pack()

        download_pdf_btn = tk.Button(self.results_frame, text="Download Results PDF",
                                     font=self.FONT_BUTTON_GAME,
                                     bg=self.COLOR_SUBMIT_BTN, fg="white",
                                     activebackground=self.COLOR_SUBMIT_BTN_ACTIVE,
                                     command=lambda: generate_game_results_pdf(
                                         self.scores,
                                         self.difficulty,
                                         self.mode
                                     ))
        download_pdf_btn.pack(pady=20)

        back_to_menu_btn = tk.Button(self.results_frame, text="Back to Main Menu",
                                     font=self.FONT_INFO,
                                     bg=self.COLOR_BG_GAME, fg="black",
                                     command=self._return_to_main_menu)
        back_to_menu_btn.pack(pady=40)

    def _return_to_main_menu(self):
        """Cleans up results frame and calls the main menu callback."""
        if self.results_frame:
            self.results_frame.pack_forget()
            self.results_frame.destroy()

        self.questions = []
        self.current_question = None
        self.current_player_index = 0
        self.scores = {}
        self.paused = False
        if self.timer_id:
            self.parent.after_cancel(self.timer_id)
            self.timer_id = None

        if self.on_game_finish_callback:
            self.on_game_finish_callback()

    def _save_results(self):
        """Saves game results to the database."""
        session = Session()
        try:
            max_score = 0
            if self.scores:
                max_score = max(self.scores.values())

            for name, score in self.scores.items():
                player = session.query(Player).filter_by(name=name).first()
                if player:
                    player.games_played += 1
                    if score == max_score and max_score > 0:
                        player.wins += 1
                    else:
                        player.losses += 1

                    game = Game(
                        player_id=player.id,
                        score=score,
                        difficulty=self.difficulty,
                        mode=self.mode
                    )
                    session.add(game)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error saving results: {e}")
            messagebox.showerror("Database Error", f"Failed to save game results: {e}")
        finally:
            session.close()
