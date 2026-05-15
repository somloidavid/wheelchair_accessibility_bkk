import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.gtfs_tools import build_gtfs_network

print("Loading data...")
network = build_gtfs_network()
print(f"Loading complete: {len(network.routes)} routes, {len(network.stops)} stops")

# Analyze stops
accessible_stops = []
inaccessible_stops = []
unknown_stops = []

for stop_id, stop in network.stops.items():
    if stop.wheelchair_boarding is True:
        accessible_stops.append(stop)
    elif stop.wheelchair_boarding is False:
        inaccessible_stops.append(stop)
    else:
        unknown_stops.append(stop)

accessible_count = len(accessible_stops)
inaccessible_count = len(inaccessible_stops)
unknown_count = len(unknown_stops)
total = accessible_count + inaccessible_count + unknown_count

print(f"\nStop Statistics:")
print(f"   Accessible: {accessible_count} ({accessible_count/total*100:.1f}%)")
print(f"   Non-accessible: {inaccessible_count} ({inaccessible_count/total*100:.1f}%)")
print(f"   Unknown: {unknown_count} ({unknown_count/total*100:.1f}%)")

# Chart 1: Pie Chart
fig1, ax1 = plt.subplots(figsize=(10, 8))
labels = ['Accessible', 'Non-Accessible', 'Unknown']
sizes = [accessible_count, inaccessible_count, unknown_count]
colors = ['#2ecc71', '#e74c3c', '#95a5a6']
ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
ax1.set_title('Budapest Public Transport Stop Accessibility', fontsize=14)
plt.savefig('1_stop_accessibility_pie.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Chart 1 saved")

# Chart 2: Grouped Bar Chart (like your screenshot)
route_type_names = {0: "Tram", 1: "Metro", 3: "Bus"}

# Initialize data structure
route_data = {
    "Bus": {'fully': 0, 'partially': 0, 'inaccessible': 0},
    "Tram": {'fully': 0, 'partially': 0, 'inaccessible': 0},
    "Metro": {'fully': 0, 'partially': 0, 'inaccessible': 0}
}

# Analyze each route
for route_id, route in network.routes.items():
    route_type = route.route_type
    if route_type not in route_type_names:
        continue
    
    route_name = route_type_names[route_type]
    
    total_stops = len(route.stops)
    if total_stops == 0:
        continue
    
    accessible_on_route = sum(1 for stop in route.stops if stop.wheelchair_boarding is True)
    ratio = accessible_on_route / total_stops
    
    if ratio == 1.0:
        route_data[route_name]['fully'] += 1
    elif ratio > 0:
        route_data[route_name]['partially'] += 1
    else:
        route_data[route_name]['inaccessible'] += 1

print("\nRoute data collected:")
for mode in ["Bus", "Tram", "Metro"]:
    print(f"   {mode}: Fully={route_data[mode]['fully']}, Partially={route_data[mode]['partially']}, Inaccessible={route_data[mode]['inaccessible']}")

# Create grouped bar chart
fig2, ax2 = plt.subplots(figsize=(10, 7))

modes = ["Bus", "Tram", "Metro"]
x = np.arange(len(modes))
width = 0.25

fully_values = [route_data[m]['fully'] for m in modes]
partially_values = [route_data[m]['partially'] for m in modes]
inaccessible_values = [route_data[m]['inaccessible'] for m in modes]

bars1 = ax2.bar(x - width, fully_values, width, label='Fully Accessible', color='#2ecc71')
bars2 = ax2.bar(x, partially_values, width, label='Partially Accessible', color='#f39c12')
bars3 = ax2.bar(x + width, inaccessible_values, width, label='Inaccessible', color='#e74c3c')

ax2.set_xlabel('Transportation Mode', fontsize=12)
ax2.set_ylabel('Number of Routes', fontsize=12)
ax2.set_title('Accessibility Distribution by Transportation Mode', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(modes)
ax2.legend(loc='upper right', fontsize=10)

# Add value labels
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax2.annotate(f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('2_route_accessibility_bar.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Chart 2 saved: 2_route_accessibility_bar.png")

# Chart 3: Map
fig3, ax3 = plt.subplots(figsize=(14, 12))

acc_lats, acc_lons = [], []
inacc_lats, inacc_lons = [], []

for stop in accessible_stops:
    if stop.lat and stop.lon:
        acc_lats.append(float(stop.lat))
        acc_lons.append(float(stop.lon))

for stop in inaccessible_stops:
    if stop.lat and stop.lon:
        inacc_lats.append(float(stop.lat))
        inacc_lons.append(float(stop.lon))

ax3.scatter(acc_lons, acc_lats, c='#2ecc71', s=15, alpha=0.6, label=f'Accessible ({len(acc_lats)})')
ax3.scatter(inacc_lons, inacc_lats, c='#e74c3c', s=15, alpha=0.6, label=f'Non-Accessible ({len(inacc_lats)})')
ax3.set_xlabel('Longitude')
ax3.set_ylabel('Latitude')
ax3.set_title('Budapest Public Transport Stops Accessibility Map', fontsize=14)
ax3.legend()
ax3.grid(True, alpha=0.3)
plt.savefig('3_accessibility_map.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Chart 3 saved")

# Chart 4: Route Level Summary
route_levels = {'Fully Accessible': 0, 'Partially Accessible': 0, 'Inaccessible': 0}

for route_id, route in network.routes.items():
    route_type = route.route_type
    if route_type not in [0, 1, 3]:
        continue
    
    total_stops = len(route.stops)
    if total_stops == 0:
        continue
    
    accessible_on_route = sum(1 for stop in route.stops if stop.wheelchair_boarding is True)
    ratio = accessible_on_route / total_stops
    
    if ratio == 1.0:
        route_levels['Fully Accessible'] += 1
    elif ratio > 0:
        route_levels['Partially Accessible'] += 1
    else:
        route_levels['Inaccessible'] += 1

fig4, ax4 = plt.subplots(figsize=(10, 6))
categories = list(route_levels.keys())
values = list(route_levels.values())
colors4 = ['#2ecc71', '#f39c12', '#e74c3c']

y_pos = range(len(categories))
ax4.barh(y_pos, values, color=colors4)
ax4.set_yticks(y_pos)
ax4.set_yticklabels(categories)
ax4.set_xlabel('Number of Routes')
ax4.set_title('Route Accessibility Summary')

for i, v in enumerate(values):
    ax4.text(v + 1, i, str(v), va='center')

plt.tight_layout()
plt.savefig('4_route_accessibility_summary.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Chart 4 saved")

# Chart 5: Top 10 Routes
route_accessible_counts = []
for route_id, route in network.routes.items():
    route_type = route.route_type
    if route_type not in [0, 1, 3]:
        continue
    
    accessible_count_on_route = sum(1 for stop in route.stops if stop.wheelchair_boarding is True)
    route_name = route.short_name if route.short_name else route_id
    route_accessible_counts.append({
        'name': route_name,
        'accessible': accessible_count_on_route,
        'total': len(route.stops)
    })

top_routes = sorted(route_accessible_counts, key=lambda x: x['accessible'], reverse=True)[:10]

fig5, ax5 = plt.subplots(figsize=(12, 8))
names = [r['name'] for r in top_routes]
accessible_counts = [r['accessible'] for r in top_routes]
total_counts = [r['total'] for r in top_routes]

x = range(len(names))
width = 0.35

ax5.bar([i - width/2 for i in x], accessible_counts, width, label='Accessible Stops', color='#2ecc71')
ax5.bar([i + width/2 for i in x], total_counts, width, label='Total Stops', color='#3498db')
ax5.set_xlabel('Route Name')
ax5.set_ylabel('Number of Stops')
ax5.set_title('Top 10 Routes with Most Accessible Stops')
ax5.set_xticks(x)
ax5.set_xticklabels(names, rotation=45, ha='right')
ax5.legend()

plt.tight_layout()
plt.savefig('5_top_10_routes.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Chart 5 saved")

# Summary Report
print("\n" + "="*60)
print("BUDAPEST PUBLIC TRANSPORT ACCESSIBILITY REPORT")
print("="*60)
print(f"\nTotal stops: {total}")
print(f"Accessible stops: {accessible_count} ({accessible_count/total*100:.1f}%)")
print(f"Non-accessible stops: {inaccessible_count} ({inaccessible_count/total*100:.1f}%)")

total_routes = sum(route_levels.values())
print(f"\nTotal routes (Tram+Metro+Bus): {total_routes}")
print(f"Fully accessible routes: {route_levels['Fully Accessible']} ({route_levels['Fully Accessible']/total_routes*100:.1f}%)")
print(f"Partially accessible routes: {route_levels['Partially Accessible']} ({route_levels['Partially Accessible']/total_routes*100:.1f}%)")
print(f"Inaccessible routes: {route_levels['Inaccessible']} ({route_levels['Inaccessible']/total_routes*100:.1f}%)")

print("\n" + "="*60)
print("✅ All 5 charts saved!")