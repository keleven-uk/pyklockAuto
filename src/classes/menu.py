###############################################################################################################
#    menu   Copyright (C) <2026>  <Kevin Scott>                                                               #
#                                                                                                             #
#    Constructs the main menu.                                                                                #
#                                                                                                             #
#    For changes see history.txt                                                                              #
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

from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui     import QAction, QIcon
from PyQt6.QtCore    import pyqtSlot

from src.projectPaths import RESOURCE_PATH

import src.windows.about as About
import src.windows.textViewer as tw
import src.windows.helpViewer as hp
import src.windows.settings as stngs


class Menu(QMenuBar):
    """  Constructs the main menu.

         self.myMenu.setVisible(self.menu_bar)  -  Creates the menu object.
         self.myMenu = self.menu.buildMenu()    -  Builds the main menu.

         To add the main menu  - setMenuBar(self.myMenu)  I save a reference, so I can alter the visibility of the menu.
    """

    def __init__(self, myConfig, myLogger, startTime, parent=None):
        super().__init__(parent)

        self.config    = myConfig
        self.logger    = myLogger
        self.parent    = parent
        self.startTime = startTime

        self.buildActions()

    # ----------------------------------------------------------------------------------------------------------------------- buildActions() --------
    def buildActions(self):
        """  Set up menu actions.
        """
        self.logger.info(" Building Menu Actions.")

        path = f"{RESOURCE_PATH}/gear.png"
        self.actSettings = QAction(QIcon(path),f"Configure {self.config.NAME}", self)
        self.actSettings.triggered.connect(self.openSettings)            #  Open the settings window.
        self.actSettings.setCheckable(False)

        path = f"{RESOURCE_PATH}/cross.png"
        self.actClose = QAction(QIcon(path),"Close", self)
        self.actClose.triggered.connect(self.parent.close)                #  Close the app, which call the closeEvent (overridden).
        self.actClose.setCheckable(False)

        self.actHelp = QAction("Help", self)
        self.actHelp.triggered.connect(self.openHelpFile)
        self.actLicence = QAction("Licence", self)
        self.actLicence.triggered.connect(self.openTextFile)
        self.actLogFile = QAction("Log File", self)
        self.actLogFile.triggered.connect(self.openTextFile)
        self.actAbout = QAction("About", self)
        self.actAbout.triggered.connect(self.openAbout)

    # ----------------------------------------------------------------------------------------------------------------------- buildMenu() -----------
    def buildMenu(self):
        # Set up main menu
        self.logger.info(" Building Menu")
        menu = QMenuBar()

        mnuFile = menu.addMenu("&File")
        mnuHelp = menu.addMenu("&Help")


        #  Set up menu actions.
        mnuFile.addAction(self.actSettings)
        mnuFile.addSeparator()
        mnuFile.addAction(self.actClose)

        mnuHelp.addAction(self.actHelp)
        mnuHelp.addSeparator()
        mnuHelp.addAction(self.actLicence)
        mnuHelp.addAction(self.actLogFile)
        mnuHelp.addSeparator()

        mnuHelp.addAction(self.actAbout)

        return menu
    #  ---------------------------------------------------------------------------------------------------------------------- openSettings ----------
    def openSettings(self):
        """  Open an Setting window, which displays the settings available and allows them to be amended.
             All button processing, settings saving and validation is handled within the dialog.

             NB: may need to tell the calling script that the settings have changed.
        """
        dlg = stngs.Settings(self, self.config, self.logger)
        dlg.exec()

        #self.parent.updateValues()
    # ----------------------------------------------------------------------------------------------------------------------- openTextFile ----------
    def openHelpFile(self):
        """  Open a text viewer.
        """
        self.helpWindow = hp.HelpViewer(self, self.config)
        self.helpWindow.show()
    # ----------------------------------------------------------------------------------------------------------------------- openAbout -------------
    def openAbout(self, event):
        """  Open an About window, which display application, system information and run times.
        """
        dlg = About.About(self, self.config, self.logger, self.startTime)
        dlg.exec()
    # ----------------------------------------------------------------------------------------------------------------------- openTextFile ----------
    @pyqtSlot()
    def openTextFile(self):
        """  Open a text viewer.
        """
        action = self.sender()

        self.textWindow = tw.TextViewer(self, action.text(), self.logger, self.config)
        self.textWindow.show()


