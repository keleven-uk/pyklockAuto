###############################################################################################################
#    fileStore.py   Copyright (C) <2026>  <Kevin Scott>                                                       #
#                                                                                                             #
#    A class that acts has a wrapper around a dictionary access.                                              #
#    The items to store are data files,                                                                       #
#      The key is made up of the file path [should be unique]                                                 #
#      Data is an empty list for the moment.                                                                  #
#                                                                                                             #
#    Uses pickle or json to load and save the library.                                                        #
#    The format is specified when the library is created.                                                     #
#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2020-2022>  <Kevin Scott>                                                                 #
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

import pickle

import src.timer as timer
import src.projectPaths as pp
import src.Exceptions as myExceptions

class FileStore():
    """  A simple class that wraps the file store dictionary.

         usage:
         self.fStore = fs.FileStore(path)
            The key is the sub directory:file name.
            The Data is the file path.

         to add an item              - self.fStore.addItem(key, data) - Data specific.
         to retrieve an item         - filedata = self.fStore.getItem(key) - Data specific.
         to test for key             - if self.fStore.hasKey(key):
         to return number of items   - l = self.fStore.noOfItems()
         to test database integrity  - self.fStore.check("test") - Data specific.
         to prune database           - self.fStore.check("delete")
         to load items               - self.fStore.load()
         to save items               - self.fStore.save()
         to return a list of keys    = self.fStore.storeFiles()

         TODO - possibly needs error checking [some done, some to go].
    """

    def __init__(self, logger, parent):
        self.fileName = pp.DATA_PATH / "fileStore.pickle"
        self.logger   = logger
        self.parent   = parent
        self.timer    = timer.Timer()                #  A timer class.

        self.__load()

    #---------------------------------------------------------------------------------------------- hasKey(self, key) -----------------------
    def hasKey(self, key):
        """  Returns true if the key exist in the fileStore.
        """
        return key in self.fileStore
    #---------------------------------------------------------------------------------------------- addItem(self, key, item1) -----------------
    def addItem(self, key, data):
        """  Adds to the fileStore 
             The key is the sub directory:file name.
             The Data is the file path.
        """
        self.fileStore[key] = data
    #---------------------------------------------------------------------------------------------- getItem(self, key) -----------------
    def getItem(self, key):
        """  Returns items at position key from the fileStore.
        """
        if self.hasKey(key):
            return self.fileStore[key]
        else:
            raise myExceptions.LibraryError
    #---------------------------------------------------------------------------------------------- getItem(self, key) -----------------
    def setProcessed(self, key):
        """  Mark item as processed.
        """
        if self.hasKey(key):
            self.fileStore[key][0] = True
        else:
            raise myExceptions.LibraryError
    #---------------------------------------------------------------------------------------------- getItem(self, key) -----------------
    def delItem(self, key):
        """  Deletes item at position key from the library.
        """
        try:
            del self.library[key]
        except (KeyError):
            raise myExceptions.LibraryError from None
    #---------------------------------------------------------------------------------------------- storeFiles(self) -----------------
    def storeFiles(self):
        """  Returns a list of the fileStore keys i.e. a list of the files in the store.
        """
        return self.fileStore.keys()
    #---------------------------------------------------------------------------------------------- noOfItems(self) -----------------
    @property
    def noOfItems(self):
        """  Return the number of entries in the fileStore
        """
        if not self.fileStore:
            self.load()
        return len(self.fileStore)
    #---------------------------------------------------------------------------------------------- save(self) -----------------------
    def save(self):
        """  Save the fileStore in pickle format - pickle format.
        """
        with open(self.fileName, "wb") as pickle_file:
            pickle.dump(self.fileStore, pickle_file)
    #---------------------------------------------------------------------------------------------- __load(self) -----------------------
    def __load(self):
        """  Loads the fileStore from disc - pickle format.
        """
        try:
            with open(self.fileName, "rb") as pickle_file:
                self.fileStore = pickle.load(pickle_file)
        except FileNotFoundError:
            self.parent.pteInfo.insertPlainText(f"ERROR :: Cannot find File Store file {self.fileName}.  Will use an empty Store. \n")
            self.fileStore = {}
    #-------------------------------------------------------------------------------- check(self, mode, logger=None) -----------------------
    def check(self, mode, logger=None):
        """  Runs a database data integrity check.

             mode is either "test" of "delete"
             If a logger is passed in, then use it - else ignore.
        """
        self.timer.Start()        #  Start timer.
        missing   = 0
        removed   = 0

        if logger:
            logger.info("-" * 100)

        self.parent.pteInfo.insertPlainText(f"Running database integrity check on {self.fileName} in {mode} mode. \n")
        self.parent.pteInfo.insertPlainText(f"Loading {self.fileName}. \n")

        if not self.fileStore:
            try:
                self.load()
            except FileNotFoundError:
                raise myExceptions.LibraryError from None

        no_files = self.noOfItems
        self.parent.pteInfo.insertPlainText(f"File Store has {no_files} files. \n")

        for filePath in self.fileStore.copy():  # iterate over a copy, gets around the error dictionary changed size during iteration
            path, month, year, fileDate = self.getItem(filePath)

            if not filePath.exists():
                if mode == "delete":
                    self.delItem(filePath)
                    print(f"Deleting {filePath}")
                    removed += 1
                else:
                    missing += 1
                    print(f"File does not exist {filePath}")

        timeStop = self.timer.Stop      #  Stop timer.

        if removed:
            self.parent.pteInfo.insertPlainText(f"Saving {self.fileName}.\n")
            self.save()
            self.parent.pteInfo.insertPlainText(f"Completed  :: {timeStop} and removed {removed} entries from database. \n")
            no_songs = self.noOfItems
            self.parent.pteInfo.insertPlainText(f"File Store has now {no_songs} files. \n")
        else:
            if missing:
                self.parent.pteInfo.insertPlainText(f"Completed  :: {timeStop} and found {missing} missing files. \n")
            else:
                self.parent.pteInfo.insertPlainText(f"Completed  :: {timeStop} and database looks good. \n")
    #-------------------------------------------------------------------------------- zap(self) ------------
    def zap(self):
        self.parent.pteInfo.insertPlainText(f" Deleting File Store {self.fileName}. \n")

        try:
            self.fileName.unlink()
        except FileNotFoundError:
            self.parent.pteInfo.insertPlainText(f" Error deleting {self.fileName} \n")

