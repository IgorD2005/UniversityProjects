import tkinter as tk
from auth_module import start_registration
from tkinter import messagebox
from databaseLogic import Session, Player
from pdfLogic import generate_players_list_pdf

selected_players = None
selected_difficulty = None
selected_mode = None
selected_language = None

label_players_chosen = None
label_difficulty_chosen = None
label_mode_chosen = None

FONT_TITLE = ("Lucida Console", 70, "bold")
FONT_BUTTON = ("Lucida Console", 35, "bold")
FONT_LABEL_LARGE = ("Lucida Console", 30)
FONT_LABEL_MEDIUM = ("Lucida Console", 20)
FONT_PLAYER_INFO = ("Lucida Console", 18)
FONT_AUTHOR = ("Arial", 19)

COLOR_BG = "silver"
COLOR_FG = "black"
BUTTON_HOVER_BG = '#b0b0b0'
BUTTON_NORMAL_BG = 'silver'

BUTTON_WIDTH = 12
BUTTON_HEIGHT = 1


def on_enter(e):
    """Event handler for button hover (mouse enter)."""
    e.widget['background'] = BUTTON_HOVER_BG


def on_leave(e):
    """Event handler for button hover (mouse leave)."""
    e.widget['background'] = BUTTON_NORMAL_BG

def create_styled_button(parent, text, x, y, command=None):
    """Creates a standardized styled button with hover effects and specific font.

    Args:
        parent (tk.Widget): The parent widget.
        text (str): The text to display on the button.
        x (int): The x-coordinate for placing the button.
        y (int): The y-coordinate for placing the button.
        command (callable, optional): The function to call when the button is clicked.
            Defaults to None.
    Returns:
        tk.Button: The created button widget.
    """
    btn = tk.Button(parent, text=text, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                    background=BUTTON_NORMAL_BG, foreground=COLOR_FG,
                    font=FONT_BUTTON, command=command)
    btn.place(x=x, y=y)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def show_frame(frame_to_show):
    """Hides all frames and shows the specified frame.

    Args:
        frame_to_show (tk.Frame): The frame to display.
    """
    for frame in frames:
        frame.pack_forget()
    frame_to_show.pack(fill='both', expand=True)

def clear_frame(frame):
    """Destroys all widgets within a given frame.

    Args:
        frame (tk.Frame): The frame to clear.
    """
    for widget in frame.winfo_children():
        widget.destroy()

def show_main_menu():
    """Displays the main menu frame."""
    show_frame(main_menu_frame)

def display_error(message):
    """Displays an error message box.

    Args:
        message (str): The error message to display.
    """
    messagebox.showerror(title="Error", message=message)

def select_players_func(num):
    """Updates the selected player count and its display label.

    Args:
        num (int): The number of players selected.
    """
    selected_players.set(num)
    label_players_chosen.config(text=f"{num} player{'s' if num > 1 else ''}")

def select_difficulty_func(diff):
    """Updates the selected difficulty and its display label.

    Args:
        diff (str): The selected difficulty level.
    """
    selected_difficulty.set(diff)
    label_difficulty_chosen.config(text=diff)

def select_mode_func(mode):
    """Updates the selected game mode and its display label.

    Args:
        mode (str): The selected game mode.
    """
    selected_mode.set(mode)
    label_mode_chosen.config(text=mode)


