"""
Name: Harika Vemulapalli
Course:       CMPS 5113
Assignment:   Program 4 - OPP
Program:      Hangman game
Language:     Python 3 ( uses tkinter)

Purpose
-------
A classic game of Hangman. The computer picks a secret word from the chosen
category and the player tries to guess it one letter at a time. Each wrong
guess draws another part of the hangman. The player wins by revealing every
letter before the drawing is complete (6 wrong guesses).

"""

import random
import string
import tkinter as tk

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
MAX_WRONG = 6  # number of wrong guesses allowed (head, body, 2 arms, 2 legs)

# Word lists by category. Single words only (no spaces).
WORDS = {
    "Animals": ["elephant", "giraffe", "penguin", "dolphin", "kangaroo",
                "cheetah", "octopus", "buffalo", "squirrel", "flamingo"],
    "Computers": ["algorithm", "compiler", "variable", "function", "keyboard",
                  "recursion", "database", "network", "inheritance", "pointer"],
    "Food": ["spaghetti", "pancake", "burrito", "broccoli", "pineapple",
             "sandwich", "chocolate", "avocado", "tortilla", "lasagna"],
    "Texas": ["armadillo", "bluebonnet", "brisket", "wichita", "alamo",
              "rodeo", "longhorn", "houston", "pecan", "mesquite"],
}

# Colors used in the interface
BG = "#f4efe6"
INK = "#2b2b2b"
GOOD = "#2e7d32"
BAD = "#c62828"


