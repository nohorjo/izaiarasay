from ncommonutils.printutils import printc
from ncommonutils.printutils import Text

import sys
import os
import atexit


class Log:
    def __init__(self, outFile=""):
        self.save = outFile != ""
        if self.save:
            try:
                try:
                    os.makedirs(outFile[:outFile.rfind('/')])
                except FileExistsError:
                    pass
                self.log = open(outFile, "w")

                def call():
                    printc("Closing logger", Text.TURQOISE)
                    self.log.close()

                atexit.register(call)
            except IOError:
                self.save = False
                self.error("Unable to open outFile: " + outFile + "\n" + sys.exc_info()[0])

    def __save(self, message):
        if self.save:
            self.log.write(message + "\n")

    def out(self, message):
        printc(message)
        self.__save(message)

    def info(self, message):
        printc(message, Text.BLUE)
        self.__save(message)

    def warn(self, message):
        printc(message, Text.YELLOW)
        self.__save(message)

    def ok(self, message):
        printc(message, Text.GREEN)
        self.__save(message)

    def critical(self, message):
        printc(message, Text.RED)
        self.__save(message)

    def debug(self, message):
        printc(message, Text.GREY)
        self.__save(message)

    def error(self, message):
        printc(message, Text.PURPLE)
        self.__save(message)

    def close(self):
        self.log.close()
