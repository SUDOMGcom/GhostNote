"""
GhostyQuotes

Normal: 85
Rare: 19
Legendary: 1

Clicking Ghosty has:
- 98.00% chance of a normal quote
- 1.99% chance of a rare quote
- 0.01% chance of the legendary quote

Quotes never repeat immediately.
"""

import random

NORMAL_QUOTES = [
    "Hidden work is still real work.",
    "Every expert has a folder named 'final_final_v7'.",
    "One tiny note today saves an hour tomorrow.",
    "Your future self already appreciates this.",
    "Not all heroes commit directly to main.",
    "Coffee first. Refactoring second.",
    "Behind every smooth day is invisible work.",
    "Bugs fear documentation.",
    "If you fixed it, it happened.",
    "Remember it now, thank yourself later.",
    "Every automation starts as one annoying task.",
    "Your work matters, even when nobody sees it.",
    "Today's tiny fix becomes tomorrow's stability.",
    "Documentation is kindness to Future You.",
    "Future You called. They said 'thanks.'",
    "Great engineers write things down.",
    "Leave clues for Future You.",
    "Every expert was once a beginner.",
    "Kind of sucking at something is the first step to being pretty good at something.",
    "Quiet victories still count.",
    "Capture it before it disappears.",
    "There is no cloud. It's just someone else's computer.",
    "Have you tried turning your memory off and on again?",
    "Your RAM isn't infinite.",
    "Cache this thought before it expires.",
    "Ctrl+S your brain.",
    "Ctrl+Z doesn't work in meetings.",
    "The compiler believes in you.",
    "Semicolons save souls.",
    "Stack Overflow can't remember what you accomplished.",
    "Your logs deserve company.",
    "May your deployments be uneventful.",
    "May your meetings be short.",
    "May your tickets reproduce consistently.",
    "May your merge conflicts be few.",
    "May your coffee remain warm.",
    "May your VPN reconnect quickly.",
    "May your printer remain someone else's problem.",
    "May your DNS always resolve.",
    "May your backups never be tested.",
    "May your scripts run on the first try.",
    "Never trust a 'quick question.'",
    "If it took five seconds, someone probably spent five hours making it that way.",
    "Every solved mystery deserves a note.",
    "Small wins compound.",
    "Every Ghost deserves a story.",
    "Every Note deserves a Ghost.",
    "Leave a little GHOST behind.",
    "Every GHOST has a NOTE to tell.",
    "Don't let your work become a GHOST. Leave a NOTE.",
    "Ghosts fade. GHOSTNOTES don't.",
    "Winter is coming... document everything.",
    "This is the way.",
    "Resistance is futile... but documentation helps.",
    "I aim to misbehave... responsibly.",
    "Live long and automate.",
    "Never tell me the odds... just save the note.",
    "You shall not forget!",
    "There can be only one... latest version.",
    "So say we all.",
    "The companion cube remembers.",
    "Every side quest gives XP.",
    "Achievement unlocked: Remembered.",
    "Side quests count too.",
    "Hidden quests give the best rewards.",
    "Autosave your accomplishments.",
    "Loot acquired: One remembered task.",
    "XP earned.",
    "Grinding counts.",
    "Even NPCs appreciate documentation.",
    "Future meetings love good notes.",
    "You'll be glad you wrote this down.",
    "Tiny notes. Big impact.",
    "Don't underestimate boring work.",
    "Invisible work still moves the world.",
    "Quiet work creates loud results.",
    "Celebrate the little victories.",
    "Practice makes permanent.",
    "Excellence is usually boring.",
    "Good notes outlive good memories.",
    "Automate the boring. Enjoy the interesting.",
    "Every master was once debugging.",
    "Tiny improvements. Every day.",
    "Leave things better than you found them.",
    "The second-best time to document it is now.",
]

RARE_QUOTES = [
    "👻 You found a rare GhostyQuote!",
    "Legend says only 1 in 500 clicks reveal this.",
    "The Ghost in the machine says hello.",
    "You've encountered a shiny Ghosty.",
    "Congratulations! Achievement Unlocked: Curiosity.",
    "You clicked Ghosty instead of doing work... I respect that.",
    "Ghosty has been pretending to work this whole time.",
    "This quote intentionally left undocumented.",
    "You weren't supposed to see this.",
    "There's no achievement for this... or is there?",
    "01001000 01101001. (Hi.)",
    "Be honest... How many times have you clicked me?",
    "I've been waiting for someone curious enough.",
    "Error 404: Productivity not found.",
    "sudo make me a sandwich",
    "Segmentation fault. (Core dumped.) ...just kidding.",
    "Achievement Unlocked: Professional Button Clicker.",
    "This is your sign to drink some water.",
    "Remember to stretch. Future You has a back.",
    "Plot twist: You were the Easter Egg all along.",
]

LEGENDARY_QUOTE = (
    "🌟 Legendary GhostyQuote Found!\n\n"
    "If you're seeing this, congratulations.\n"
    "Either you're incredibly lucky...\n"
    "...or you've clicked Ghosty way too many times.\n\n"
    "Curiosity is rarely wasted.\n"
    "Thanks for being the kind of person who clicks the ghost."
)

NORMAL_CHANCE = 9800
RARE_CHANCE = 199
LEGENDARY_CHANCE = 1

_first_click = True
_last_quote = None

def get_random_quote():
    """Return a GhostyQuote with rarity weighting and no immediate repeats."""
    global _first_click, _last_quote

    if _first_click:
        _first_click = False
        _last_quote = "👻 Thanks for clicking on me."
        return _last_quote

    while True:
        roll = random.randint(1, 10000)

        if roll <= LEGENDARY_CHANCE:
            quote = LEGENDARY_QUOTE
        elif roll <= LEGENDARY_CHANCE + RARE_CHANCE:
            quote = random.choice(RARE_QUOTES)
        else:
            quote = random.choice(NORMAL_QUOTES)

        if quote != _last_quote:
            _last_quote = quote
            return quote