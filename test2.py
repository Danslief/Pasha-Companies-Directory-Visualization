import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import geoplot as gplt
import geopy
import re
from geopy.geocoders import Nominatim
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Read data from the file
data = pd.read_csv('pasha_companies_directory.csv')  # Replace with the actual file name

# Function to extract city names from the location column
def extract_city(location):
    if isinstance(location, str):  # Check if location is a string
        parts = location.split(',')
        if len(parts) >= 2:
            city = parts[-3].strip()  # Adjusted index to extract city name
            return city
    return None  # Return None for non-string or invalid locations

# Apply the function to extract city names and create a new column
data['city'] = data['location'].apply(extract_city)

# Drop rows with missing city values
data.dropna(subset=['city'], inplace=True)
data['city'] = data['city'].apply(lambda x: re.sub(r'[\d\s\W]+', '', x))
# Preprocess city names to remove single quotation marks
data['city'] = data['city'].str.replace("'", "")

# Create a dashboard using Tkinter
root = tk.Tk()
root.title("Company Directory Dashboard")

# Frame to display the visualizations
visualization_frame = tk.Frame(root)
visualization_frame.pack()

# Function to display bar chart of companies by city
def display_city_bar_chart():
    # Count the number of companies in each city
    city_counts = data['city'].value_counts()

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    bar_chart = city_counts.plot(kind='bar')
    plt.title('Number of Companies in Different Cities')
    plt.xlabel('City')
    plt.ylabel('Number of Companies')
    plt.yticks(range(0, max(city_counts)+1, 50))  # Set y-axis ticks with increments of 50
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.tight_layout()

    # Embed the bar chart into the visualization frame
    canvas = FigureCanvasTkAgg(bar_chart.figure, master=visualization_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Function to geocode city names to get latitude and longitude coordinates
def geocode_city(city_name):
    try:
        geolocator = Nominatim(user_agent="company_dashboard", timeout=10)  # Increase timeout to 10 seconds
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except (geopy.exc.GeocoderTimedOut, geopy.exc.GeocoderUnavailable):
        # Handle timeout or service unavailable errors
        print(f"Geocoding service timed out or unavailable for city: {city_name}")
        return None, None

# Add latitude and longitude columns to DataFrame
data['latitude'], data['longitude'] = zip(*data['city'].apply(geocode_city))
print(data[['city', 'latitude', 'longitude']])
# Display bar chart
display_city_bar_chart()

# Function to display a map with cities marked
def display_city_map():
    print("Displaying city map...")  # Debug information
    # Load world map
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Convert DataFrame to GeoDataFrame
    gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.longitude, data.latitude))

    # Plot cities on map
    ax = gplt.pointplot(gdf, ax=gplt.polyplot(world, figsize=(10, 6)), color='red', edgecolor='black')
    ax.set_title('Cities with Companies')

    plt.show()

# Button to display city map
city_map_button = tk.Button(root, text="Display City Map", command=display_city_map)
city_map_button.pack()

root.mainloop()
