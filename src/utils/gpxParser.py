###############################################################################################################
#    gpxParser.py   Copyright (C) <2026>  <Kevin Scott>                                                       #
#                                                                                                             #
#    A helper utility to parse GPX xml files and generate Leaflet HTML maps for journey routes.               #
#                                                                                                             #
#    This file was generated using AI, by Google Antigravity.                                                 #
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
import json
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
    last_lat, last_lon, last_ele = None, None, None
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
            total_dist += haversine(last_lat, last_lon, lat, lon)
            if ele is not None and last_ele is not None:
                diff = ele - last_ele
                if diff > 0:
                    ele_gain += diff

        last_lat, last_lon, last_ele = lat, lon, ele

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
        "ele_gain_m": ele_gain,
        "ele_gain_ft": ele_gain * 3.28084
    }

def generate_map_html(data, output_path):
    """ Generate leaflet.js map html file for the track.
    """
    points_json = json.dumps(data["points"])
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>pyKlockAuto - Map of {data["filename"]}</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        html, body, #map {{
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .info-panel {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: rgba(30, 30, 30, 0.85);
            backdrop-filter: blur(10px);
            color: #fff;
            padding: 15px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-width: 320px;
        }}
        .info-panel h2 {{
            margin: 0 0 10px 0;
            font-size: 18px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            padding-bottom: 5px;
            color: #4CAF50;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            font-size: 14px;
        }}
        .info-label {{
            color: #aaa;
            margin-right: 15px;
        }}
        .info-value {{
            font-weight: bold;
            text-align: right;
        }}
    </style>
</head>
<body>

<div id="map"></div>

<div class="info-panel">
    <h2>Journey Summary</h2>
    <div class="info-row">
        <span class="info-label">File:</span>
        <span class="info-value">{data["filename"]}</span>
    </div>
    <div class="info-row">
        <span class="info-label">Date:</span>
        <span class="info-value">{data["date"]}</span>
    </div>
    <div class="info-row">
        <span class="info-label">Distance:</span>
        <span class="info-value">{data["distance_km"]:.2f} km ({data["distance_miles"]:.2f} mi)</span>
    </div>
    <div class="info-row">
        <span class="info-label">Duration:</span>
        <span class="info-value">{data["duration_str"]}</span>
    </div>
    <div class="info-row">
        <span class="info-label">Avg Speed:</span>
        <span class="info-value">{data["avg_speed_kmh"]:.2f} km/h ({data["avg_speed_mph"]:.2f} mph)</span>
    </div>
    <div class="info-row">
        <span class="info-label">Elevation Gain:</span>
        <span class="info-value">{data["ele_gain_m"]:.1f} m ({data["ele_gain_ft"]:.1f} ft)</span>
    </div>
</div>

<script>
    const map = L.map('map');

    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 20
    }}).addTo(map);

    const points = {points_json};

    if (points.length > 0) {{
        const polyline = L.polyline(points, {{
            color: '#00e676',
            weight: 5,
            opacity: 0.8,
            lineJoin: 'round'
        }}).addTo(map);

        map.fitBounds(polyline.getBounds());

        // Start Marker (Green)
        L.marker(points[0]).addTo(map)
            .bindPopup('<b>Start Position</b><br>' + points[0][0] + ', ' + points[0][1]);

        // End Marker (Red)
        L.marker(points[points.length - 1]).addTo(map)
            .bindPopup('<b>End Position</b><br>' + points[points.length - 1][0] + ', ' + points[points.length - 1][1]);
    }}
</script>

</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
