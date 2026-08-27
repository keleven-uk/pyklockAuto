###############################################################################################################
#    dfStore.py   Copyright (C) <2026>  <Kevin Scott>                                                         #
#                                                                                                             #
#    A class that acts has a wrapper around a dictionary access.                                              #
#    The items to store are data files,                                                                       #
#      The key is made up of the file path [should be unique]                                                 #
#      Data is an empty list for the moment.                                                                  #
#                                                                                                             #
#    Uses pickle to load and save the library.                                                                #
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

import pickle

import src.projectPaths as pp

import pandas as pd

class dfStore():
    """  A simple class that wraps the file store dictionary.

         usage:
         self.dfStore = fs.FileStore(path)

         to add an item - self.fStore.add(df) .

         TODO - possibly needs error checking [some done, some to go].
    """

    def __init__(self, logger, sub, parent):
        self.logger = logger
        self.sub    = sub
        self.parent = parent

        self.storeName = pp.DATA_PATH / f"dfStore_{self.sub}.pickle"

        self.__load()

    #------------------------------------------------------------------------------------------------------------- add(self) ------------------------
    def add(self, df):
        """  Add a single data frame to the dfStore.
        """
        self.dfData = pd.concat([self.dfData, df])
    #------------------------------------------------------------------------------------------------------------- save(self) -----------------------
    def save(self):
        """  Save the dfStore in pickle format - pickle format.
        """
        with open(self.storeName, "wb") as pickle_file:
            pickle.dump(self.dfData, pickle_file)
    #----------------------------------------------------------------------------------------------------------- __load(self) -----------------------
    def __load(self):
        """  Attempt to load the dfStore, if not create a new empty one.
        """
        try:
            self.dfData = pd.read_pickle(self.storeName)                #  Load data store, if it exists.
        except (FileNotFoundError, EOFError):
            self.parent.insertInfo(f"ERROR :: Cannot find df Store file {self.storeName}.\n  Will use an empty Store.")
            self.dfData = pd.DataFrame()                                #  Create the data Pandas Dataframe.
    #-------------------------------------------------------------------------------- zap(self) ------------
    def zap(self):
        """  Clears the file store and deletes the physical file.
             Prompts the user first.
        """
        try:
            self.storeName.unlink()
            self.dfData = pd.DataFrame() 
            self.parent.insertInfo(f" Deleted {self.storeName}.")
        except FileNotFoundError:
            self.parent.insertInfo(f" Error deleting {self.storeName}.")