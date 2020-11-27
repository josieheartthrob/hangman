"""Tools for working with user input from the shell

A condition is a dictionary such that
    must have 'function' key which should be a boolean function that takes
        at least a string as its first argument
    all other keys are optional:
    'args' a list of other arguments the function might need
        defaluts to []
    'kwargs' a dictionary of keyword arguments the function might need
        defaults to {}
    'message' a string to let the user know what went wrong with their input
        defaults to 'invalid input'
"""

import subprocess
import sys

_default_message = 'invalid input'

def clear(clear_word):
    subprocess.call(clear_word, shell=True)

def get_option(menu):
    """Get an menu option from the user

    assumes menu is a dictioinary where the keys 'text' and 'options' are
        mandatory, 'prompt' and 'message' are optional
        default for prompt: ''
        message: 'invalid input'
    assumes 'text', 'prompt', and 'message' map to strings and uses
        'text' for the display screen
        'prompt' to ask the user for input
        'message' to inform the user their input was invalid
    assumes 'options' maps to a collection of strings

    returns a string as the user's choice from options
    """
    condition = {
        'function': lambda data, options: data in options,
        'args': [menu['options']], 'message': menu['message']}
    return ask_for(menu['text'], menu.get('prompt', ''), [condition])


def ask_for(text, prompt, conditions,
            cast=str, cast_message='', clear_word='clear'):
    """Prompt and get valid user input as specified by conditions and cast

    Preconditions
    text and pompt are both strings
    conditions is a list of conditions as defined in
        the module documentation
    cast is an optional built-in type
    cast_message is an optional string
        defaults to 'input must be [a(n)] [type]' where [a(n)] is 'a' if
        the first letter of [type] is a consonant, 'an' otherwise.
        [type] is the string of the built-in type

    returns an object
    Postconditions
        must be same type as cast and must meet all conditions
    """
    error = ''
    while True:
        clear(clear_word)
        data = input(get_screen(text, prompt, error))
        if data == 'quit':
            print('FORCE QUIT')
            sys.exit()

        if not cast_message:
            cast_message = _get_default_cast_message(cast)
        data, error = try_casting(data, cast, cast_message)
        if error: continue

        error = try_meeting_conditions(data, conditions)
        if error: continue
        return data

def get_screen(text, prompt, error):
    """Build the screen from the given arguments

    Preconditions:
        text, error, and prompt are all strings

    returns a string
    Postconditions:
        text is at the beginning of the string
        if error is not an empty string, screen is followed by two newlines
            and error
        screen is followed by two newlines, prompt and ' > '
    """
    screen = text
    if error:
        screen += '\n\n%s' % error
    screen += '\n\n%s > ' % prompt
    return screen

def try_casting(data, cast, message):
    """Try to cast data to the specified type

    Preconditions
        data - string
        cast - built-in type
        message - string

    returns a tuple of an object (data) and a string (error)
    Postconditions
        if data hasn't changed, error isn't an empty string
        else data has changed, error is an empty string
    """
    error = ''
    try:
        data = cast(data)
    except:
        error = message
    return data, error

def try_meeting_conditions(data, conditions):
    """Check to see if data meets the specified conditions

    Preconditions
        data is an object with a primitive type
        conditions is a dictionary as defined in the module documentation

    returns a string
    Postconditions
        if any conditions weren't met, return the message in the condition
        else return an empty string
    """
    for condition in conditions:
        meets_condition = condition['function']
        args = condition.get('args', [])
        kwargs = condition.get('kwargs', {})

        if not meets_condition(data, *args, **kwargs):
            return condition.get('message', _default_message)
    return ''

def _get_default_cast_message(cast):
    cast_str = str(cast).split("'")[1]
    a_or_an = 'a'
    if cast_str[0] in 'aeiou':
        a_or_an = 'an'
    return 'input must be %s %s' % (a_or_an, cast_str)
