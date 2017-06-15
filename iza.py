#!/usr/bin/python3

import datetime
import os
import re
import shutil
import subprocess
import sys
import time

from ncommonutils.cliutils import getArg
from ncommonutils.confutils import getPropertyFromFile
from ncommonutils.logger import Log
from ncommonutils.progressbar import printBar

defaultLog = "/home/muhammed/Dev/python/izaiarasay/logFile.log"
log = Log(defaultLog)

settingsFile = getArg("conf", "settings.conf")

startTime = time.time()
today = str(datetime.date.today())

listOfFiles = []
backupDirs = []

directories = None
backupLocation = None
backupDriveReserveKBytes = 0

backupKBytes = 0
filecount = 0

fileExcludePatterns = []
excludedDirs = []

try:
    backupLocation = getPropertyFromFile(settingsFile, "backupdir")
    logFile = backupLocation + '/' + today + "/logFile.log"
    log = Log(logFile)
    directories = getPropertyFromFile(settingsFile, "dirtobackup", True)
    fileExcludePatterns = getPropertyFromFile(settingsFile, "excludefile", True)
    excludedDirs = getPropertyFromFile(settingsFile, "dirtoignore", True)
    backupDriveReserveKBytes = int(getPropertyFromFile(settingsFile, "reservekbytes"))
except FileNotFoundError:
    log.critical("Settings file " + settingsFile + " not found!")
    exit(1)

diskFreeKBytes = int(subprocess.Popen(["df", backupLocation], stdout=subprocess.PIPE).communicate()[0].split()[-3])
diskSpaceKBytes = int(subprocess.Popen(["df", backupLocation], stdout=subprocess.PIPE).communicate()[0].split()[-5])


def listFilesRecursively(startDir):
    rtnFilesList = []

    try:
        files = os.listdir(startDir)

        for file in files:
            fullFile = startDir + "/" + file
            if os.path.isfile(fullFile):
                exclude = False
                for pattern in fileExcludePatterns:
                    if re.match(pattern, file):
                        exclude = True
                        break
                if not exclude:
                    rtnFilesList.append(fullFile)
            elif os.path.isdir(fullFile):
                if fullFile not in excludedDirs and file not in excludedDirs:
                    rtnFilesList.extend(listFilesRecursively(fullFile))
    except PermissionError:
        log.error("Permission denied for:" + startDir)
    except FileNotFoundError:
        log.warn("Directory does not exist. Skipping " + startDir)
    return rtnFilesList


def getLatestBackup(originalFile):
    for backupDir in backupDirs:
        latestBackup = backupLocation + '/' + backupDir + '/' + originalFile
        if os.path.exists(latestBackup):
            return latestBackup
    return None


def backUpFile(fileToBackup):
    try:
        dest = backupLocation + '/' + today + fileToBackup
        try:
            os.makedirs(dest[:dest.rfind('/')])
        except FileExistsError:
            pass
        shutil.copy2(fileToBackup, dest)
        linkdest = backupLocation + '/root' + fileToBackup + "_" + today
        try:
            os.makedirs(linkdest[:linkdest.rfind('/')])
        except FileExistsError:
            pass
        try:
            os.symlink(dest, linkdest)
        except FileExistsError:
            pass
        log.info("Backed up: " + fileToBackup[fileToBackup.rfind('/') + 1:])
    except IOError:
        log.error("Error backing up: " + fileToBackup + " Exception: " + str(sys.exc_info()[1]))


# Getting directories of previous backups
for potentialBackupDir in os.listdir(backupLocation):
    if os.path.isdir(backupLocation + "/" + potentialBackupDir):
        try:
            datetime.datetime.strptime(potentialBackupDir, "%Y-%m-%d")
            backupDirs.append(potentialBackupDir)
        except ValueError:
            log.warn("Ignoring directory:" + potentialBackupDir)

# Sort directories by date descending
backupDirs.sort(key=lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").timestamp(), reverse=True)

# Get list of files to back up
for directory in directories:
    listOfFiles.extend(listFilesRecursively(directory))

# Count the size of the backup
for foundFile in listOfFiles:
    try:
        backupKBytes += (os.path.getsize(foundFile) / 1024)
    except FileNotFoundError:
        pass

# Check available space1
if backupKBytes > diskSpaceKBytes - backupDriveReserveKBytes:
    log.critical(
        "Backups size too big! Remove some items from the backup list or decrease the reserve\nBackup size:" + str(
            backupKBytes) + ", Max: " + str(diskSpaceKBytes - backupDriveReserveKBytes))
    exit(1)

# Make space for the backup
while backupKBytes > diskFreeKBytes - backupDriveReserveKBytes:
    oldestBackup = backupDirs[-1]
    shutil.rmtree(backupLocation + '/' + oldestBackup, True, log.error("Error deleting backup: " + oldestBackup))
    diskFreeKBytes = int(subprocess.Popen(["df", backupLocation], stdout=subprocess.PIPE).communicate()[0].split()[-3])

for foundFile in listOfFiles:
    backedUpFile = getLatestBackup(foundFile)
    if backedUpFile is not None:
        currentMDate = os.path.getmtime(foundFile)
        backupMDate = os.path.getmtime(backedUpFile)
        if currentMDate > backupMDate:
            backUpFile(foundFile)
    else:
        backUpFile(foundFile)
    filecount += 1
    printBar(filecount, len(listOfFiles))

log.ok("\n\nDone! That took " + str(time.time() - startTime)[0:5] + " seconds! File count:" + str(filecount))
log.close()
shutil.copy2(logFile, defaultLog[:defaultLog.rfind('/')])
os.system('notify-send "Iza: backup complete"')
exit(0)
