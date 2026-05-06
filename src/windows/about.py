###############################################################################################################
#    About   Copyright (C) <2026>  <Kevin Scott>                                                              #
#                                                                                                             #
#    Displays an about dialog.                                                                                #
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
import platform

from PyQt6.QtWidgets import (QDialog, QGridLayout, QVBoxLayout, QDialogButtonBox, QGroupBox, QLabel,
                             QApplication)
from PyQt6.QtGui     import QPixmap
from PyQt6.QtCore    import Qt, QTimer, PYQT_VERSION_STR

import src.utils.stubUtils as utils

from src.projectPaths import RESOURCE_PATH

class About(QDialog):
    def __init__(self, parent, myConfig, myLogger, startTime):
        super().__init__(parent)

        self.config    = myConfig
        self.logger    = myLogger
        self.startTime = startTime

        height     = 600
        width      = 400
        screenSize = QApplication.primaryScreen().availableGeometry()
        xPos       = int((screenSize.width() / 2)  - (width / 2))
        yPos       = int((screenSize.height() / 2) - (height / 2))

        self.logger.info("Launching About dialog")

        self.setWindowTitle(f"About {self.config.NAME}")
        self.setGeometry(xPos, yPos, width, height)
        self.setFixedSize(width, height)

        layout = QVBoxLayout()

        self.buildTopGroup()
        self.buildMidGroup()
        self.buildBotGroup()

        layout.addWidget(self.topGroup)
        layout.addWidget(self.midGroup)
        layout.addWidget(self.botGroup)

        QBtn = QDialogButtonBox.StandardButton.Ok

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.close)

        layout.addWidget(buttonBox)

        self.setLayout(layout)
        self.update()

        #  Set up timer to update the clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def update(self):
        self.bootTime = utils.getBootTime()
        self.pcUpTime.setText(f" {utils.formatSeconds(self.bootTime)}")
        self.appUpTime.setText(f" {utils.formatSeconds(time.perf_counter() - self.startTime)}")

    def buildTopGroup(self):
        icon = QLabel()
        pixmap = QPixmap(f"{RESOURCE_PATH}/tea.ico")
        icon.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

        title1 = QLabel("pyklockAuto will [eventually] contain a number of agents that will ")
        title2 = QLabel("poll a number of sensors attached to a vehicle [motorbike].")
        name  = QLabel(f"{self.config.NAME}  Version {self.config.VERSION}")
        copy  = QLabel("(c) Kevin Scott 2026")
        email = QLabel("pyklockAuto@keleven.co.uk")
        built = QLabel(f"Built using python {platform.python_version()} and QT {PYQT_VERSION_STR}")

        self.topGroup  = QGroupBox("Application")
        self.topLayout = QVBoxLayout(self.topGroup)
        self.topLayout.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.topLayout.addWidget(icon, Qt.AlignmentFlag.AlignCenter)
        self.topLayout.addWidget(title1)
        self.topLayout.addWidget(title2)
        self.topLayout.addWidget(name)
        self.topLayout.addWidget(copy)
        self.topLayout.addWidget(email)
        self.topLayout.addWidget(built)
        self.topGroup.setLayout(self.topLayout)

    def buildMidGroup(self):
        uname = platform.uname()

        nodeName  = QLabel(f" {uname.node}")
        system    = QLabel(f" {uname.system}  {uname.release}")
        version   = QLabel(f" {uname.version}")
        machine   = QLabel(f" {uname.machine}")
        processor = QLabel(f" {uname.processor}")

        self.midGroup = QGroupBox("Environment")
        self.midLayout = QGridLayout(self.midGroup)
        self.midLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.midLayout.addWidget(QLabel("Node Name :: "), 0, 0, Qt.AlignmentFlag.AlignRight)
        self.midLayout.addWidget(nodeName, 0, 1, Qt.AlignmentFlag.AlignLeft)
        self.midLayout.addWidget(QLabel("OS :: "), 1, 0, Qt.AlignmentFlag.AlignRight)
        self.midLayout.addWidget(system, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self.midLayout.addWidget(QLabel("Version Info :: "), 2, 0, Qt.AlignmentFlag.AlignRight)
        self.midLayout.addWidget(version, 2, 1, Qt.AlignmentFlag.AlignLeft)
        self.midLayout.addWidget(QLabel("Machine Info :: "), 3, 0, Qt.AlignmentFlag.AlignRight)
        self.midLayout.addWidget(machine, 3, 1, Qt.AlignmentFlag.AlignLeft)
        self.midLayout.addWidget(QLabel("Processor :: "), 4, 0, Qt.AlignmentFlag.AlignRight)
        self.midLayout.addWidget(processor, 4, 1, Qt.AlignmentFlag.AlignLeft)
        self.midGroup.setLayout(self.midLayout)

    def buildBotGroup(self):
        self.pcUpTime  = QLabel(" 00:00:00")
        self.appUpTime = QLabel(" 00:00:00")

        self.botGroup = QGroupBox("Running Time")
        self.botLayout = QGridLayout(self.botGroup)
        self.botLayout.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.botLayout.addWidget(QLabel("PC Up Time :"), 0, 0, Qt.AlignmentFlag.AlignRight)
        self.botLayout.addWidget(self.pcUpTime, 0, 1, Qt.AlignmentFlag.AlignLeft)
        self.botLayout.addWidget(QLabel(f"{self.config.NAME} Up Time :"), 1, 0, Qt.AlignmentFlag.AlignRight)
        self.botLayout.addWidget(self.appUpTime, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self.botGroup.setLayout(self.botLayout)

    def closeEvent(self, event):
        self.logger.info("About Close Event")
        self.timer.stop()           #  Stop the time when the frame closes.
        self.timer = None           #  Hopefully, stop any memory leaks - maybe only need close()
        event.accept()


