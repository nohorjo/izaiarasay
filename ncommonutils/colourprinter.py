class TextColours:
    GREY = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    TURQOISE = '\033[96m'


def printc(string, selectedColour='\033[0m', end='\n'):
    try:
        if selectedColour.index("\033") != 0:
            raise ValueError
        print(selectedColour + string + '\033[0m', end=end)
    except ValueError:
        printc("Invalid colour: " + selectedColour + "\nUse textColours class", TextColours().RED)
