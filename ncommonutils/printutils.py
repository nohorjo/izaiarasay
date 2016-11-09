class Text:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GREY = '\033[90m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'

    TURQOISE = '\033[96m'

    CURSOR_UP_ONE = '\x1b[1A'
    CURSOR_DOWN_ONE = '\x1b[1B'
    ERASE_LINE = '\x1b[2K'


def printc(string, selectedColour='\033[0m', end='\n', pre=''):
    try:
        if selectedColour.index("\033") != 0:
            raise ValueError
        print(pre + selectedColour + string + '\033[0m', end=end, flush=True)
    except ValueError:
        printc("Invalid colour: " + selectedColour + "\nUse textColours class", Text.RED)
