###############################################################################################################
#    pyklockAuto   Copyright (C) <2026>  <Kevin Scott>                                                        #
#                                                                                                             #
#    pyklockAuto will [eventually] contain a number of agents that will poll a number of                       #
#        sensors attached to a vehicle [motorbike].                                                           #
#                                                                                                             #
#    The sensors will primarily monitor gps data and log position - but more may be added.                    #
#    To install dependencies pip install -r requirements.txt                                                  #
#                                                                                                             #
#    The main program [this] will collated this dat and display the information from either one               #
#        journey or multiple journeys.                                                                        #
#    The main display is probably on a map.                                                                   #
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

import sys
import platform

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui     import QIcon
from PyQt6.QtCore    import PYQT_VERSION_STR

import src.pyklockAuto as pyklockAuto
import src.config      as Config
import src.logger      as Logger

from src.projectPaths import LOGGER_PATH, CONFIG_PATH, RESOURCE_PATH, FROZEN, STYLE_PATH

def loadQSS(app, myConfig):
    """  Load the global style sheet.

            Style sheet from https://qss-stock.devsecstudio.com/
    """
    fileName = f"{STYLE_PATH}\\{myConfig.STYLE_SHEET}"
    try:
        with open (fileName, "r", encoding="utf-8") as file:
            qss = file.read()
        app.setStyleSheet(qss)
        myLogger.info(f" Using style sheet file {fileName}")
    except FileNotFoundError:
        myLogger.error(f" Style sheet file not found {fileName}")
        print(f" ERROR :: Style sheet file not found {fileName}")

############################################################################################### __main__ ######
if __name__ == "__main__":

    #  Print out any deprecation warnings for functions used in your code
    import warnings
    warnings.simplefilter("default", DeprecationWarning)

    myLogger  = Logger.get_logger(str(LOGGER_PATH))    # Create the logger.

    myLogger.info("-" * 100)

    myConfig  = Config.Config(CONFIG_PATH, myLogger)  # Create the config.

    myLogger.info(f" Running {myConfig.NAME} Version {myConfig.VERSION} ")
    myLogger.debug(f" {platform.uname()}")
    myLogger.debug(f" Python Version {platform.python_version()}  QT Version {PYQT_VERSION_STR}")
    myLogger.debug("")

    if FROZEN:
        myLogger.info("Running as a frozen binary - probably be pyInstaller.")
        #myLogger.info(f"uk.co.keleven.{myConfig.NAME}.{myConfig.VERSION}")

    myLogger.info(f" Config path   {CONFIG_PATH}")
    myLogger.info(f" Logger path   {LOGGER_PATH}")
    myLogger.info(f" Resource path {RESOURCE_PATH}")

    #  So Windows will use the correct icon in the task bar.
    try:
        from ctypes import windll # Only exists on Windows.
        myappid = myConfig.NAME
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    path = f"{RESOURCE_PATH}/tea.ico"
    app.setWindowIcon(QIcon(path))
    
    window = pyklockAuto.mainWindow(myConfig, myLogger)
    
    loadQSS(app, myConfig)

    window.show()

    sys.exit(app.exec())