class HangmanApp:
    """Main application class: builds the window and holds the game state."""

    def __init__(self, root):
        self.root = root
        root.title("Hangman - CMPS 5113 Program 4")
        root.configure(bg=BG)
        root.resizable(False, False)

        # ---- game state ----
        self.word = ""
        self.guessed = set()
        self.wrong = 0
        self.game_over = False
        self.hint_used = False
        self.wins = 0
        self.losses = 0

        self.category = tk.StringVar(value=list(WORDS.keys())[0])
        self.letter_buttons = {}

        self._build_widgets()
        self.new_game()

    # Interface construction
    def _build_widgets(self):
        """Create and lay out every widget in the window."""
        # Title and a one-line statement of purpose / expectations
        tk.Label(self.root, text="HANGMAN", font=("Helvetica", 24, "bold"),
                 bg=BG, fg=INK).grid(row=0, column=0, columnspan=2, pady=(10, 0))
        tk.Label(self.root,
                 text="Guess the secret word one letter at a time. "
                      "6 wrong guesses and you lose!",
                 font=("Helvetica", 10), bg=BG, fg=INK
                 ).grid(row=1, column=0, columnspan=2, pady=(0, 8))

        # Left side: drawing canvas
        self.canvas = tk.Canvas(self.root, width=240, height=260, bg="white",
                                highlightthickness=1,
                                highlightbackground="#999999")
        self.canvas.grid(row=2, column=0, padx=12, pady=4)

        # Right side: word display, status, tally
        right = tk.Frame(self.root, bg=BG)
        right.grid(row=2, column=1, padx=12, pady=4, sticky="n")

        self.word_label = tk.Label(right, text="", font=("Courier", 24, "bold"),
                                   bg=BG, fg=INK)
        self.word_label.pack(pady=(10, 6))

        self.status_label = tk.Label(right, text="", font=("Helvetica", 12),
                                     bg=BG, fg=INK, wraplength=260,
                                     justify="center")
        self.status_label.pack(pady=4)

        self.lives_label = tk.Label(right, text="", font=("Helvetica", 11),
                                    bg=BG, fg=INK)
        self.lives_label.pack(pady=4)

        self.tally_label = tk.Label(right, text="", font=("Helvetica", 11, "bold"),
                                    bg=BG, fg=INK)
        self.tally_label.pack(pady=(10, 4))

        # Category chooser
        cat_row = tk.Frame(right, bg=BG)
        cat_row.pack(pady=6)
        tk.Label(cat_row, text="Category:", bg=BG, fg=INK).pack(side="left")
        tk.OptionMenu(cat_row, self.category, *WORDS.keys()).pack(side="left", padx=4)

        # Letter buttons A-Z in a grid
        letters = tk.Frame(self.root, bg=BG)
        letters.grid(row=3, column=0, columnspan=2, pady=8)
        for i, ch in enumerate(string.ascii_uppercase):
            btn = tk.Button(letters, text=ch, width=3, font=("Helvetica", 11, "bold"),
                            command=lambda c=ch.lower(): self.guess(c))
            btn.grid(row=i // 9, column=i % 9, padx=2, pady=2)
            self.letter_buttons[ch.lower()] = btn

        # Control buttons: New Game, Hint, Quit
        controls = tk.Frame(self.root, bg=BG)
        controls.grid(row=4, column=0, columnspan=2, pady=(4, 12))
        self.new_btn = tk.Button(controls, text="New Game", width=10,
                                 command=self.new_game)
        self.hint_btn = tk.Button(controls, text="Hint", width=10,
                                  command=self.give_hint)
        self.quit_btn = tk.Button(controls, text="Quit", width=10,
                                  command=self.root.destroy)
        for col, b in enumerate([self.new_btn, self.hint_btn, self.quit_btn]):
            b.grid(row=0, column=col, padx=3)

        # Let the player type letters on the keyboard too
        self.root.bind("<Key>", self._on_key)

    # Game logic
    def new_game(self):
        """Reset state, pick a new secret word, and re-enable all buttons."""
        self.word = random.choice(WORDS[self.category.get()])
        self.guessed = set()
        self.wrong = 0
        self.game_over = False
        self.hint_used = False

        for btn in self.letter_buttons.values():
            btn.config(state="normal")
        self.hint_btn.config(state="normal")
        self.status_label.config(text="Pick a letter to begin!", fg=INK)
        self.refresh()

    def guess(self, letter):
        """Process one guessed letter (ignored if game over or repeated)."""
        if self.game_over or letter in self.guessed:
            return
        self.guessed.add(letter)
        self.letter_buttons[letter].config(state="disabled")

        if letter in self.word:
            self.status_label.config(text=f"Yes! There is a '{letter.upper()}'.",
                                     fg=GOOD)
        else:
            self.wrong += 1
            self.status_label.config(text=f"Sorry, no '{letter.upper()}'.", fg=BAD)
        self.refresh()
        self.check_end()

    def give_hint(self):
        """Reveal one unguessed letter at the cost of one life (once per game)."""
        if self.game_over or self.hint_used:
            return
        remaining = sorted(set(self.word) - self.guessed)
        if not remaining:
            return
        self.hint_used = True
        self.hint_btn.config(state="disabled")
        letter = random.choice(remaining)
        self.guessed.add(letter)
        self.letter_buttons[letter].config(state="disabled")
        self.wrong += 1  # the price of a hint
        self.status_label.config(
            text=f"Hint: the word contains '{letter.upper()}' (cost 1 life).",
            fg=INK)
        self.refresh()
        self.check_end()

    def check_end(self):
        """Detect a win or loss and finish the game accordingly."""
        if self.wrong >= MAX_WRONG:
            self.game_over = True
            self.losses += 1
            self.status_label.config(
                text=f"You lost! The word was '{self.word.upper()}'.", fg=BAD)
            self._disable_all()
        elif all(ch in self.guessed for ch in self.word):
            self.game_over = True
            self.wins += 1
            self.status_label.config(text="You won! Great job!", fg=GOOD)
            self._disable_all()
        self.refresh()

    def _disable_all(self):
        """Disable letter and hint buttons when a game is finished."""
        for btn in self.letter_buttons.values():
            btn.config(state="disabled")
        self.hint_btn.config(state="disabled")


    # Display

    def refresh(self):
        """Redraw the word, lives, tally and hangman drawing."""
        shown = " ".join(ch.upper() if ch in self.guessed or
                         (self.game_over and self.wrong >= MAX_WRONG) else "_"
                         for ch in self.word)
        self.word_label.config(text=shown)
        self.lives_label.config(text=f"Lives left: {MAX_WRONG - self.wrong}")
        self.tally_label.config(text=f"Wins: {self.wins}    Losses: {self.losses}")
        self.draw_hangman()

    def draw_hangman(self):
        """Draw the gallows plus one body part per wrong guess."""
        c = self.canvas
        c.delete("all")
        # Gallows (always visible)
        c.create_line(30, 240, 150, 240, width=4)   # base
        c.create_line(60, 240, 60, 30, width=4)     # pole
        c.create_line(60, 30, 150, 30, width=4)     # beam
        c.create_line(150, 30, 150, 55, width=3)    # rope

        # Body parts, revealed in order as self.wrong increases
        if self.wrong >= 1:
            c.create_oval(130, 55, 170, 95, width=3)               # head
        if self.wrong >= 2:
            c.create_line(150, 95, 150, 160, width=3)              # body
        if self.wrong >= 3:
            c.create_line(150, 110, 120, 140, width=3)             # left arm
        if self.wrong >= 4:
            c.create_line(150, 110, 180, 140, width=3)             # right arm
        if self.wrong >= 5:
            c.create_line(150, 160, 125, 205, width=3)             # left leg
        if self.wrong >= 6:
            c.create_line(150, 160, 175, 205, width=3)             # right leg
            # X eyes for the losing pose
            c.create_text(142, 72, text="x", font=("Helvetica", 10, "bold"))
            c.create_text(158, 72, text="x", font=("Helvetica", 10, "bold"))


    # Dialogs and keyboard

    def _on_key(self, event):
        """Route typed letters to guess()."""
        if event.char and event.char.lower() in self.letter_buttons:
            self.guess(event.char.lower())


def main():
    root = tk.Tk()
    HangmanApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()