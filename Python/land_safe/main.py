import math
import folium
import webbrowser
from geopy.distance import geodesic
import requests
import random
from dotenv import load_dotenv
import os

load_dotenv()
# Aircraft-specific parameters
GLIDE_SLOPE = 22  # Glide slope ratio (horizontal:vertical)
STALL_SPEED = 21  # m/s
MAX_WIND_CRUISE = 14  # m/s
OPTIMAL_APPROACH_SPEED = 24  # m/s

# Replace with your Google Maps API Key
API_KEY = os.getenv("GOOGLE_API_KEY")

def fetch_elevation(lat, lon):
    """Fetch elevation data for a given latitude and longitude using Google Maps API."""
    if not API_KEY:
        raise ValueError("Google Maps API Key is missing or invalid. Please provide a valid API key.")
    url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={lat},{lon}&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            elevation = data["results"][0]["elevation"]
            return elevation
        else:
            print(f"Error in response: {data['status']}")
            return None
    else:
        print(f"HTTP error: {response.status_code}")
        return None

def fetch_terrain_data(center_lat, center_lon, radius_km, num_points=20):
    """
    Generate terrain data (elevation) for random points within a radius using Google Maps Elevation API.
    Each terrain grid size is calculated based on the aircraft dimensions with a 25% buffer.
    """
    # Aircraft dimensions with 25% buffer
    grid_length = 7.2 / 111000  # Length in degrees (~111 km per degree latitude)
    grid_width = 4.06 / 111000  # Width in degrees (~111 km per degree latitude)

    terrain_data = []
    for _ in range(num_points):
        # Generate random latitude and longitude offsets within the radius
        lat_offset = random.uniform(-radius_km / 111, radius_km / 111)  # 1 degree lat ~ 111 km
        lon_offset = random.uniform(-radius_km / 111, radius_km / 111)
        point_lat = center_lat + lat_offset
        point_lon = center_lon + lon_offset

        # Fetch elevation data for the grid center
        elevation = fetch_elevation(point_lat, point_lon)
        if elevation is not None:
            terrain_data.append({
                "location": (point_lat, point_lon),
                "elevation": elevation,
                "grid_size": (grid_length * 111000, grid_width * 111000),  # Grid size in meters
                "population": random.uniform(0, 1),
                "infrastructure": random.uniform(0, 1),
                "trees": random.uniform(0, 1),
                "wind_speed": random.uniform(5, 20),
                "terrain_flatness": random.uniform(0.5, 1.0)
            })
    return terrain_data

def calculate_distance(point1, point2):
    """Calculate geodesic distance in meters."""
    return geodesic(point1, point2).meters

def calculate_turn_angle(current_heading, target_location, current_location):
    """Calculate turn angle to a target location."""
    lat1, lon1 = current_location
    lat2, lon2 = target_location

    # Calculate bearing to the target
    bearing = math.degrees(math.atan2(
        math.sin(math.radians(lon2 - lon1)) * math.cos(math.radians(lat2)),
        math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) -
        math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(lon2 - lon1))
    ))

    # Calculate turn angle
    turn_angle = abs(current_heading - bearing) % 360
    if turn_angle > 180:
        turn_angle = 360 - turn_angle
    return turn_angle

def calculate_safety_score(zone, turn_angle, glide_distance, max_glide_distance, weights):
    """Calculate the safety score for a landing zone."""
    if zone["wind_speed"] > MAX_WIND_CRUISE:  # Exclude zones with unsafe wind speeds
        return float("inf")
    
    # Safety criteria
    safety_score = (
        zone["population"] * weights["population"] +
        zone["infrastructure"] * weights["infrastructure"] +
        zone["trees"] * weights["trees"] +
        ((1 - zone["terrain_flatness"]) * weights["flatness"])
    )

    # Turn penalty
    turn_penalty = (1 - math.cos(math.radians(turn_angle))) * weights["turn"]

    # Glide feasibility
    glide_penalty = max(0, (glide_distance - max_glide_distance) / max_glide_distance) * weights["glide"]

    # Combine scores
    total_score = safety_score + turn_penalty + glide_penalty
    return total_score

def find_landing_zone(center_lat, center_lon, current_heading, altitude, radius_km, num_points, weights):
    """Find the best landing zone using Google terrain data."""
    zones = fetch_terrain_data(center_lat, center_lon, radius_km, num_points)
    max_glide_distance = altitude * GLIDE_SLOPE

    candidates = []
    for zone in zones:
        distance = calculate_distance((center_lat, center_lon), zone["location"])
        if distance <= max_glide_distance:
            turn_angle = calculate_turn_angle(current_heading, zone["location"], (center_lat, center_lon))
            score = calculate_safety_score(zone, turn_angle, distance, max_glide_distance, weights)
            candidates.append({"zone": zone, "distance": distance, "turn_angle": turn_angle, "score": score})

    # Sort by score
    candidates.sort(key=lambda x: x["score"])
    return candidates