def create_settings_option_section(parent_frame, title_text, y_offset, buttons_data):
    """Creates a section for game settings (players, difficulty, mode).

    Args:
        parent_frame (tk.Frame): The frame to place widgets in.
        title_text (str): Title for the section (e.g., "Choose the amount of players").
        y_offset (int): Vertical position offset for the section.
        buttons_data (list): List of tuples (button_text, command_func, arg).
    """
    tk.Label(parent_frame, text=title_text, font=FONT_LABEL_LARGE, fg=COLOR_FG, bg=COLOR_BG).place(
        x=BUTTON_POS_X_SETT, y=y_offset)

    for i, (text, command, arg) in enumerate(buttons_data):
        create_styled_button(parent_frame, text, x=BUTTON_POS_X_SETT + i * 450, y=y_offset + 80,
                             command=lambda a=arg: command(a))

    tk.Label(parent_frame, text="You've chosen:", font=FONT_LABEL_LARGE, fg=COLOR_FG, bg=COLOR_BG).place(
        x=BUTTON_POS_X_SETT + 1000, y=y_offset)

    global label_players_chosen, label_difficulty_chosen, label_mode_chosen

    if "players" in title_text.lower():
        label_players_chosen = tk.Label(parent_frame, text="Not selected", font=FONT_LABEL_LARGE, fg=COLOR_FG,
                                        bg=COLOR_BG)
        label_players_chosen.place(x=BUTTON_POS_X_SETT + 1350, y=y_offset)
    elif "difficulty" in title_text.lower():
        label_difficulty_chosen = tk.Label(parent_frame, text="Not selected", font=FONT_LABEL_LARGE, fg=COLOR_FG,
                                           bg=COLOR_BG)
        label_difficulty_chosen.place(x=BUTTON_POS_X_SETT + 1350, y=y_offset)
    elif "mode" in title_text.lower():
        label_mode_chosen = tk.Label(parent_frame, text="Not selected", font=FONT_LABEL_LARGE, fg=COLOR_FG, bg=COLOR_BG)
        label_mode_chosen.place(x=BUTTON_POS_X_SETT + 1350, y=y_offset)


def create_game_settings_ui():
    """Initializes/re-creates the game settings UI on the game_frame."""
    global selected_players, selected_difficulty, selected_mode, label_players_chosen, label_difficulty_chosen, label_mode_chosen

    selected_players = tk.IntVar(value=0)
    selected_difficulty = tk.StringVar(value="")
    selected_mode = tk.StringVar(value="")

    create_settings_option_section(
        game_frame, "Choose the amount of players", BUTTON_POS_Y_SETT - 80,
        [("1 player", select_players_func, 1),
         ("2 players", select_players_func, 2),
         ("3 players", select_players_func, 3),
         ("4 players", select_players_func, 4)]
    )

    create_settings_option_section(
        game_frame, "Difficulty", BUTTON_POS_Y_SETT + 130,
        [("Easy", select_difficulty_func, "Easy"),
         ("Medium", select_difficulty_func, "Medium"),
         ("Hard", select_difficulty_func, "Hard")]
    )

    create_settings_option_section(
        game_frame, "Game mode", BUTTON_POS_Y_SETT + 360,
        [("For Time", select_mode_func, "For Time"),
         ("To mistake", select_mode_func, "To mistake")]
    )

    create_styled_button(game_frame, "Back to Menu", x=screen_width - 970, y=screen_height - 160,
                         command=show_main_menu)
    create_styled_button(game_frame, "Next", x=screen_width - 470, y=screen_height - 160,
                         command=lambda: check_ready("You haven't chosen all options"))


def start_game():
    """Handles showing the game settings frame and preparing it for a new game setup."""
    clear_frame(game_frame)
    create_game_settings_ui()
    show_frame(game_frame)


def check_ready(error_message):
    """Checks if all game settings are selected. If so, initiates player registration.

    Args:
        error_message (str): The message to display if settings are incomplete.
    """
    if selected_players.get() > 0 and selected_difficulty.get() and selected_mode.get():
        start_registration(
            game_frame,
            num_players=selected_players.get(),
            difficulty=selected_difficulty.get(),
            game_mode=selected_mode.get(),
            language=selected_language.get(),
            on_game_finish_callback=show_main_menu
        )
    else:
        display_error(error_message)

def settings_menu():
    """Creates and displays the settings window for language selection."""
    window_settings = tk.Toplevel(window)
    window_settings.title("Crossword settings")
    window_settings.configure(bg=COLOR_BG)
    window_settings.geometry("650x650")
    window_settings.resizable(False, False)

    sett_frame = tk.Frame(window_settings, bg=COLOR_BG)
    sett_frame.pack(fill='both', expand=True)

    tk.Label(sett_frame, text="Choose language of questions/\nWybierz język pytań:",
             font=FONT_LABEL_LARGE, bg=COLOR_BG).pack(pady=40)

    def set_language(lang):
        """Sets the selected language and updates the display label.

        Args:
            lang (str): The language code ('pl' or 'en').
        """
        selected_language.set(lang)
        label_chosen_language.config(text=f"Selected: {'Polish' if lang == 'pl' else 'English'}")

    lang_buttons_frame = tk.Frame(sett_frame, bg=COLOR_BG)
    lang_buttons_frame.pack(pady=20)

    tk.Button(lang_buttons_frame, text="Polski", font=FONT_LABEL_MEDIUM,
              command=lambda: set_language("pl"), width=10).grid(row=0, column=0, padx=20)
    tk.Button(lang_buttons_frame, text="English", font=FONT_LABEL_MEDIUM,
              command=lambda: set_language("en"), width=10).grid(row=0, column=1, padx=20)

    label_chosen_language = tk.Label(sett_frame,
                                     text=f"Selected: {'Polish' if selected_language.get() == 'pl' else 'English'}",
                                     font=FONT_LABEL_MEDIUM, bg=COLOR_BG)
    label_chosen_language.pack(pady=20)

    tk.Button(sett_frame, text="Back to Menu", width=12, height=1, background=BUTTON_NORMAL_BG, foreground=COLOR_FG,
              font=FONT_BUTTON, command=window_settings.destroy).place(x=120, y=480)


