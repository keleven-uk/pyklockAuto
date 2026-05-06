###############################################################################################################
#    Settings   Copyright (C) <2026>  <Kevin Scott>                                                           #
#                                                                                                             #
#    Displays an settings dialog.                                                                             #
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
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QTabWidget, QWidget, QFormLayout,
                             QApplication, QLineEdit, QMessageBox)
from PyQt6.QtCore    import Qt


import src.classes.styles as styles


class Page(QWidget):
    def __init__(self):
        super().__init__()

        page_layout = QFormLayout()
        self.setLayout(page_layout)

class Settings(QDialog):
    def __init__(self, parent, myConfig, myLogger):
        super().__init__(parent)

        self.config = myConfig
        self.logger = myLogger
        self.styles = styles.Styles()             #  Styles for QToggle.

        height     = 400
        width      = 460
        screenSize = QApplication.primaryScreen().availableGeometry()
        xPos       = int((screenSize.width() / 2)  - (width / 2))
        yPos       = int((screenSize.height() / 2) - (height / 2))

        self.logger.info("Launching Settings dialog")

        self.setWindowTitle(f"{self.config.NAME} Settings ")
        self.setGeometry(xPos, yPos, width, height)
        self.setFixedSize(width, height)

        self.newSettings      = {}              # a directory to hold amended settings if any.

        layout = QVBoxLayout()

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.clicked.connect(self.buttonClicked)

        self.twTab = QTabWidget()

        funcs = [self.Info]

        for func in funcs:          #  Add the individual tabs.  For a tab to be added - insert title into the list funcs.
            func()

        layout.addWidget(self.twTab)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)
    # ----------------------------------------------------------------------------------------------------------------------- Info() ----------------
    def Info(self):
        """  Display application Info.
             Both name and Version are for display only.
        """
        page   = QWidget(self.twTab)
        layout = QFormLayout()
        layout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        page.setLayout(layout)

        lbName = QLineEdit(self.config.NAME, self)
        lbName.setReadOnly(True)
        lbVersion = QLineEdit(self.config.VERSION, self)
        lbVersion.setReadOnly(True)

        layout.addRow("Name ", lbName)                                 #  Name is read only.
        layout.addRow("Version ", lbVersion)                           #  Version is read only.
    # ----------------------------------------------------------------------------------------------------------------------- buttonClicked() -------
    def buttonClicked(self, button):
        """   Handles the pressed buttons, either Ok or Cancel.
              All button processing, settings saving and validation is handled within this class.

              If Ok is pressed the new settings are written to the config file.
              if Cancel is pressed the form will just close.
                 If amendments have been made, they are lost - prompt the user first.
        """
        role = self.buttonBox.standardButton(button)
        if role == QDialogButtonBox.StandardButton.Cancel:
            if self.newSettings:                        #  Settings have been amended.
                confirmation = QMessageBox.question(self, "Confirmation", "Are you sure you want to close the application?")

                if confirmation == QMessageBox.StandardButton.Yes:
                    self.close()                        #  Close the app, losing any edits.
                else:
                    return                              #  Continue to the app.
            else:                                       #  No settings have been amended.
                self.close()                            #  Close the app.

        elif role == QDialogButtonBox.StandardButton.Ok:
            self.saveSettings()
            self.close()
    # ----------------------------------------------------------------------------------------------------------------------- saveSettings() --------
    def saveSettings(self):
        """  Transfers the new settings dictionary to config values and writes new config file.
        """
        for key, value in self.newSettings.items():
            self.config.__setattr__(key, value)         #  Dirty way of setting the property value using a string.

        self.newSettings = {}                           #  Clear new settings dict
        self.config.writeConfig()                       #  Save new settings.
    # ----------------------------------------------------------------------------------------------------------------------- closeEvent() ----------
    def closeEvent(self, event):
        self.logger.info("Settings Close Event")
        event.accept()


