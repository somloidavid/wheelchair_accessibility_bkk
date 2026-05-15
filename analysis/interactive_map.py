import sys
import os

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.gtfs_tools import build_gtfs_network
import folium

print("Loading data...")
network = build_gtfs_network()
print(f"Loading complete: {len(network.routes)} routes, {len(network.stops)} stops")

# Collect stops data
accessible_stops = []
inaccessible_stops = []

for stop_id, stop in network.stops.items():
    if stop.wheelchair_boarding is True and stop.lat and stop.lon:
        accessible_stops.append((float(stop.lat), float(stop.lon), stop.name))
    elif stop.wheelchair_boarding is False and stop.lat and stop.lon:
        inaccessible_stops.append((float(stop.lat), float(stop.lon), stop.name))

print(f"Accessible stops with coordinates: {len(accessible_stops)}")
print(f"Non-accessible stops with coordinates: {len(inaccessible_stops)}")

# Calculate center of Budapest
center_lat = sum(lat for lat, lon, name in accessible_stops) / len(accessible_stops)
center_lon = sum(lon for lat, lon, name in accessible_stops) / len(accessible_stops)

# Create map
m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='OpenStreetMap')

# Add accessible stops (green)
for lat, lon, name in accessible_stops:
    folium.CircleMarker(
        location=[lat, lon],
        radius=3,
        color='green',
        fill=True,
        fill_color='#2ecc71',
        fill_opacity=0.7,
        popup=f"Accessible: {name}"
    ).add_to(m)

# Add non-accessible stops (red)
for lat, lon, name in inaccessible_stops:
    folium.CircleMarker(
        location=[lat, lon],
        radius=3,
        color='red',
        fill=True,
        fill_color='#e74c3c',
        fill_opacity=0.7,
        popup=f"Non-Accessible: {name}"
    ).add_to(m)

# Save to HTML file
m.save('budapest_accessibility_map.html')
print("\n✅ Map saved as: budapest_accessibility_map.html")
print("   Double-click the file to open it in your browser!")