import os


def getBar(current, total):
    width = int(os.popen('stty size', 'r').read().split()[1]) - 8
    percentage = int((current * 100) // total)
    bar = "";
    barWidth = percentage * width / 100
    for x in range(0, width):
        if x - 1 <= barWidth:
            bar += '#'
        else:
            bar += '-'
    return '[' + bar + "] " + str(percentage if percentage < 99else 100) + "%" + ("\n" if percentage == 100else"")


def printBar(current, total):
    print("\n\033[96m" + getBar(current, total), end='\033[0m\x1b[1A\r\x1b[2K', flush=True)
