###############################################################################################################
#    pyStub_PyQt   Copyright (C) <2026>  <Kevin Scott>                                                        #
#                                                                                                             #
#    A skeleton program for a python GUI application using the GUI framework PyQt6.                           #
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

import time

from PyQt6.QtWidgets import (QMainWindow, QHBoxLayout, QVBoxLayout, QMessageBox, QLabel,
                             QPushButton, QFrame, QGroupBox)
from PyQt6.QtCore    import Qt, QTimer, QDateTime

import src.classes.menu as mu

import src.utils.stubUtils as utils     

class mainWindow(QMainWindow):
    def __init__(self, myConfig, myLogger):
        super().__init__()

        self.startTime = time.perf_counter()

        self.config = myConfig
        self.logger = myLogger

        self.updateValues()

        self.setWindowTitle(self.config.NAME)
        self.setGeometry(self.Xpos, self.Ypos, self.width, self.height)

        self.menu   = mu.Menu(self.config, self.logger, self.startTime, self)
        self.myMenu = self.menu.buildMenu()

        #self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        #self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        #self.setStyleSheet("background : transparent;")

        #  Build GUI
        self.buildGUI()
        self.buildStatusBar()
        self.setMenuBar(self.myMenu)

        self.myMenu.setVisible(True)

        self.updateTime()

    def updateValues(self):
        """  Set up run time values from the config file.
             Also called if the config file changes.
        """
        self.Xpos   = self.config.X_POS
        self.Ypos   = self.config.Y_POS
        self.width  = self.config.WIDTH
        self.height = self.config.HEIGHT

    def buildGUI(self):
        """  Set up the GUI widgets.
        """
        self.logger.info(" Building GUI.")
        #  Create a central widget.
        self.centralWidget = QFrame()
        self.setCentralWidget(self.centralWidget)
        self.centralLayout = QVBoxLayout()
        self.ButtonLayout  = QHBoxLayout()

        self.stubGroup  = QGroupBox("pyklockAuto")
        self.stubLayout = QHBoxLayout()

        #  insert widgets here.

        self.stubGroup.setLayout(self.stubLayout)

        btnClose = QPushButton(text="Close", parent=self)
        btnClose.clicked.connect(self.close)

        self.ButtonLayout.addWidget(btnClose)

        self.centralLayout.addWidget(self.stubGroup)
        self.centralLayout.addLayout(self.ButtonLayout)

        self.centralWidget.setLayout(self.centralLayout)

        #  Set up short timer to update the clock every second
        self.Timer = QTimer(self)
        self.Timer.timeout.connect(self.updateTime)
        self.Timer.start(1000)

    def buildStatusBar(self):
        """  Create a status bar
        """
        self.logger.info(" Building Statusbar.")
        self.statusBar = self.statusBar()
        self.statusBar.setSizeGripEnabled(False)

        self.stsTime  = QLabel("00:00")
        self.stsDate  = QLabel("")
        self.stsState = QLabel("cisN")
        self.stsIdle  = QLabel("")

        self.stsTime.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.stsDate.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.stsState.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stsIdle.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.statusBar.addPermanentWidget(self.stsTime,  1)
        self.statusBar.addPermanentWidget(self.stsDate,  1)
        self.statusBar.addPermanentWidget(self.stsState, 1)
        self.statusBar.addPermanentWidget(self.stsIdle,  1)
    # ----------------------------------------------------------------------------------------------------------------------- updateTime() ----------
    def updateTime(self):
        """  Update the time, info line  and status bar every second.
        """
        dtCurrent = QDateTime.currentDateTime()
        #txtTime   = dtCurrent.toString("HH:mm:ss")
        txtTime   = dtCurrent.toString("HH:mm")
        txtDate = dtCurrent.toString("dddd dd MMMM yyyy")

        self.stsTime.setText(txtTime)
        self.stsDate.setText(txtDate)
        self.stsState.setText(f"{utils.getState()}")
        self.stsIdle.setText(utils.getIdleDuration())
   # ----------------------------------------------------------------------------------------------------------------------- closeEvent() ----------
    def closeEvent(self, event):
        """  Ask for confirmation before closing, if required.

             Save new config properties to file.
        """
        if self.config.CONFIRM_EXIT:
            confirmation = QMessageBox.question(self, "Confirmation", "Are you sure you want to close the application?")

            if confirmation == QMessageBox.StandardButton.Yes:
                self.endBit()
                event.accept()      #  Close the app.
            else:
                event.ignore()      #  Continue the app.
        else:
            self.endBit()
            event.accept()          #  Close the app.
            self.close()
    # ----------------------------------------------------------------------------------------------------------------------- endBit() --------------
    def endBit(self):
        """  Save config file, stop the timer and print Goodbye.
        """
        self.Timer.stop()           #  Stop the time when the frame closes.
        self.Timer = None           #  Hopefully, stop any memory leaks - maybe only need close()
        self.saveConfig()
        self.logger.info(f"  Ending {self.config.NAME} Version {self.config.VERSION} ")
        self.logger.info("=" * 100)
    # ----------------------------------------------------------------------------------------------------------------------- saveConfig() ----------
    def saveConfig(self):
        """  Save stuff to the config file, in case any has changed.
        """
        self.config.X_POS  = self.Xpos
        self.config.Y_POS  = self.Ypos
        self.config.WIDTH  = self.width
        self.config.HEIGHT = self.height
        self.config.writeConfig()