def visualize_landing_zones_on_map(center_lat, center_lon, candidates):
    """Visualize the landing zones on an interactive map using Folium."""
    # Initialize the map at the current location
    landing_map = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # Mark the current location
    folium.Marker(
        location=[center_lat, center_lon],
        popup="Current Location",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(landing_map)

    # Add candidate landing zones
    for idx, candidate in enumerate(candidates):
        zone = candidate["zone"]
        lat, lon = zone["location"]
        score = candidate["score"]

        # Determine marker color
        marker_color = "green" if idx == 0 else "blue"

        # Add a marker for each candidate
        folium.Marker(
            location=[lat, lon],
            popup=f"Candidate #{idx + 1}\nScore: {score:.2f}\nElevation: {zone['elevation']:.2f} m",
            icon=folium.Icon(color=marker_color, icon="cloud"),
        ).add_to(landing_map)

    # Return the map object
    return landing_map

def visualize_terrain_grid_on_map(center_lat, center_lon, terrain_data, first_candidate):
    """Visualize the terrain grid with buffer zones and line to the first candidate on an interactive map."""
    # Initialize the map
    terrain_map = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # Plot the current location
    folium.Marker(
        location=[center_lat, center_lon],
        popup="Current Location",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(terrain_map)

    # Plot terrain grids with buffer
    for zone in terrain_data:
        lat, lon = zone["location"]
        grid_length, grid_width = zone["grid_size"]
        folium.Rectangle(
            bounds=[
                [lat - grid_length / 2 / 111000, lon - grid_width / 2 / 111000],
                [lat + grid_length / 2 / 111000, lon + grid_width / 2 / 111000],
            ],
            color="blue",
            fill=True,
            fill_opacity=0.3,
            popup=f"Elevation: {zone['elevation']} m",
        ).add_to(terrain_map)

    # Add the first candidate (best landing zone)
    best_lat, best_lon = first_candidate["zone"]["location"]
    folium.Marker(
        location=[best_lat, best_lon],
        popup=f"Best Landing Zone\nElevation: {first_candidate['zone']['elevation']} m\nScore: {first_candidate['score']:.2f}",
        icon=folium.Icon(color="green", icon="ok-sign"),
    ).add_to(terrain_map)

    # Draw a line from current location to the first candidate
    distance = calculate_distance((center_lat, center_lon), (best_lat, best_lon))
    folium.PolyLine(
        locations=[(center_lat, center_lon), (best_lat, best_lon)],
        color="purple",
        weight=2.5,
        opacity=1,
        popup=f"Distance: {distance:.2f} meters",
    ).add_to(terrain_map)

    # Add a label for the distance
    folium.Marker(
        location=[
            (center_lat + best_lat) / 2, 
            (center_lon + best_lon) / 2
        ],
        icon=folium.DivIcon(
            html=f'<div style="font-size: 12px; color: purple;">{distance:.2f} meters</div>'
        ),
    ).add_to(terrain_map)

    # Return the map object
    return terrain_map

# Main demo
if __name__ == "__main__":
    # Input parameters
    current_lat = -33.668362
    current_lon = 150.850820
    radius_km = 3  # 3 km search radius
    num_points = 10  # Number of terrain points

    # Fetch terrain data with grid size based on aircraft dimensions
    terrain_data = fetch_terrain_data(current_lat, current_lon, radius_km, num_points)

    # Find the best candidate
    weights = {
        "population": 0.4,
        "infrastructure": 0.3,
        "trees": 0.2,
        "flatness": 0.1,
        "turn": 0.05,
        "glide": 0.05,
    }
    candidates = find_landing_zone(current_lat, current_lon, 90, 122, radius_km, num_points, weights)
    first_candidate = candidates[0]

    # Visualize terrain grid on map
    terrain_map = visualize_terrain_grid_on_map(current_lat, current_lon, terrain_data, first_candidate)

    # Save map to HTML
    html_file = "terrain_grid_with_line_map.html"
    terrain_map.save(html_file)
    print(f"Terrain grid map saved as '{html_file}'.")

    # Automatically open the map in a web browser
    webbrowser.open(html_file, new=2)  # 'new=2' opens in a new tab or window

