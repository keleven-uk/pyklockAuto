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

import numpy as np
import plotly.express as px

class displayGPX():
    """  A class that acts has a wrapper around methods to display dataframes as maps.
    """

    def __init__(self):
        pass

    def _auto_zoom_map(self, df, lat_col, lon_col):
        """  Calculates the center and approximate zoom level for tile maps.
        """
        lats = df[lat_col]
        lons = df[lon_col]
        
        # 1. Find the geographic center
        center = {"lat": lats.mean(), "lon": lons.mean()}
        
        # 2. Calculate the degree span
        lat_range = lats.max() - lats.min()
        lon_range = lons.max() - lons.min()
        max_range = max(lat_range, lon_range)
        
        # 3. Logarithmic conversion from degrees to map zoom levels
        if max_range == 0:
            zoom = 13  # Default zoom if there is only one point
        else:
            # Tweak the subtraction constant (- 1.2) to make the padding tighter or looser
            zoom = np.log2(360 / max_range) 
            
        return zoom, center

    def displayGPX_elevation(self, df, title):
        """  This method uses elevation as the colour map.
             The map will be displayed in the active browser, if not open - will open a browser.
        """
        fig_map = px.line_map(
            df, 
            lat       = "latitude", 
            lon       = "longitude",
            zoom      = 8, 
            map_style = "open-street-map",
            title     = title
        )

        # Calculate and apply the automated bounds
        zoom_level, center_coords = self._auto_zoom_map(df, "latitude", "longitude")

        fig_map.update_layout(
            map=dict(
                center=center_coords, 
                zoom=zoom_level
            )
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