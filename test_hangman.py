import unittest
import testtools
import hangman

from collections import OrderedDict
from copy import deepcopy
from difflib import ndiff

def condition1(guess):
    return len(guess) == 7 or len(guess) == 1

def condition2(guess):
    return guess.isalpha()

def condition3(guess, guesses):
    return guess not in guesses

class TestHangman(unittest.TestCase):
    def test_load_words(self):
        # Partitions
        #     words in file
        #         == 1 [x] | > 1 [x]
        # Coverage
        #     words in file == 1
        #     words in file > 1
        run_tests = testtools.run_function_tests
        function = hangman.load_words
        cases = (
            {'args': ['test_files/words1.txt']},
            {'args': ['test_files/words2.txt']})
        expectedv = (
            ['word'],

            ['unique', 'words', 'over', 'three',
             'letters', 'long', 'file'])

        for result, message in run_tests(function, cases, expectedv):
            self.assertTrue(result, message)

    def test_get_menu(self):
        # Partitions
        #     options size
        #         == 1 [x] | > 1 [x]
        # Coverage
        #     options size == 1
        #     options size > 1
        run_tests = testtools.run_function_tests
        function = hangman.get_menu
        cases = (
            {'args': [OrderedDict([('1', 'option')])]},
            {'args': [OrderedDict([('1', 'option 1'), ('2', 'option 2')])]})
        expectedv = (
            ('[--------------------]\n' +
             '\n' +
             ' [1]           option\n' +
             '\n' +
             '[--------------------]'
            ),
            ('[--------------------]\n' +
             '\n' +
             ' [1]         option 1\n' +
             '\n' +
             ' [2]         option 2\n' +
             '\n' +
             '[--------------------]'))

        for result, message in run_tests(function, cases, expectedv):
            self.assertTrue(result, message)

    def test_make_guess(self):
        # Partitions
        #     guess length
        #         == 1 [x] | == word legth [x]
        #     guess is correct
        #         == true [x] | == false [x]
        #     visible characters
        #         completely '_' [x] | some non-'_' [x]
        #     word length
        #         == 3 [x] | > 3 [ ]
        #     unique letters
        #         == 2 [x] | > 2 & < 6 [x] | == 6 [x]
        #     strikes
        #         == 0 [x] | > 0 [x]
        # Coverage
        #     length == 1 | guess is correct | completely '_' | unique == 2 |
        #         strikes == 0 | length == 3
        #     some non-'_' | 2 < unique < 6 | strikes > 0 | length > 3
        #     length == word length | guess is not correct | unique == 6
        arguments = [{'args': [word]} for word in ('sos', 'hangman', 'abduce')]
        Game = hangman.Game
        attributes = ({},
            {'visible_letters': ['_', 'a', '_', '_', '_', 'a', '_'],
             'strikes': 2},

            {'visible_letters': ['a', 'b', 'd', 'u', 'c', '_'],
             'strikes': 5})

        get_instances = testtools.get_instances
        instances = get_instances(Game, arguments, attributes) 
        method = 'make_guess'
        cases = [{'args': [guess]} for guess in ('s', 'n', 'abduct')]
        targets = (
            {'visible_letters': ['s', '_', 's'],
             'strikes': 0},
            
            {'visible_letters': ['_', 'a', 'n', '_', '_', 'a', 'n'],
             'strikes': 2},
            
            {'visible_letters': ['a', 'b', 'd', 'u', 'c', '_'],
             'strikes': 6})

        run_tests = testtools.run_void_method_tests
        for result, message in run_tests(instances, method, cases, targets):
            self.assertTrue(result, message)

    def test_show_letters(self):
        # Partitions
        #     word length
        #         == 3 [x] | > 3 [x]
        #     guess index
        #         == 0 [x] | > 0 [x] | == word length [x]
        #     guess apperances
        #         == 1 [x] | < word length [x]
        #     visible characters
        #         completely '_' [x] | some non-'_' [ ]
        # Coverage
        #     length == 3 | index == 0 | apperances == 1 | completely '_'
        #     length > 3 | index == length | some non-'_'
        #     index > 0 | apperances < length
        Game = hangman.Game
        words = ('cat', 'dog', 'mississippi')
        arguments = [{'args': [word]} for word in words]
        attributes = (
            {'visible_letters': ['_', '_', '_']},
            {'visible_letters': ['d', '_', '_']},
            {'visible_letters': [
                'm', 'i', '_', '_', 'i', '_', '_', 'i', '_', '_', 'i']})
        
        get_instances = testtools.get_instances
        instances = get_instances(Game, arguments, attributes)
        method = 'show_letters' 
        cases = [{'args': [letter]} for letter in ('c', 'g', 's')]
        targets = (
            {'visible_letters': ['c', '_', '_']},
            {'visible_letters': ['d', '_', 'g']},
            {'visible_letters': [
                'm', 'i', 's', 's', 'i', 's', 's', 'i', '_', '_', 'i']})

        run_tests = testtools.run_void_method_tests
        for result, message in run_tests(instances, method, cases, targets):
            self.assertTrue(result, message)

    def test_get_screen(self):
        # Partitions
        # Coverage
        message = testtools.function_message
        game = hangman.Game('hangman')
        expected = r"""----------------------------------
|__|  /\  |\ | /**  |\/|  /\  |\ |
|  | /--\ | \| \__| |  | /--\ | \|
----------------------------------

o-----------------o
|  _ _ _ _ _ _ _  |
o-----------------o
[ Already Guessed ]
|                 |
o-----------------o"""
        actual = game.get_screen()
        self.assertTrue(expected == actual)

    def test_get_gameover_screen(self):
        # Partitions
        # Coverage
        run_tests = testtools.run_function_tests
        game = hangman.Game('hangman')
        function = game.get_gameover_screen
        screen = r"""----------------------------------
|__|  /\  |\ | /**  |\/|  /\  |\ |
|  | /--\ | \| \__| |  | /--\ | \|
----------------------------------

o-----------------o
|  _ _ _ _ _ _ _  |
o-----------------o
[ Already Guessed ]
|                 |
o-----------------o

"""
        gameover = OrderedDict([
            ('win', 'You guessed the word: hangman'),
            ('lose', 'You lose. The word was: hangman')])
        cases = [{'args': [state]} for state in gameover.keys()]
        expectedv = [screen + text for text in gameover.values()]

        for result, message in run_tests(function, cases, expectedv):
            self.assertTrue(result, message)

if __name__ == '__main__':
    unittest.main()
