###############################################################################################################
#    gpxParser.py   Copyright (C) <2026>  <Kevin Scott>                                                       #
#                                                                                                             #
#    A helper utility to parse GPX xml files and provide route details.               #
#                                                                                                             #
#    This file was generated using AI, by Google Antigravity.                                                 #
#                                                                                                             #
#    21 May 2026 - Added top speed, also by AI.                                                               #
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

import xml.etree.ElementTree as ET
import math
from datetime import datetime
from pathlib import Path

def haversine(lat1, lon1, lat2, lon2):
    """ Calculate the great-circle distance between two points on the Earth (in km).
    """
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def format_duration(seconds):
    """ Format seconds into HH:MM:SS
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def parse_gpx_file(file_path):
    """ Parse GPX file and return parsed trackpoints and journey statistics.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        return {"error": f"Failed to parse GPX: {str(e)}"}

    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"

    pts = root.findall(f".//{ns}trkpt")
    if not pts:
        return {"error": "No track points found in GPX file."}

    trackpoints = []
    total_dist = 0.0
    ele_gain = 0.0
    max_speed = 0.0
    last_lat, last_lon, last_ele, last_time = None, None, None, None
    start_time, end_time = None, None

    for pt in pts:
        try:
            lat = float(pt.attrib["lat"])
            lon = float(pt.attrib["lon"])
        except (KeyError, ValueError):
            continue

        # Time
        time_elem = pt.find(f"{ns}time")
        pt_time = None
        if time_elem is not None and time_elem.text:
            try:
                # replacing Z with +00:00 for python 3.7+ compatibility
                pt_time = datetime.fromisoformat(time_elem.text.replace("Z", "+00:00"))
                if start_time is None:
                    start_time = pt_time
                end_time = pt_time
            except ValueError:
                pass

        # Elevation
        ele_elem = pt.find(f"{ns}ele")
        ele = None
        if ele_elem is not None and ele_elem.text:
            try:
                ele = float(ele_elem.text)
            except ValueError:
                pass

        trackpoints.append((lat, lon))

        if last_lat is not None:
            dist = haversine(last_lat, last_lon, lat, lon)
            total_dist += dist
            if ele is not None and last_ele is not None:
                diff = ele - last_ele
                if diff > 0:
                    ele_gain += diff
            if last_time is not None and pt_time is not None:
                dt = (pt_time - last_time).total_seconds()
                if dt > 0:
                    speed = dist / (dt / 3600.0)
                    # Filter out unrealistic GPS speed spikes (e.g. > 250 km/h)
                    if speed > max_speed and speed < 250.0:
                        max_speed = speed

        last_lat, last_lon, last_ele = lat, lon, ele
        if pt_time is not None:
            last_time = pt_time

    # Calculate stats
    duration_secs = (end_time - start_time).total_seconds() if start_time and end_time else 0
    duration_str = format_duration(duration_secs)
    avg_speed = (total_dist / (duration_secs / 3600.0)) if duration_secs > 0 else 0.0
    
    date_str = start_time.strftime("%d %B %Y") if start_time else "Unknown"

    return {
        "points": trackpoints,
        "filename": Path(file_path).name,
        "date": date_str,
        "distance_km": total_dist,
        "distance_miles": total_dist * 0.621371,
        "duration_secs": duration_secs,
        "duration_str": duration_str,
        "avg_speed_kmh": avg_speed,
        "avg_speed_mph": avg_speed * 0.621371,
        "max_speed_kmh": max_speed,
        "max_speed_mph": max_speed * 0.621371,
        "ele_gain_m": ele_gain,
        "ele_gain_ft": ele_gain * 3.28084
    }
