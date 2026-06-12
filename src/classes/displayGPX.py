###############################################################################################################
#    displayGPX.py.py   Copyright (C) <2026>  <Kevin Scott>                                                   #
#                                                                                                             #
#    A class that acts has a wrapper around methods to display dataframes as maps.                            #
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

import plotly.express as px

class displayGPX():
    """  A class that acts has a wrapper around methods to display dataframes as maps.
    """

    def __init__(self):
        pass

    def displayGPX_elevation(self, df, title):
        """  This method uses elevation as the colour map.
             The map will be displayed on the active browser, if not open - will open a browser.
        """
        fig_map = px.line_map(
            df, 
            lat       = "latitude", 
            lon       = "longitude",
            zoom      = 8, 
            map_style = "open-street-map",
            title     = title
        )

        fig_map.update_traces(
            mode="markers",        # Show both the line and the points
            marker=dict(
                size=6,                  # Adjust point size
                symbol         = "circle",         # Type of point shape
                autocolorscale = False,
                colorscale     = "Rainbow",
                color          = df["elevation"],
                showscale      = True
            )
        )

        fig_map.show()

# `colorscale` may be a palette name string of the
#             following list: Blackbody,Bluered,Blues,Cividis,Earth,E
#             lectric,Greens,Greys,Hot,Jet,Picnic,Portland,Rainbow,Rd
#             Bu,Reds,Viridis,YlGnBu,YlOrRd.