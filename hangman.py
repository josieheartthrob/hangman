"""
word is a string at least 3 letters long, completely alphabetical and has no
    more than 6 unique letters, no less than 2 unique characters

visible_letters is a list of letters with the same length as the chosen word and
    each character is either '_' or appears in visible_letters in the same place as
    word
"""

import subprocess
import sys
import prompter
import random

from copy import deepcopy
from collections import OrderedDict
from textwrap import wrap

_CLEAR_WORD = 'cls'
if len(sys.argv) > 1 and sys.argv[1] == '-u':
    _CLEAR_WORD = 'clear'

title = r"""================================================================================

||     ||  ||=\\       ||\    ||    //====||   ||\   /||   ||=\\       ||\    ||
||     ||  ||  \\      ||\\   ||   /|          ||\\ //||   ||  \\      ||\\   ||
||=====||  ||===\\     || \\  ||   ||   ====   || \\/ ||   ||===\\     || \\  ||
||     ||  ||    \\    ||  \\ ||   \|     ||   ||     ||   ||    \\    ||  \\ ||
||     ||  ||     \\   ||   \\||    \\====||   ||     ||   ||     \\   ||   \\||

================================================================================"""

def load_words(filename, sep=' '):
    """Load a random word from word_file

    Preconditions:
        word_file is a string as the name of a text file located in the same
        directory as this module
        has no new lines and contains only unique words as defined in the
        module documentation seperated by 1 space each

    returns a string (word)
    Postcondition
        word is a random word in word_file
    """
    with open(filename) as word_file:
        return word_file.read().split(sep)
words = load_words('words.txt', '\n')

def get_menu(options):
    """Get the string representation of a menu from the specified options

    Assumes options is an ordered dictionary that maps strings (option)
        to strings (name)
        assumes option length + name length + 2 < 20

    Return a string along these lines
        each option must appear in order
    [--------------------]

     [1]           option

     ...              ...

    [--------------------]
    """
    border = '[%s]' % ('-'*20)
    menu = border
    for option, name in options.items():
        space = ' ' * (20 - (len(option) + 2) - len(name))
        menu += '\n\n [%s]%s%s' % (option, space, name)
    menu += '\n\n%s' % border
    return menu

saves = {}
def new_game():
    saves['game'] = Game(random.choice(words))
    return saves['game'].play()

def continue_game():
    return saves['game'].play()

menus = {
    'main': {
        'text': '%s\n\n%s' % (title, get_menu(OrderedDict([
            ('1', 'new game'), ('2', 'exit')]))),
        'options': {'1': new_game, '2': lambda: {}},
        'message': 'Please enter "1" or "2"'},
    
    'continue': {
        'text': '%s\n\n%s' % (title, get_menu(OrderedDict([
            ('1', 'continue'), ('2', 'new game'), ('3', 'exit')]))),
        'options': {'1': continue_game, '2': new_game, '3': lambda: {},
        'message': 'Please enter "1", "2", or "3"'}
    },

    'gameover': {
        'text': '{}\n\n%s' % get_menu(OrderedDict([
            ('1', 'new game'), ('2', 'exit')])),
         'options': {'1': new_game, '2': lambda: {}},
         'message': 'Please enter "1" or "2"'}
}

def main():
    prompter.clear(_CLEAR_WORD)
    menu = menus['main']
    while menu:
        choice = prompter.get_option(menu)
        menu = menu['options'][choice]()
    prompter.clear(_CLEAR_WORD)
    sys.exit()

class Game(object):
    screen = r"""----------------------------------
|__|  /\  |\ | /**  |\/|  /\  |\ |
|  | /--\ | \| \__| |  | /--\ | \|
----------------------------------

o-----------------o
%s
o-----------------o
[ Already Guessed ]
o-----------------o
%s
o-----------------o"""
    label = '| {:%s15} |'
    gameover_text = {
        'win': 'You guessed the word: %s',
        'lose': 'You lose. The word was: %s'}

    def __init__(self, word):
        self.word = word
        self.visible_letters = ['_' for letter in word]
        self.guesses = []
        self.strikes = 0

    def play(self):
        limit = strike_limit(self.word)
        win_condition = 'lose'
        while self.strikes < limit:
            guess = self._get_valid_guess()
            self.guesses.append(guess)
            self.make_guess(guess)
            if not ('_' in self.visible_letters):
                win_condition = 'win'
                break
        gameover_menu = deepcopy(menus['gameover'])
        text = gameover_menu['text'] 
        screen = self.get_gameover_screen(win_condition)
        gameover_menu['text'] = text.format(screen)
        return gameover_menu

    def make_guess(self, guess):
        """Make a guess for the hidden word

        assumes guess is an alphabetical string 1 character long or as long as
        word and it's not in visible_letters. If as long as word, it meets
        precondition of word as defined in the module documentation

        mutates self such that strikes has increased by 1 if the guess was
        incorrect

        mutates visible_letters such that if the guess was correct guess now
        appears in visible_letters where it appears in word
        """
        if guess == self.word:
            self.visible_letters = [letter for letter in self.word]
        elif guess in self.word:
            self.show_letters(guess)
        else:
            self.strikes += 1

    def show_letters(self, guess):
        """Reveal the places where guess appears in word

        Preconditions
        guess - is a string
         * lowercase alphabetical
         * one character long
         * in self.word

        Postconditions
        mutates visible_letters
         * at each index where guess appears in self.word,
           guess now appears in self.visible_letters
        """
        for i, letter in enumerate(self.word):
            if letter == guess:
                self.visible_letters[i] = letter

    def get_screen(self):
        """Get the current screen as a string"""
        vl = ' '.join(self.visible_letters)
        vl = self._get_label(vl, '^')

        guesses = ' '.join(self.guesses)
        guesses = self._get_label(guesses, '<')

        return Game.screen % (vl, guesses)

    def get_gameover_screen(self, state):
        """Get the gameover screen as a string

        assumes state is a string of either 'win' or 'lose'
        """
        gameover_text = Game.gameover_text[state] % self.word
        return '%s\n\n%s' % (self.get_screen(), gameover_text)

    def _get_label(self, text, justification):
        label = Game.label % justification
        lines = ['']
        if text: 
            lines = wrap(text, 15)
        lines = [label.format(line) for line in lines]
        return '\n'.join(lines)

    def _get_valid_guess(self):
        vl = self.visible_letters
        conditions = [
            {'function': lambda data, letters: len(data) in (1, len(letters)),
             'args': [vl],
             'message': (
                 'Your guess must be 1 character or as long as the word')},

            {'function': lambda data: data.isalpha(),
             'message': 'Your guess must only contain alphabetical characters'},

            {'function': lambda data, guesses: data.lower() not in guesses,
             'args': [self.guesses],
             'message': 'You\'ve already guessed that'}]

        prompt = 'Guess a letter or a word'
        guess = prompter.ask_for(self.get_screen(), prompt, conditions,
            clear_word=_CLEAR_WORD)
        return guess.lower()

def strike_limit(word):
    """Get the strike limit for a specific word

    Precondition
    word - is a string
     * contains only alphabetical characters

    Postconditions
    Returns an integer (limit)
     * positive
     * greater than the amount of unique letters in word
     * greater than or equal to 6
     * less than or equal to 26
    """
    return 6

if __name__ == '__main__':
    main()
