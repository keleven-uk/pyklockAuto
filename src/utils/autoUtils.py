###############################################################################################################
#    stubUtils   Copyright (C) <2026>  <Kevin Scott>                                                          #
#                                                                                                             #
#    Contains utility functions for pyStub_PyQt.                                                              #
#                                                                                                             #
#                                                                                                             #
###############################################################################################################
#                                                                                                             #
#    This program is free software: you can redistribute it and/or modify it under the terms of the           #
#    GNU General Public License as published by the Free Software Foundation, either Version 3 of the         #
#    License, or (at your option) any later Version.                                                          #
#                                                                                                             #
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without        #
#    even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#    GNU General Public License for more details.                                                             #
#                                                                                                             #
#    You should have received a copy of the GNU General Public License along with this program.               #
#    If not, see <http://www.gnu.org/licenses/>.                                                              #
#                                                                                                             #
###############################################################################################################

import os

import win32api
import win32con
import ctypes

from src.projectPaths import DATA_PATH
 # ----------------------------------------------------------------------------------------------------------------------- getState() ---------------
def getState():
    """  Checks the current state of Caps Lock, Insert, Scroll Lock & Num Lock.
         The results are returned as a sting.
         A Upper case indicates the lock is on, lower case indicates the lock is off.
    """
    state  = ""
    caps   = win32api.GetKeyState(win32con.VK_CAPITAL)
    insert = win32api.GetKeyState(win32con.VK_INSERT)
    scroll = win32api.GetKeyState(win32con.VK_SCROLL)
    num    = win32api.GetKeyState(win32con.VK_NUMLOCK)

    if caps:
        state = "C"
    else:
        state = "c"

    if insert:
        state += "I"
    else:
        state += "i"

    if scroll:
        state += "S"
    else:
        state += "s"

    if num:
        state += "N"
    else:
        state += "n"

    return state
 # ----------------------------------------------------------------------------------------------------------------------- getIdleDuration() --------
def getIdleDuration():
    """  Returns the number of seconds the PC has been idle.
         Uses the class LASTINPUTINFO above.

         Stolen from -
         http://stackoverflow.com/questions/911856/detecting-idle-time-in-python
    """
    idle = (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0

    if idle > 5:  #  Only print idles time if greater then 5 seconds.
        return f"idle : {formatSeconds(idle)}"
    else:
        return "                "
 # ----------------------------------------------------------------------------------------------------------------------- formatSeconds() ----------
def formatSeconds(secs):
    """  Formats number of seconds into a human readable form i.e. hours:minutes:seconds
    """
    # variable (which stores total time in seconds)
    minutes, seconds  = divmod(secs, 60)
    hours, minutes    = divmod(minutes, 60)
    days, hours       = divmod(hours, 24)

    if days:
        return f"{days:0.0f}d:{hours:02.0f}h:{minutes:02.0f}m:{seconds:02.1f}s"
    elif hours:
        return f"{hours:02.0f}h:{minutes:02.0f}m:{seconds:02.1f}s"
    elif minutes:
        return f"{minutes:02.0f}m:{seconds:02.1f}s"
    else:
        return f"{seconds:02.1f}s"
 # ----------------------------------------------------------------------------------------------------------------------- getBootTime() ------------
def getBootTime():
    """  Returns the number of seconds since system boot up.

         https://www.geeksforgeeks.org/python/getting-the-time-since-os-startup-using-python/
    """
    # getting the library in which GetTickCount64() resides
    lib = ctypes.windll.kernel32

    # calling the function and storing the return value
    t = lib.GetTickCount64()

    # since the time is in milliseconds i.e. 1000 * seconds
    # therefore truncating the value
    t = int(str(t)[:-3])

    # extracting hours, minutes, seconds & days from t
    # variable (which stores total time in seconds)
    mins, sec  = divmod(t, 60)
    hour, mins = divmod(mins, 60)
    days, hour = divmod(hour, 24)

    # formatting the time in readable form
    # (format = x days, HH:MM:SS)
    #print(f"{days} days, {hour:02}:{mins:02}:{sec:02}")

    return (t)
 # ----------------------------------------------------------------------------------------------------------------------- getDataDirectories() -----
def getDataDirectories():
    """  Return a list of sub-directories within the directory od data.
         The special directories .tmp.driveupload is excluded - used my MEGA backup.
    """
    subs = []
    with os.scandir(f"{DATA_PATH}") as dirs:
        for entry in dirs:
            if entry.is_dir() and not entry.name.startswith(".tmp") :
                subs.append(entry.name)

    return subs
 # ----------------------------------------------------------------------------------------------------------------------- listFiles() --------------
def listFiles(dirPath, verbose):
    """  Produce a list of data files in the data directory.
         If screen is True [default], the file name will be printed to screen.
    """
    dataFiles = []
    dirObject = os.scandir(dirPath)

    for entry in dirObject:
        if entry.is_file():
            dataFiles.append(entry.name)
            if verbose:
                print(f"Found data file :: {entry.name}")

    return(dataFiles)