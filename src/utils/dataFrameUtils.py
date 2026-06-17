###############################################################################################################
#    dataFrameUtils.py   Copyright (C) <2026>  <Kevin Scott>                                                  #
#                                                                                                             #
#    A class that acts has a wrapper around data frame utilities.                                             #
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

import gpxpy
import pandas as pd

class dfUtils():
    """  A class that acts has a wrapper around data frame utilities. 
    """

    def __init__(self):
        pass

    def gpx2df_elevation(self, gpxFileName):
        """  Converts a gpx file to a Pandas dataframe.
        """
        try:
            with open(gpxFileName, "r") as gpx_file:
                gpx = gpxpy.parse(gpx_file)
        except FileNotFoundError:
            return(f"The file {gpxFileName} was not found.")
        except IOError:
            return(f"An error occurred while reading the file {gpxFileName}.")

        route_data = []                         #  empty list
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    route_data.append({
                        "latitude" : point.latitude,
                        "longitude": point.longitude,
                        "elevation": point.elevation,
                        "time"     : point.time
                    })

        df = pd.DataFrame(route_data)

        return(df)