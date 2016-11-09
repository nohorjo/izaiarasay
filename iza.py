#!/usr/bin/python3

import datetime
import os
import shutil
import subprocess
import time
import sys

from ncommonutils.confutils import getPropertyFromFile
from ncommonutils.progressbar import printBar
from ncommonutils.logger import Log

settingsFile = "/usr/local/etc/izaiarasay/settings.conf"

log = Log("/home/muhammed/Dev/python/izaiarasay/logfile.log")

startTime = time.time()
today = str(datetime.date.today())

listOfFiles = []
backupDirs = []

directories = None
backupLocation = None
backupDriveReserveKBytes = 0

backupKBytes = 0
filecount = 0

try:
    backupLocation = getPropertyFromFile(settingsFile, "backupdir")
    logFile = backupLocation + '/' + today + "/logFile.log"
    log = Log(logFile)
    directories = getPropertyFromFile(settingsFile, "dirtobackup", True)
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
                rtnFilesList.append(fullFile)
            elif os.path.isdir(fullFile):
                rtnFilesList.extend(listFilesRecursively(fullFile))
    except PermissionError:
        log.error("Permission denied for:" + startDir)
    return rtnFilesList


def getLatestBackup(originalFile):
    for backupDir in backupDirs:
        latestBackup = backupLocation + '/' + backupDir + '/' + originalFile
        if os.path.exists(latestBackup):
            return latestBackup
    return None


def backUpFile(fileToBackup):
    try:
        destDir = backupLocation + '/' + today + fileToBackup
        try:
            os.makedirs(destDir[:destDir.rfind('/')])
        except FileExistsError:
            pass
        shutil.copy2(fileToBackup, destDir)
        log.info("Backed up: " + fileToBackup[fileToBackup.rfind('/') + 1:])
    except IOError:
        log.error("Error backing up: " + fileToBackup + "Exception: " + str(sys.exc_info()[0]))


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
    backupKBytes += (os.path.getsize(foundFile) / 1024)

# Check available space
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
os.system('notify-send "Iza: backup complete"')
exit(0)