def show_players():
    """Displays the list of registered players with their statistics."""
    clear_frame(players_frame)

    tk.Label(players_frame, text="Players List", font=("Lucida Console", 40), bg=COLOR_BG).pack(pady=40)

    session = Session()
    players = session.query(Player).all()
    session.close()

    if not players:
        tk.Label(players_frame, text="No players found.", font=FONT_LABEL_MEDIUM, bg=COLOR_BG).pack(pady=20)
    else:
        canvas = tk.Canvas(players_frame, bg=COLOR_BG, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(players_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")


        inner_frame = tk.Frame(canvas, bg=COLOR_BG)
        canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="n")

        def on_canvas_resize(event):
            canvas.itemconfig(canvas_window, width=event.width)
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", on_canvas_resize)

        for p in players:
            info = f"Name: {p.name} | Games Played: {p.games_played} | Wins: {p.wins} | Losses: {p.losses}"
            tk.Label(inner_frame, text=info, font=FONT_PLAYER_INFO, bg=COLOR_BG, anchor="center").pack(pady=5, fill=tk.X, expand=True)

        canvas.config(scrollregion=canvas.bbox("all"))


    create_styled_button(players_frame, "Download Players PDF", 100, screen_height - 250,
                         command=generate_players_list_pdf)

    create_styled_button(players_frame, "Back to Menu", 100, screen_height - 160, command=show_main_menu)
    show_frame(players_frame)


window = tk.Tk()
window.title("Crossword_PROJECT")
window.configure(bg=COLOR_BG)
window.state('zoomed')
window.resizable(False, False)

selected_language = tk.StringVar(value="en")

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
window.geometry(f"{screen_width}x{screen_height}")

frames = []
main_menu_frame = tk.Frame(window, bg=COLOR_BG)
frames.append(main_menu_frame)

players_frame = tk.Frame(window, bg=COLOR_BG)
frames.append(players_frame)

game_frame = tk.Frame(window, bg=COLOR_BG)
frames.append(game_frame)

TITLE_POS_X = 130
TITLE_POS_Y = 60
BUTTON_OFFSET_Y = 125
BUTTON_SPACING_MAIN_MENU = 150

tk.Label(main_menu_frame, text="Crossword", font=FONT_TITLE, fg=COLOR_FG, bg=COLOR_BG).place(x=TITLE_POS_X,
                                                                                             y=TITLE_POS_Y)

create_styled_button(main_menu_frame, "Start game", TITLE_POS_X, TITLE_POS_Y + BUTTON_OFFSET_Y, command=start_game)
create_styled_button(main_menu_frame, "Settings", TITLE_POS_X, TITLE_POS_Y + BUTTON_OFFSET_Y + BUTTON_SPACING_MAIN_MENU,
                     command=settings_menu)
create_styled_button(main_menu_frame, "Players", TITLE_POS_X,
                     TITLE_POS_Y + BUTTON_OFFSET_Y + 2 * BUTTON_SPACING_MAIN_MENU, command=show_players)
create_styled_button(main_menu_frame, "Exit", TITLE_POS_X, TITLE_POS_Y + BUTTON_OFFSET_Y + 3 * BUTTON_SPACING_MAIN_MENU,
                     command=window.destroy)

tk.Label(main_menu_frame, text="Made by Ihar Dziarhai, s30033", font=FONT_AUTHOR, fg="#333333", bg=COLOR_BG).place(
    x=screen_width - 370, y=screen_height - 80)

BUTTON_POS_X_SETT = 100
BUTTON_POS_Y_SETT = 200

show_main_menu()

window.mainloop()