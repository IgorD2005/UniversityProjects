from fpdf import FPDF
from datetime import datetime
from databaseLogic import Session, Player, Game


class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Crossword Game Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def generate_game_results_pdf(players_scores: dict, difficulty: str, mode: str, filename_prefix="game_results"):
    pdf = PDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 15, "Game Summary Report", 0, 1, "C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Difficulty: {difficulty}", 0, 1)
    pdf.cell(0, 8, f"Game Mode: {mode}", 0, 1)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Final Scores:", 0, 1)
    pdf.ln(5)

    max_score = 0
    if players_scores:
        max_score = max(players_scores.values())

    pdf.set_font("Arial", "B", 12)
    col_widths = [60, 40, 50]

    pdf.cell(col_widths[0], 10, "Player Name", 1, 0, "C")
    pdf.cell(col_widths[1], 10, "Score", 1, 0, "C")
    pdf.cell(col_widths[2], 10, "Status", 1, 1, "C")

    pdf.set_font("Arial", "", 12)

    sorted_players = sorted(players_scores.items(), key=lambda item: item[1], reverse=True)

    for name, score in sorted_players:
        status = "Participant"
        if score == max_score and max_score > 0:
            status = "Winner!"
        elif max_score == 0:
            status = "No points"

        pdf.cell(col_widths[0], 10, name, 1, 0, "L")
        pdf.cell(col_widths[1], 10, str(score), 1, 0, "C")
        pdf.cell(col_widths[2], 10, status, 1, 1, "C")


    filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    print(f"Game results PDF generated: {filename}")
    return filename


def generate_players_list_pdf(filename_prefix="players_list"):
    session = Session()
    players = session.query(Player).all()
    session.close()

    pdf = PDF()
    pdf.add_page()


    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 15, "Registered Players List", 0, 1, "C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.ln(10)

    if not players:
        pdf.set_font("Arial", "", 14)
        pdf.cell(0, 10, "No players registered yet.", 0, 1, "C")
    else:
        pdf.set_font("Arial", "B", 10)

        col_widths = [60, 30, 30, 30]

        pdf.cell(col_widths[0], 10, "Name", 1, 0, "C")
        pdf.cell(col_widths[1], 10, "Games", 1, 0, "C")
        pdf.cell(col_widths[2], 10, "Wins", 1, 0, "C")
        pdf.cell(col_widths[3], 10, "Losses", 1, 1, "C")

        pdf.set_font("Arial", "", 10)

        sorted_players = sorted(players, key=lambda p: p.name.lower())

        for p in sorted_players:
            pdf.cell(col_widths[0], 10, p.name, 1, 0, "L")
            pdf.cell(col_widths[1], 10, str(p.games_played), 1, 0, "C")
            pdf.cell(col_widths[2], 10, str(p.wins), 1, 0, "C")
            pdf.cell(col_widths[3], 10, str(p.losses), 1, 1, "C")

    filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    print(f"Players list PDF generated: {filename}")
    return filename