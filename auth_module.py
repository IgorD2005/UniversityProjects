import tkinter as tk
from tkinter import messagebox
import random
import string
from databaseLogic import Session, Player
import hashlib
from gameProcess import CrosswordGame

FONT_TITLE_AUTH = ("Lucida Console", 30)
FONT_LABEL_AUTH = ("Lucida Console", 20)
FONT_ENTRY_AUTH = ("Lucida Console", 20)
FONT_BUTTON_AUTH = ("Lucida Console", 20)
FONT_SWITCH_BUTTON = ("Lucida Console", 12)
COLOR_BG_AUTH = "silver"

def hash_password(password):
    """Hashes a given password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

class RegistrationManager:
    """
    Manages player registration/login process for multi-player game setup.
    Handles creation of player input frames and transition to game.
    """
    def __init__(self, parent_window, num_players, difficulty, game_mode, language, on_game_finish_callback):
        self.parent = parent_window
        self.num_players = num_players
        self.difficulty = difficulty
        self.game_mode = game_mode
        self.language = language
        self.on_game_finish_callback = on_game_finish_callback
        self.current_player = 0
        self.players_data = []
        self.frames = []
        self.name_entries = [None] * num_players
        self.pass_entries = [None] * num_players
        self.confirm_entries = [None] * num_players
        self.login_mode = False

        self.container = tk.Frame(self.parent, bg=COLOR_BG_AUTH)
        self.container.pack(fill='both', expand=True)

        self._initialize_player_frames()


    def _initialize_player_frames(self):
        """Creates all player registration/login frames at once."""
        for i in range(self.num_players):
            frame = self._create_player_frame(i, self.container)
            self.frames.append(frame)
        self.show_frame(self.frames[0])

    def generate_guest_name(self):
        """Generates a random guest username."""
        chars = string.ascii_uppercase + string.digits
        return f"Guest_{''.join(random.choice(chars) for _ in range(4))}"

    def show_frame(self, frame):
        """Hides all player frames and shows the specified one."""
        for f in self.frames:
            f.pack_forget()
        frame.pack(in_=self.container, fill='both', expand=True)

    def toggle_mode(self, index):
        """
        Toggles between login and registration mode for the current player.
        Re-creates the current player's frame to reflect the mode change.
        """
        self.login_mode = not self.login_mode
        self.frames[index].destroy()
        self.frames[index] = self._create_player_frame(index, self.container)
        self.show_frame(self.frames[index])

    def next_player(self):
        """
        Processes the current player's input (login/registration).
        Moves to the next player or starts the game if all players are processed.
        """
        session = Session()
        name = self.name_entries[self.current_player].get().strip()
        password = self.pass_entries[self.current_player].get().strip()

        if not name or not password:
            messagebox.showerror("Error", "Please enter both name and password.")
            session.close()
            return

        try:
            if self.login_mode:
                player = session.query(Player).filter_by(name=name).first()
                hashed_password = hash_password(password)
                if not player or player.password != hashed_password:
                    messagebox.showerror("Login Failed", "Invalid username or password.")
                    return
            else:
                confirm = self.confirm_entries[self.current_player].get().strip()
                if password != confirm:
                    messagebox.showerror("Error", "Passwords do not match.")
                    return

                existing = session.query(Player).filter_by(name=name).first()
                if existing:
                    messagebox.showerror("Error", "Username already taken.")
                    return

                hashed_password = hash_password(password)
                player = Player(name=name, password=hashed_password)
                session.add(player)
                session.commit()

            self.players_data.append((name, password))
            self.current_player += 1

            if self.current_player < self.num_players:
                self.show_frame(self.frames[self.current_player])
            else:
                messagebox.showinfo("Registration Complete", f"Players: {', '.join(n for n, _ in self.players_data)}")
                self.finish_registration()

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            session.rollback()
        finally:
            session.close()

    def finish_registration(self):
        """Cleans up registration frames and starts the crossword game."""
        self.container.destroy()

        CrosswordGame(
            self.parent,
            self.players_data,
            self.language,
            self.difficulty,
            self.game_mode,
            self.on_game_finish_callback
        )

    def _create_player_frame(self, i, container):
        """
        Creates a single player registration/login frame.
        This is a helper method, intended for internal use.
        """
        frame = tk.Frame(container, bg=COLOR_BG_AUTH)

        wrapper = tk.Frame(frame, bg=COLOR_BG_AUTH)
        wrapper.place(relx=0.5, rely=0.5, anchor='center')

        title = "Login" if self.login_mode else f"Player {i + 1} Registration"
        tk.Label(wrapper, text=title, font=FONT_TITLE_AUTH, bg=COLOR_BG_AUTH).grid(row=0, column=0, columnspan=2, pady=20)

        tk.Label(wrapper, text="Name:", font=FONT_LABEL_AUTH, bg=COLOR_BG_AUTH).grid(row=1, column=0, sticky='e', padx=10, pady=10)
        name_entry = tk.Entry(wrapper, font=FONT_ENTRY_AUTH, width=20)
        name_entry.insert(0, self.generate_guest_name() if not self.login_mode else "")
        name_entry.grid(row=1, column=1, padx=10, pady=10)
        self.name_entries[i] = name_entry

        tk.Label(wrapper, text="Password:", font=FONT_LABEL_AUTH, bg=COLOR_BG_AUTH).grid(row=2, column=0, sticky='e', padx=10, pady=10)
        pass_entry = tk.Entry(wrapper, font=FONT_ENTRY_AUTH, width=20, show='*')
        pass_entry.grid(row=2, column=1, padx=10, pady=10)
        self.pass_entries[i] = pass_entry

        if not self.login_mode:
            tk.Label(wrapper, text="Confirm:", font=FONT_LABEL_AUTH, bg=COLOR_BG_AUTH).grid(row=3, column=0, sticky='e', padx=10, pady=10)
            confirm_entry = tk.Entry(wrapper, font=FONT_ENTRY_AUTH, width=20, show='*')
            confirm_entry.grid(row=3, column=1, padx=10, pady=10)
            self.confirm_entries[i] = confirm_entry
        else:
            self.confirm_entries[i] = None

        btn_row = 4 if not self.login_mode else 3
        tk.Button(wrapper, text="Next", font=FONT_BUTTON_AUTH, bg=COLOR_BG_AUTH,
                  command=self.next_player).grid(row=btn_row, column=0, columnspan=2, pady=20)

        switch_text = "Already have an account? Login" if not self.login_mode else "Don't have an account? Register"
        tk.Button(wrapper, text=switch_text, font=FONT_SWITCH_BUTTON, bg=COLOR_BG_AUTH,
                  command=lambda: self.toggle_mode(i)).grid(row=btn_row + 1, column=0, columnspan=2)

        return frame

def start_registration(parent, num_players, difficulty, game_mode, language, on_game_finish_callback=None):
    """
    Initializes and starts the player registration/login process.

    Args:
        parent (tk.Frame): The parent Tkinter frame where the registration UI will be placed.
        num_players (int): The number of players to register/login.
        difficulty (str): Game difficulty.
        game_mode (str): Game mode.
        language (str): Language for questions.
        on_game_finish_callback (callable, optional): Callback function to run after game finishes.
    """
    manager = RegistrationManager(parent, num_players, difficulty, game_mode, language, on_game_finish_callback)
    return manager