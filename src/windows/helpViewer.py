###############################################################################################################
#    HelpViewer.py    Copyright (C) <2026>  <Kevin Scott>                                                     #
#                                                                                                             #
#    A class that displays a help file in a separate window.                                                  #
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

from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtPdf import QPdfDocument

from src.projectPaths import HELP_PATH


class HelpViewer(QWidget):
    """  A class that displays a help file [in PDF format] in a separate window.
    """
    def __init__(self, parent, myConfig):
        super().__init__()

        self.parent = parent
        self.config = myConfig
        
        self.height     = 800
        self.width      = 800
        self.screenSize = QApplication.primaryScreen().availableGeometry()
        self.xPos       = int((self.screenSize.width() / 2)  - (self.width / 2))
        self.yPos       = int((self.screenSize.height() / 2) - (self.height / 2))

        self.setGeometry(self.xPos, self.yPos, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        self.setWindowTitle(f"{self.config.NAME} Help")

        self.buildGUI()
        self.loadHelpFile()

    def buildGUI(self):
        """  Build the GUI elements.
        """
        self.view    = QPdfView(self)
        self.pdfView = QPdfDocument(self.view)

        btnClose = QPushButton(text="Close", parent=self)
        btnClose.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(btnClose)

        self.setLayout(layout)

    def loadHelpFile(self):
        """  Load the help file.
        """
        path = f"{HELP_PATH}/pyStub_PyQt.pdf"
        self.pdfView = QPdfDocument(None)
        self.pdfView.load(path)

        self.view.setPageMode(QPdfView.PageMode.MultiPage)
        self.view.setDocument(self.pdfView)

    def closeEvent(self, event):
        self.parent.helpWindow = None       #  Set to None in parent, so can open helpViewer again.
        event.accept()
