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
import textwrap

from pathlib import Path

from pyqttoast import Toast, ToastPreset


from PyQt6.QtWidgets import (QMainWindow, QHBoxLayout, QVBoxLayout, QMessageBox, QLabel,
                             QPushButton, QFrame, QGroupBox, QListWidget, QPlainTextEdit, QComboBox)
from PyQt6.QtCore    import Qt, QTimer, QDateTime
from PyQt6.QtGui     import QBrush, QColorConstants, QTextCursor

import src.classes.menu as mu
import src.classes.fileStore as fs
import src.classes.displayGPX as displayGPX

import src.utils.autoUtils as utils     
import src.utils.gpxParser as gpxParser
import src.utils.dataFrameUtils as dfUtils

from src.projectPaths import DATA_PATH

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

        self.displayGPX     = displayGPX.displayGPX()
        self.dfUtils        = dfUtils.dfUtils()

        self.subDirectories = utils.getDataDirectories()        #  A list of the sub directories under data.
        self.subDirFiles    = {}                                #  A dictionary, each entry will be a list of files for that sub directory.

        #  Build GUI
        self.buildGUI()
        self.buildStatusBar()
        self.setMenuBar(self.myMenu)

        self.insertInfo(f"{self.config.NAME} {self.config.VERSION}.")

        self.fStore = fs.FileStore(self.logger, self)   #  Create the file store.

        self.updateTime()

        self.BuildFileLists()


    def updateValues(self):
        """  Set up run time values from the config file.
             Also called if the config file changes.
        """
        self.Xpos     = self.config.X_POS
        self.Ypos     = self.config.Y_POS
        self.width    = self.config.WIDTH
        self.height   = self.config.HEIGHT
        self.dataPath = f"{DATA_PATH}/data_350"

    def buildGUI(self):
        """  Set up the GUI widgets.
        """
        self.logger.info(" Building GUI.")
        #  Create a central widget.
        centralWidget = QFrame()
        self.setCentralWidget(centralWidget)

        centralLayout = QVBoxLayout()
        ButtonLayout  = QHBoxLayout()

        mainGroup  = QGroupBox("pyklockAuto")
        mainLayout = QVBoxLayout()

        topLayout = QHBoxLayout()
        midLayout = QHBoxLayout()

        self.cbData = QComboBox(self)
        self.cbData.currentTextChanged.connect(self.changeDataPath)
        self.pteInfo = QPlainTextEdit("", self)
        self.lwFileList = QListWidget()
        self.lwFileList.currentItemChanged.connect(self.showInfo)
        self.lwFileList.setMouseTracking(True)

        self.cursor = self.pteInfo.textCursor()
        self.pteInfo.setTextCursor(self.cursor)

        self.cbData.addItems(self.subDirectories)

        topLayout.addWidget(self.cbData)

        midLayout.addWidget(self.pteInfo)
        midLayout.addWidget(self.lwFileList)

        midLayout.setStretchFactor(self.pteInfo, 3)
        midLayout.setStretchFactor(self.lwFileList, 2)

        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(midLayout)

        mainGroup.setLayout(mainLayout)

        self.btnAddNew = QPushButton(text="Add New Files", parent=self)
        self.btnAddAll = QPushButton(text="Clear All Files", parent=self)
        self.btnDisplay = QPushButton(text="Display Route", parent=self)
        btnClose  = QPushButton(text="Close", parent=self)

        self.btnAddNew.clicked.connect(self.addNewFiles)
        self.btnAddNew.setEnabled(False)
        self.btnAddAll.clicked.connect(self.clearAllFiles)
        self.btnAddAll.setEnabled(True)
        self.btnDisplay.clicked.connect(self.displayFile)
        self.btnDisplay.setEnabled(False)
        btnClose.clicked.connect(self.close)

        ButtonLayout.addWidget(self.btnAddNew)
        ButtonLayout.addWidget(self.btnAddAll)
        ButtonLayout.addWidget(self.btnDisplay)
        ButtonLayout.addWidget(btnClose)

        centralLayout.addWidget(mainGroup)
        centralLayout.addLayout(ButtonLayout)

        centralWidget.setLayout(centralLayout)

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
        txtTime   = dtCurrent.toString("HH:mm")
        txtDate   = dtCurrent.toString("dddd dd MMMM yyyy")

        self.stsTime.setText(txtTime)
        self.stsDate.setText(txtDate)
        self.stsState.setText(f"{utils.getState()}")
        self.stsIdle.setText(utils.getIdleDuration())
    # ----------------------------------------------------------------------------------------------------------------------- BuildFileLists() ------
    def BuildFileLists(self):
        """  For each sub directory found [below the data directory.] - add a list of the files to a global dictionary.
             Display files for data_350 initially - should this be the first dictionary entry.
        """
        for sub in self.subDirectories:
            sb = f"{DATA_PATH}/{sub}"
            self.insertInfo(f"Building file list for  {sub}.")
            self.subDirFiles[sub] = utils.listFiles(sb, False)                  #  Set to True to print file names to console.

        self.lwFileList.addItems(self.subDirFiles["data_350"][0])
        self.checkFileList("data_350")
    # ----------------------------------------------------------------------------------------------------------------------- displayFile() ---------
    def displayFile(self):
        """  Display the gpx file as geo map in the browser.
           
             self.dfUtils.gpx2df_elevation returns a pandas dataframe.
               But, an error in returned as a string.
        """
        fileName = self.lwFileList.currentItem().text()
        sub      = f"{self.cbData.currentText()}"
        pos      = self.subDirFiles[sub][0].index(fileName)
        filepath = self.subDirFiles[sub][1][pos]

        df = self.dfUtils.gpx2df_elevation(filepath)

        if isinstance(df, str):
            self.insertInfo(f"{df}.")

        self.displayGPX.displayGPX_elevation(df, self.lwFileList.currentItem().text())
    # ----------------------------------------------------------------------------------------------------------------------- changeDataPath() ------
    def changeDataPath(self):
        """  When the desired data is changed via the combo box, display the required files in the file list.

             Note: This method is first called when the combo bos is populated.
        """
        selected = f"{self.cbData.currentText()}"
        if len(self.subDirFiles) != 0:                              #  If initially called, don't try to access an empty self.subDirFiles.
            self.lwFileList.clear()
            self.lwFileList.addItems(self.subDirFiles[selected][0])
            self.checkFileList(selected)
    # ----------------------------------------------------------------------------------------------------------------------- checkFileList() -------
    def checkFileList(self, sub):
        """  For each file in the displayed file list, check is the file already exists in the file store.
             If the file has been already stored, display in green.
             If the file is new, display in red and add to the file store. 

             The key is the sub directory:file name.
             The Data is the file path.
        """
        newFiles = False
        for item in self.lwFileList.findItems("*", Qt.MatchFlag.MatchWildcard):
            key = f"{sub}:{item.text()}"                                    #  key = sub:fileName
            if self.fStore.hasKey(key):
                item.setForeground(QBrush(QColorConstants.Green)) 
            else:
                item.setForeground(QBrush(QColorConstants.Red)) 
                newFiles = True

        if newFiles:                        #  If new file are found, enable aff new File button.
            self.btnAddNew.setEnabled(True)
        else:
            self.btnAddNew.setEnabled(False)

        self.insertInfo(f"Displaying files for {sub} - {self.lwFileList.count()} files.")

        self.reverseCheck(sub)
     # ----------------------------------------------------------------------------------------------------------------------- reverseCheck() -------
    def reverseCheck(self, sub):
        """  Performs a reverse file check.
             For each item in the filestore, check that the file actually exists.
        """
        self.insertInfo(f"Reverse checking files for {sub}.")

        fileList = self.fStore.storedFiles()
        copyList = list(fileList)

        for key in copyList:                    # iterate over a copy, gets around the error dictionary changed size during iteration
            if key.startswith(sub):
                filePath = Path(self.fStore.getItem(key))
                if not filePath.exists():
                    self.insertInfo(f"ERROR - {filePath}  does not exist.")
                    self.fStore.delItem(key)
                    self.insertInfo(f"ERROR - {filePath}  deleted from File Store.")
    # ----------------------------------------------------------------------------------------------------------------------- addNewFiles() ---------
    def addNewFiles(self):
        """  Adds any new files to the filestore.
        """
        sub= f"{self.cbData.currentText()}"
        for pos, item in enumerate(self.lwFileList.findItems("*", Qt.MatchFlag.MatchWildcard)):
            fname = item.text()
            key   = f"{sub}:{fname}"  
            if not self.fStore.hasKey(key):                                   #  key = sub:fileName
                self.insertInfo(f"Adding {fname}.")
                item.setForeground(QBrush(QColorConstants.Green))     
                filePath = self.subDirFiles[sub][1][pos]                      #  key     :  data
                self.fStore.addItem(key, filePath)                            # addItem(sub:fileName, filepath)

                self.insertInfo(f"Correcting elevation {fname}.")

                error = utils.correctElevation(filePath)

                if error != None:
                    self.insertInfo(f"{error} \n")
                else:
                    self.insertInfo(f"Correcting elevation OK.")

        self.btnAddNew.setEnabled(False)
        self.fStore.save()                                                     #  Save the file store.
    # ----------------------------------------------------------------------------------------------------------------------- addAllFiles() ---------
    def clearAllFiles(self):
        """  Clears the filestore and file list.
        """
        self.fStore.zap()
        self.lwFileList.clear()
        self.BuildFileLists()
    # ----------------------------------------------------------------------------------------------------------------------- addAllFiles() ---------
    def showInfo(self, item):
        """  Displays an info window when a journey is selected on the list.

            gpxParser.parse_gpx_file(filepath) was generated using AI, by Google Antigravity.  
        """
        if item is None:
            return

        toast = Toast(self)
        toast.setDuration(5000) 
        toast.applyPreset(ToastPreset.INFORMATION_DARK)
        toast.setPositionRelativeToWidget(self.lwFileList)
        toast.setMinimumHeight(80)
        toast.setTitle(item.text())

        filename = item.text()
        sub      = f"{self.cbData.currentText()}"
        pos      = self.subDirFiles[sub][0].index(filename)
        filepath = self.subDirFiles[sub][1][pos]
        stats    = gpxParser.parse_gpx_file(filepath)

        info = textwrap.dedent(f"""\
            Date:                   {stats['date']}
            Distance:             {stats['distance_miles']:.2f} miles
            Duration:             {stats['duration_str']}
            Average Speed:  {stats['avg_speed_mph']:.2f} mph
            Top Speed:         {stats['max_speed_mph']:.2f} mph
            Elevation Gain:   {stats['ele_gain_ft']:.1f} fee
            """)
        toast.setText(info)

        toast.show()

        self.btnDisplay.setEnabled(True)
   # ----------------------------------------------------------------------------------------------------------------------- closeEvent() -----------
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
    # ----------------------------------------------------------------------------------------------------------------------- insertInfo() ----------
    def insertInfo(self, message):
        """  Insert the message into the info window [QListWidget], appending an end of line.
             Then moves the cursor to the end, displaying the last line.
        """
        self.pteInfo.insertPlainText(f"{message} \n")
        self.pteInfo.moveCursor(QTextCursor.End)
    # ----------------------------------------------------------------------------------------------------------------------- endBit() --------------
    def endBit(self):
        """  Save config file, stop the timer and print Goodbye.
        """
        self.Timer.stop()           #  Stop the time when the frame closes.
        self.Timer = None           #  Hopefully, stop any memory leaks - maybe only need close()
        self.saveConfig()           #  Save the config file.
        self.fStore.save()          #  Save the file store.
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
